from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
import heapq
import os
import random
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

from models import (
    Customer,
    Restaurant,
    Rider,
    Order,
    OrderStatus,
    RiderStatus,
    PaymentMethod,
    RefundStatus,
    PaymentRecord,
    RefundRecord,
)

from registry import (
    OrderRegistry,
    RiderRegistry,
    RestaurantRegistry,
)

from order_queue import (
    RestaurantOrderQueue,
    UrgentOrderQueue,
)

from simulation import (
    build_sample_graph,
    build_sample_riders,
    build_sample_orders,
)


app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("SECRET_KEY", "quickbite-secure-session-key-2026-auth")
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_COOKIE_NAME"] = "quickbite_session"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.permanent_session_lifetime = timedelta(days=30)


@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory(os.path.join(app.root_path, "static"), filename)

# ============================================================
# CONFIGURATION & GLOBAL CONTEXT
# ============================================================

WHATSAPP_NUMBER = os.environ.get("WHATSAPP_NUMBER", "919876543210")

# ============================================================
# USER & AUTHENTICATION STORAGE
# ============================================================

USERS = {
    "rahul@quickbite.com": {
        "id": "USER001",
        "name": "Rahul Sharma",
        "email": "rahul@quickbite.com",
        "phone": "+91 98765 43210",
        "password_hash": generate_password_hash("password123"),
        "dob": "1998-05-14",
        "avatar": "👨‍💼",
        "address": "Flat 402, Sea View Apartments, Shivaji Park, Dadar West",
        "city": "Dadar",
        "pincode": "400028",
        "created_at": "2026-01-15"
    }
}


def get_current_user():
    """Return the currently logged in user dictionary or None."""
    user_email = session.get("user_email")
    if user_email and user_email in USERS:
        return USERS[user_email]
    return None


def login_required(f):
    """Decorator to require login for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not get_current_user():
            return redirect(url_for("login_page", next=request.path))
        return f(*args, **kwargs)
    return decorated_function


@app.context_processor
def inject_global_vars():
    """Inject global context variables into all Jinja templates."""
    return {
        "whatsapp_number": WHATSAPP_NUMBER,
        "current_year": datetime.now().year,
        "current_user": get_current_user(),
    }


# ============================================================
# IN-MEMORY DATA STORAGE
# ============================================================

WEB_ORDERS = {}
WEB_REFUNDS = {}
SUPPORT_TICKETS = {}
WEB_ORDER_COUNTER = 1
TICKET_COUNTER = 1001

# Sequence of 7 progressive order stages
ORDER_LIFECYCLE_STAGES = [
    "placed",
    "confirmed",
    "preparing",
    "rider_assigned",
    "picked_up",
    "on_the_way",
    "delivered",
]


# ============================================================
# SAMPLE RESTAURANTS
# ============================================================

def create_restaurants():
    return [
        Restaurant(
            id="REST001",
            name="Spice Kitchen",
            location="Bandra",
        ),
        Restaurant(
            id="REST002",
            name="Burger House",
            location="Andheri",
        ),
        Restaurant(
            id="REST003",
            name="Pizza Point",
            location="Kurla",
        ),
    ]


# ============================================================
# SAMPLE CUSTOMERS
# ============================================================

def create_customers():
    return [
        Customer(
            id="C001",
            name="Devan",
            location="Dadar",
        ),
        Customer(
            id="C002",
            name="Rahul",
            location="Powai",
        ),
        Customer(
            id="C003",
            name="Sneha",
            location="Goregaon",
        ),
        Customer(
            id="C004",
            name="Aditya",
            location="Thane",
        ),
    ]


# ============================================================
# DIJKSTRA HELPER
# ============================================================

def _shortest_path(graph, start, end):
    """
    Return (path, distance) using the LocationGraph's Dijkstra implementation.
    """
    if start == end:
        return [start], 0.0

    result = graph.dijkstra_shortest_weighted(start, end)
    if result is None:
        return None

    path, distance = result
    return path, float(distance)


# ============================================================
# MIN-HEAP RIDER SELECTION
# ============================================================

def _select_best_rider_heap(idle_riders, restaurant_location, graph):
    """
    Select the closest reachable idle rider using a Min-Heap.
    Heap key: distance from rider -> restaurant calculated by Dijkstra.
    """
    heap = []

    for rider in idle_riders:
        result = _shortest_path(graph, rider.current_location, restaurant_location)
        if result is None:
            continue

        _, distance = result
        heapq.heappush(heap, (distance, rider.id, rider))

    if not heap:
        return None

    return heapq.heappop(heap)[2]


# ============================================================
# ASSIGN RIDER + CALCULATE COMPLETE ROUTE
# ============================================================

def _assign_rider_to_order(order, rider, graph):
    """
    Calculate Rider -> Restaurant -> Customer using Dijkstra for both legs.
    """
    rider_to_restaurant = _shortest_path(
        graph,
        rider.current_location,
        order.restaurant.location,
    )

    restaurant_to_customer = _shortest_path(
        graph,
        order.restaurant.location,
        order.customer.location,
    )

    if rider_to_restaurant is None:
        raise ValueError(
            f"No route from rider location '{rider.current_location}' to restaurant '{order.restaurant.location}'."
        )

    if restaurant_to_customer is None:
        raise ValueError(
            f"No route from restaurant '{order.restaurant.location}' to customer '{order.customer.location}'."
        )

    rider_path, rider_distance = rider_to_restaurant
    customer_path, customer_distance = restaurant_to_customer

    # Join routes without duplicating the restaurant node
    full_route = rider_path + customer_path[1:]

    order.assigned_rider = rider
    order.route = full_route
    order.eta_minutes = rider_distance + customer_distance
    order.status = OrderStatus.RIDER_ASSIGNED
    rider.status = RiderStatus.BUSY

    return order


# ============================================================
# SEED INITIAL DEMO ORDERS
# ============================================================

def _seed_demo_orders():
    """Seed initial representative orders with varied statuses and payment methods."""
    global WEB_ORDERS, WEB_REFUNDS

    if WEB_ORDERS:
        return

    # Seed 1: Active Delivered Order
    WEB_ORDERS["O001"] = {
        "order_id": "O001",
        "customer": "Rahul Sharma",
        "customer_email": "rahul@quickbite.com",
        "customer_location": "Powai",
        "address": "Flat 302, Lake View, Powai",
        "restaurant": "Burger House",
        "restaurant_location": "Andheri",
        "rider": "Aarav",
        "rider_id": "R001",
        "route": ["Andheri", "Bandra", "BKC", "Kurla", "Ghatkopar", "Powai"],
        "eta": 42.0,
        "status": "delivered",
        "total": 358.0,
        "payment_method": "cod",
        "payment_details": "Cash on Delivery",
        "cart": [
            {"id": "food002", "name": "Classic Cheeseburger", "price": 179, "quantity": 2}
        ],
        "created_at": "2026-08-22 17:30"
    }

    # Seed 2: Active Preparing Order (Prepaid UPI)
    WEB_ORDERS["O002"] = {
        "order_id": "O002",
        "customer": "Rahul Sharma",
        "customer_email": "rahul@quickbite.com",
        "customer_location": "Dadar",
        "address": "Flat 402, Sea View Apartments, Shivaji Park, Dadar West",
        "restaurant": "Spice Kitchen",
        "restaurant_location": "Bandra",
        "rider": "Vikram",
        "rider_id": "R002",
        "route": ["Bandra", "Dadar"],
        "eta": 15.0,
        "status": "preparing",
        "total": 555.0,
        "payment_method": "upi",
        "payment_details": "UPI ID: rahul@okhdfcbank",
        "cart": [
            {"id": "food001", "name": "Chicken Biryani", "price": 249, "quantity": 2},
            {"id": "food005", "name": "Garlic Naan", "price": 79, "quantity": 1}
        ],
        "created_at": "2026-08-22 18:10"
    }

    # Seed 3: Cancelled Order with Refund (Prepaid Card)
    WEB_ORDERS["O003"] = {
        "order_id": "O003",
        "customer": "Rahul Sharma",
        "customer_email": "rahul@quickbite.com",
        "customer_location": "Dadar",
        "address": "Flat 402, Sea View Apartments, Shivaji Park, Dadar West",
        "restaurant": "Pizza Point",
        "restaurant_location": "Kurla",
        "rider": "Rohan",
        "rider_id": "R003",
        "route": ["Kurla", "BKC", "Dadar"],
        "eta": 22.0,
        "status": "cancelled",
        "cancellation_reason": "Placed order by mistake",
        "total": 489.0,
        "payment_method": "card",
        "payment_details": "Card: ending in 4242 (Rahul Sharma)",
        "cart": [
            {"id": "food003", "name": "Paneer Tikka", "price": 229, "quantity": 2}
        ],
        "created_at": "2026-08-22 16:45"
    }

    WEB_REFUNDS["O003"] = {
        "refund_id": "REF-84291",
        "order_id": "O003",
        "amount": 489.0,
        "method": "card",
        "status": "completed",
        "reason": "Placed order by mistake",
        "account_destination": "Visa Card ending in 4242",
        "created_at": "2026-08-22 16:50",
        "updated_at": "2026-08-22 16:52"
    }


_seed_demo_orders()


# ============================================================
# DASHBOARD SIMULATION
# ============================================================

def run_dashboard_simulation():
    """Run the complete data-structure dispatch pipeline for the homepage dashboard."""
    graph = build_sample_graph()
    order_registry = OrderRegistry()
    rider_registry = RiderRegistry()
    restaurant_registry = RestaurantRegistry()

    restaurants = create_restaurants()
    for restaurant in restaurants:
        restaurant_registry.add(restaurant.id, restaurant)

    customers = create_customers()
    riders = build_sample_riders()
    for rider in riders:
        rider_registry.add(rider.id, rider)

    orders = build_sample_orders(restaurants, customers)
    for order in orders:
        order_registry.add(order.id, order)

    restaurant_queues = {r.id: RestaurantOrderQueue() for r in restaurants}
    urgent_queue = UrgentOrderQueue()

    for order in orders:
        order.status = OrderStatus.QUEUED
        if order.is_urgent:
            urgent_queue.push(order, priority=1)
        else:
            restaurant_queues[order.restaurant.id].enqueue(order)

    processing_order = []
    urgent_order = urgent_queue.pop()
    if urgent_order is not None:
        processing_order.append(urgent_order)

    for restaurant in restaurants:
        queue = restaurant_queues[restaurant.id]
        while len(queue) > 0:
            item = queue.dequeue()
            if item is not None:
                processing_order.append(item)

    delivered_count = 0
    failed_count = 0
    total_eta = 0.0
    results = []

    for order in processing_order:
        order.status = OrderStatus.PREPARING
        order.status = OrderStatus.AWAITING_RIDER
        idle_riders = rider_registry.idle_riders()

        rider = _select_best_rider_heap(idle_riders, order.restaurant.location, graph)

        if rider is None:
            order.status = OrderStatus.FAILED
            failed_count += 1
            results.append({
                "id": order.id,
                "customer": order.customer.name,
                "restaurant": order.restaurant.name,
                "rider": None,
                "rider_id": None,
                "urgent": order.is_urgent,
                "route": [],
                "eta": 0.0,
                "status": "failed",
            })
            continue

        try:
            _assign_rider_to_order(order, rider, graph)
        except (ValueError, KeyError) as error:
            order.status = OrderStatus.FAILED
            failed_count += 1
            results.append({
                "id": order.id,
                "customer": order.customer.name,
                "restaurant": order.restaurant.name,
                "rider": rider.name,
                "rider_id": rider.id,
                "urgent": order.is_urgent,
                "route": [],
                "eta": 0.0,
                "status": f"failed: {error}",
            })
            continue

        eta = order.eta_minutes or 0.0
        route = order.route.copy()
        rider_name = rider.name
        rider_id = rider.id

        # Mark simulated order delivered
        order.status = OrderStatus.DELIVERED
        rider.status = RiderStatus.IDLE
        if order.customer.location:
            rider.current_location = order.customer.location

        delivered_count += 1
        total_eta += eta

        results.append({
            "id": order.id,
            "customer": order.customer.name,
            "restaurant": order.restaurant.name,
            "rider": rider_name,
            "rider_id": rider_id,
            "urgent": order.is_urgent,
            "route": route,
            "eta": eta,
            "status": order.status.value,
        })

    average_eta = total_eta / delivered_count if delivered_count > 0 else 0.0

    rider_data = []
    for rider in rider_registry.all():
        rider_data.append({
            "id": rider.id,
            "name": rider.name,
            "location": rider.current_location,
            "status": rider.status.value,
        })

    return {
        "locations": len(graph._adj),
        "orders": len(orders),
        "delivered": delivered_count,
        "failed": failed_count,
        "average_eta": average_eta,
        "riders": rider_data,
        "results": results,
        "restaurants": restaurants,
        "customers": customers,
    }


# ============================================================
# ROUTES: AUTHENTICATION & PROFILE
# ============================================================

@app.route("/login")
def login_page():
    if get_current_user():
        next_url = request.args.get("next") or url_for("profile_page")
        return redirect(next_url)
    return render_template("login.html")


@app.route("/api/login", methods=["POST"])
def login_api():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    next_url = data.get("next") or url_for("profile_page")
    if next_url == "/":
        next_url = url_for("profile_page")

    if not email or not password:
        return jsonify({"success": False, "message": "Please provide email and password."}), 400

    user = USERS.get(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"success": False, "message": "Invalid email or password."}), 401

    session.permanent = True
    session["user_email"] = email
    return jsonify({
        "success": True,
        "message": "Login successful! Welcome back.",
        "redirect": next_url,
        "user": {
            "name": user["name"],
            "email": user["email"],
            "avatar": user["avatar"]
        }
    })


@app.route("/api/signup", methods=["POST"])
def signup_api():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    phone = data.get("phone", "").strip()
    location = data.get("location", "Dadar")
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"success": False, "message": "Name, email, and password are required."}), 400

    if email in USERS:
        return jsonify({"success": False, "message": "An account with this email already exists. Please Sign In."}), 400

    new_user = {
        "id": f"USER{len(USERS)+1:03d}",
        "name": name,
        "email": email,
        "phone": phone,
        "password_hash": generate_password_hash(password),
        "dob": "2000-01-01",
        "avatar": "🧑‍🍳",
        "address": f"Apartment 101, {location}",
        "city": location,
        "pincode": "400001",
        "created_at": datetime.now().strftime("%Y-%m-%d")
    }

    USERS[email] = new_user
    # Explicitly do NOT log the user in automatically after signup

    return jsonify({
        "success": True,
        "message": "Account created successfully. Please login."
    })


@app.route("/api/forgot-password", methods=["POST"])
def forgot_password_api():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()

    if not email:
        return jsonify({"success": False, "message": "Please enter your email address."}), 400

    if email in USERS:
        return jsonify({
            "success": True,
            "message": f"Password reset instructions have been sent to {email}. Check your inbox!"
        })
    else:
        return jsonify({
            "success": False,
            "message": "No account found with this email address."
        }), 404


@app.route("/logout")
def logout():
    session.pop("user_email", None)
    return redirect(url_for("dashboard"))


@app.route("/profile")
@login_required
def profile_page():
    user = get_current_user()
    user_orders = [o for o in WEB_ORDERS.values() if o.get("customer_email") == user["email"] or o.get("customer") == user["name"]]
    return render_template("profile.html", user=user, orders_count=len(user_orders) or 3)


@app.route("/api/profile", methods=["POST"])
@login_required
def update_profile_api():
    user = get_current_user()
    data = request.get_json(silent=True) or {}

    user["name"] = data.get("name", user["name"]).strip()
    user["phone"] = data.get("phone", user["phone"]).strip()
    user["dob"] = data.get("dob", user.get("dob", ""))
    user["address"] = data.get("address", user.get("address", "")).strip()
    user["city"] = data.get("city", user.get("city", "Dadar")).strip()
    user["pincode"] = data.get("pincode", user.get("pincode", "")).strip()
    user["avatar"] = data.get("avatar", user.get("avatar", "👨‍💼"))

    return jsonify({
        "success": True,
        "message": "Profile updated successfully!",
        "user": user
    })


# ============================================================
# ROUTES: HOME & CORE PAGES
# ============================================================

@app.route("/")
def dashboard():
    data = run_dashboard_simulation()
    return render_template("index.html", data=data)


@app.route("/restaurant/<restaurant_id>")
def restaurant_page(restaurant_id):
    restaurants = create_restaurants()
    restaurant = next((r for r in restaurants if r.id == restaurant_id), None)
    if restaurant is None:
        return "Restaurant not found", 404
    return render_template("restaurant.html", restaurant=restaurant)


@app.route("/cart")
def cart():
    return render_template("cart.html")


@app.route("/checkout")
def checkout():
    return render_template("checkout.html")


@app.route("/payment")
def payment():
    return render_template("payment.html")


# ============================================================
# ROUTES: ORDERS & TRACKING (PROTECTED)
# ============================================================

@app.route("/orders")
@login_required
def orders_page():
    user = get_current_user()
    # Filter orders by user or show all web orders if admin/demo
    orders = list(reversed(list(WEB_ORDERS.values())))
    return render_template("orders.html", orders=orders)


@app.route("/track/<order_id>")
def track_order(order_id):
    order = WEB_ORDERS.get(order_id)
    if order is None:
        # Search dashboard simulation results
        data = run_dashboard_simulation()
        result = next((item for item in data["results"] if item["id"] == order_id), None)
        if result is not None:
            order = {
                "order_id": result["id"],
                "customer": result["customer"],
                "restaurant": result["restaurant"],
                "restaurant_location": "Bandra",
                "customer_location": "Dadar",
                "rider": result["rider"],
                "rider_id": result["rider_id"],
                "route": result["route"],
                "eta": result["eta"],
                "status": result["status"],
                "total": 249,
                "payment_method": "upi",
                "payment_details": "UPI ID: guest@okhdfcbank"
            }

    if order is None:
        return render_template("tracking.html", order=None), 404

    return render_template("tracking.html", order=order)


@app.route("/api/track/<order_id>")
def track_order_api(order_id):
    order = WEB_ORDERS.get(order_id)
    if order is None:
        data = run_dashboard_simulation()
        result = next((item for item in data["results"] if item["id"] == order_id), None)
        if result is None:
            return jsonify({"success": False, "message": "Order not found."}), 404
        return jsonify({
            "success": True,
            "order_id": result["id"],
            "customer": result["customer"],
            "restaurant": result["restaurant"],
            "rider": result["rider"],
            "rider_id": result["rider_id"],
            "route": result["route"],
            "eta": result["eta"],
            "status": result["status"],
            "total": 249,
            "payment_method": "upi"
        })

    return jsonify({
        "success": True,
        "order_id": order["order_id"],
        "customer": order.get("customer", "Guest Customer"),
        "customer_location": order.get("customer_location", "Dadar"),
        "address": order.get("address", ""),
        "restaurant": order.get("restaurant", "Spice Kitchen"),
        "restaurant_location": order.get("restaurant_location", "Bandra"),
        "rider": order.get("rider", "Available Rider"),
        "rider_id": order.get("rider_id", "R001"),
        "route": order.get("route", []),
        "eta": order.get("eta", 25.0),
        "status": order.get("status", "placed"),
        "total": order.get("total", 0),
        "payment_method": order.get("payment_method", "upi"),
        "payment_details": order.get("payment_details", ""),
        "cart": order.get("cart", [])
    })


# ============================================================
# API: PROCESS PAYMENT & PLACE ORDER (DIJKSTRA + MIN-HEAP)
# ============================================================

@app.route("/api/process-payment", methods=["POST"])
@app.route("/api/place-order", methods=["POST"])
def process_payment():
    global WEB_ORDER_COUNTER

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "message": "No payment or order data received."}), 400

    user = get_current_user()

    cart_items = data.get("cart", [])
    customer_name = data.get("customer_name") or (user["name"] if user else "Guest Customer")
    customer_email = user["email"] if user else "guest@quickbite.com"
    customer_location = data.get("customer_location") or (user["city"] if user else "Dadar")
    restaurant_id = data.get("restaurant_id", "REST001")
    address = data.get("address") or (user["address"] if user else "Mumbai")
    payment_method = data.get("payment_method", "upi").lower()
    payment_details = data.get("payment_details", "")
    phone = data.get("phone") or (user["phone"] if user else "")
    notes = data.get("notes", "")

    if not cart_items:
        return jsonify({"success": False, "message": "Cart is empty."}), 400

    # Build Graph & Dijkstra
    graph = build_sample_graph()

    restaurants = create_restaurants()
    restaurant = next((r for r in restaurants if r.id == restaurant_id), restaurants[0])

    customer = Customer(
        id=f"CUST-{WEB_ORDER_COUNTER:03d}",
        name=customer_name,
        location=customer_location,
    )

    order_id = f"WEB{WEB_ORDER_COUNTER:03d}"
    WEB_ORDER_COUNTER += 1

    order = Order(
        id=order_id,
        customer=customer,
        restaurant=restaurant,
        is_urgent=False,
    )
    order.status = OrderStatus.QUEUED

    # FIFO queue insertion
    queue = RestaurantOrderQueue()
    queue.enqueue(order)
    order = queue.dequeue()
    order.status = OrderStatus.CONFIRMED

    # Min-Heap Rider Selection
    riders = build_sample_riders()
    idle_riders = [r for r in riders if r.status in [RiderStatus.IDLE, "idle"]]

    rider = _select_best_rider_heap(idle_riders, restaurant.location, graph)
    if rider is None:
        order.status = OrderStatus.FAILED
        return jsonify({"success": False, "message": "No reachable rider available."}), 503

    # Calculate Dijkstra route
    try:
        _assign_rider_to_order(order, rider, graph)
    except (ValueError, KeyError) as error:
        order.status = OrderStatus.FAILED
        return jsonify({"success": False, "message": str(error)}), 500

    route = order.route.copy()
    eta = order.eta_minutes or 25.0
    rider_name = rider.name
    rider_id = rider.id

    # Calculate total bill
    subtotal = 0.0
    for item in cart_items:
        try:
            price = float(item.get("price", 0))
            quantity = int(item.get("quantity", 1))
            subtotal += price * quantity
        except (TypeError, ValueError):
            pass

    total = subtotal + 5.0 + 2.0  # + delivery fee + platform fee

    # Create Payment Record
    payment_id = f"PAY-{payment_method.upper()}-{random.randint(10000, 99999)}"
    payment_record = PaymentRecord(
        payment_id=payment_id,
        method=payment_method,
        amount=total,
        status="pending_cod" if payment_method == "cod" else "completed",
        details=payment_details,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M")
    )

    # Initial order status: placed/confirmed/rider_assigned
    order.status = OrderStatus.RIDER_ASSIGNED
    status = order.status.value

    WEB_ORDERS[order_id] = {
        "order_id": order_id,
        "customer": customer.name,
        "customer_email": customer_email,
        "customer_location": customer.location,
        "address": address,
        "phone": phone,
        "notes": notes,
        "restaurant": restaurant.name,
        "restaurant_location": restaurant.location,
        "rider": rider_name,
        "rider_id": rider_id,
        "route": route,
        "eta": eta,
        "status": status,
        "total": total,
        "cart": cart_items,
        "payment_method": payment_method,
        "payment_id": payment_id,
        "payment_details": payment_details,
        "payment_status": payment_record.status,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    return jsonify({
        "success": True,
        "order_id": order_id,
        "customer": customer.name,
        "restaurant": restaurant.name,
        "rider": rider_name,
        "rider_id": rider_id,
        "route": route,
        "eta": eta,
        "status": status,
        "payment_id": payment_id,
        "payment_method": payment_method,
        "total": total,
        "message": "Order dispatched successfully via Dijkstra & Min-Heap!",
        "tracking_url": f"/track/{order_id}",
    })


# ============================================================
# API: ORDER STATUS ADVANCEMENT SIMULATOR
# ============================================================

@app.route("/api/order-status/advance/<order_id>", methods=["POST"])
def advance_order_status(order_id):
    order = WEB_ORDERS.get(order_id)
    if not order:
        return jsonify({"success": False, "message": "Order not found."}), 404

    current_status = order.get("status", "placed").lower()

    if current_status == "cancelled":
        return jsonify({"success": False, "message": "Cancelled orders cannot be advanced."}), 400

    if current_status not in ORDER_LIFECYCLE_STAGES:
        next_status = "confirmed"
    else:
        idx = ORDER_LIFECYCLE_STAGES.index(current_status)
        if idx < len(ORDER_LIFECYCLE_STAGES) - 1:
            next_status = ORDER_LIFECYCLE_STAGES[idx + 1]
        else:
            return jsonify({"success": True, "message": "Order is already delivered.", "status": "delivered"})

    order["status"] = next_status
    return jsonify({
        "success": True,
        "order_id": order_id,
        "previous_status": current_status,
        "status": next_status,
        "message": f"Status updated to {next_status.replace('_', ' ').title()}"
    })


# ============================================================
# API: ORDER CANCELLATION & REFUND TRIGGER
# ============================================================

@app.route("/api/cancel-order", methods=["POST"])
def cancel_order_api():
    data = request.get_json(silent=True) or {}
    order_id = data.get("order_id")
    reason = data.get("reason", "Customer requested cancellation")

    if not order_id or order_id not in WEB_ORDERS:
        return jsonify({"success": False, "message": f"Order {order_id} not found."}), 404

    order = WEB_ORDERS[order_id]
    current_status = order.get("status", "").lower()

    # Check cancellation rule: allowed before picked_up / on_the_way / delivered
    if current_status in ["picked_up", "on_the_way", "out_for_delivery", "delivered"]:
        return jsonify({
            "success": False,
            "message": f"Order cannot be cancelled online as it is already '{current_status.replace('_', ' ')}'. Please contact support."
        }), 400

    if current_status == "cancelled":
        return jsonify({"success": True, "message": "Order is already cancelled."})

    order["status"] = "cancelled"
    order["cancellation_reason"] = reason
    order["cancelled_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    # If prepaid (UPI or Card), initiate automated refund record
    payment_method = order.get("payment_method", "upi").lower()
    refund_record = None

    if payment_method in ["upi", "card", "qr"]:
        refund_id = f"REF-{random.randint(10000, 99999)}"
        dest = order.get("payment_details", "Original payment source")
        refund_record = {
            "refund_id": refund_id,
            "order_id": order_id,
            "amount": order.get("total", 0.0),
            "method": payment_method,
            "status": "completed",
            "reason": reason,
            "account_destination": dest,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        WEB_REFUNDS[order_id] = refund_record

    return jsonify({
        "success": True,
        "order_id": order_id,
        "status": "cancelled",
        "message": f"Order {order_id} has been cancelled successfully.",
        "refund": refund_record,
        "refund_url": f"/refund-status/{order_id}" if refund_record else None
    })


# ============================================================
# ROUTES: REFUND STATUS
# ============================================================

@app.route("/refund-status/<order_id>")
def refund_status_page(order_id):
    order = WEB_ORDERS.get(order_id)
    refund = WEB_REFUNDS.get(order_id)

    if order is None and refund is not None:
        order = {
            "order_id": order_id,
            "total": refund["amount"],
            "payment_method": refund["method"],
            "cancellation_reason": refund["reason"],
            "status": "cancelled"
        }

    return render_template("refund_status.html", order=order, refund=refund)


@app.route("/refunds")
def refunds_overview_page():
    return render_template("refund_status.html", order=None, refund=None)


@app.route("/api/refund-status/<order_id>")
def refund_status_api(order_id):
    refund = WEB_REFUNDS.get(order_id)
    order = WEB_ORDERS.get(order_id)

    if not refund and not order:
        return jsonify({"success": False, "message": "No refund record found for this order."}), 404

    if not refund and order:
        if order.get("payment_method") == "cod":
            return jsonify({
                "success": True,
                "order_id": order_id,
                "status": "not_applicable",
                "message": "Cash on Delivery order — no payment refund required."
            })

    return jsonify({
        "success": True,
        "order_id": order_id,
        "refund": refund
    })


# ============================================================
# ROUTES: FAQ, HELP, CONTACT, POLICIES
# ============================================================

@app.route("/faq")
def faq_page():
    return render_template("faq.html")


@app.route("/help")
def help_page():
    return render_template("help.html")


@app.route("/api/support-ticket", methods=["POST"])
def support_ticket_api():
    global TICKET_COUNTER
    data = request.get_json(silent=True) or {}

    category = data.get("category", "General Inquiry")
    order_id = data.get("order_id", "")
    customer_name = data.get("customer_name", "Guest")
    contact = data.get("contact", "")
    description = data.get("description", "")

    ticket_id = f"TKT-{TICKET_COUNTER}"
    TICKET_COUNTER += 1

    SUPPORT_TICKETS[ticket_id] = {
        "ticket_id": ticket_id,
        "category": category,
        "order_id": order_id,
        "customer_name": customer_name,
        "contact": contact,
        "description": description,
        "status": "open",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    return jsonify({
        "success": True,
        "ticket_id": ticket_id,
        "message": f"Support ticket {ticket_id} created successfully."
    })


@app.route("/contact")
def contact_page():
    return render_template("contact.html")


@app.route("/api/contact", methods=["POST"])
def contact_api():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "")
    email = data.get("email", "")
    subject = data.get("subject", "")
    message = data.get("message", "")

    return jsonify({
        "success": True,
        "message": f"Thank you {name}! Your message regarding '{subject}' has been received."
    })


@app.route("/privacy")
def privacy_page():
    return render_template("privacy.html")


@app.route("/terms")
def terms_page():
    return render_template("terms.html")


@app.route("/refund-policy")
def refund_policy_page():
    return render_template("refund_policy.html")


# ============================================================
# API: SYSTEM HEALTH & REGISTRIES
# ============================================================

@app.route("/health")
def health():
    return jsonify({
        "status": "online",
        "server": "Flask",
        "backend": "QuickBite Food Delivery Dispatch",
        "algorithms": {
            "routing": "Dijkstra Shortest Path",
            "rider_selection": "Min-Heap Priority Queue",
            "order_queuing": "FIFO Queue"
        },
        "auth_system": "Active",
        "whatsapp_integration": "Enabled",
        "whatsapp_number": WHATSAPP_NUMBER
    })


@app.route("/api/simulation")
def simulation_api():
    data = run_dashboard_simulation()
    return jsonify({
        "status": "success",
        "backend": "Flask",
        "locations": data["locations"],
        "orders": data["orders"],
        "delivered": data["delivered"],
        "failed": data["failed"],
        "average_eta": data["average_eta"],
    })


@app.route("/api/riders")
def riders_api():
    data = run_dashboard_simulation()
    return jsonify({
        "status": "success",
        "backend": "Flask",
        "riders": data["riders"],
    })


@app.route("/api/orders")
def web_orders_api():
    return jsonify({
        "success": True,
        "orders": list(WEB_ORDERS.values()),
    })


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )