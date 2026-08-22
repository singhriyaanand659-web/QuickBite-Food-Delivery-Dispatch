# 🍕 QuickBite — Food Delivery & Algorithmic Dispatch Engine

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Tests](https://img.shields.io/badge/Unit%20Tests-18%20Passed-brightgreen.svg)]()
[![Algorithms](https://img.shields.io/badge/Algorithms-Dijkstra%20%7C%20Min--Heap%20%7C%20FIFO-orange.svg)]()

> A full-stack web application and Data Structures & Algorithms showcase simulating a real-time food delivery dispatch platform. Powered by **Dijkstra's Shortest Path Routing**, **Min-Heap Rider Allocation**, **FIFO Order Queuing**, and a complete customer-facing eCommerce flow.

---

## 📸 Core Features & Highlights

- **🗺️ Algorithmic Dispatch Engine**: Real-time graph routing over a weighted city network (Dadar, Bandra, Andheri, Kurla, BKC, etc.) using Dijkstra's algorithm.
- **⚡ Min-Heap Nearest Rider Selection**: Efficient priority queue matching for idle riders closest to pickup restaurants.
- **🍕 Restaurant & Menu Experience**: Multi-restaurant catalog with category filtering, add-to-cart, quantity increments, and live total calculations.
- **💳 Multi-Method Payment Gateway**: Demo checkout supporting **Cash on Delivery (COD)**, **UPI (GPay / PhonePe / Paytm / QR)**, and **Credit/Debit Cards**.
- **📍 7-Stage Live Order Tracking**: Dynamic progression from *Placed → Confirmed → Preparing → Rider Assigned → Picked Up → On The Way → Delivered* with full route waypoint visualization and WhatsApp rider messaging.
- **❌ Order Cancellation & 3-Stage Refunds**: Policy-based order cancellation with automated refund tracking (*Refund Initiated → Processing → Completed*) and COD safety handling.
- **👤 Modern Authentication & Profile Management**: Persistent session auth, Sign In / Sign Up with pre-fill login redirection, interactive **12-Avatar Emoji Studio**, and Dijkstra city vertex preferences.
- **❓ Interactive FAQ & Help Center**: Accordion-based categorized knowledgebase, live search, issue ticketing, and contact support forms.

---

## 🧠 Data Structures & Algorithms Architecture

| Component | Data Structure / Algorithm | Time Complexity | Purpose |
| :--- | :--- | :--- | :--- |
| **Entity Registries** | Hash Map (`dict`) | $O(1)$ lookup | Instant retrieval of Orders, Riders, Restaurants, and Users by ID |
| **Restaurant Orders** | FIFO Queue (`collections.deque`) | $O(1)$ push/pop | Order sequence preparation maintaining fair scheduling |
| **Urgent Deliveries** | Priority Queue (`heapq`) | $O(\log N)$ | Expedited queue prioritizing express and VIP orders |
| **Rider Allocation** | Min-Heap Priority Queue | $O(K \log K)$ | Matches the closest idle rider based on shortest Dijkstra distance |
| **Road Network** | Adjacency List Graph | $O(V + E)$ space | Memory-efficient sparse graph representation of urban delivery hubs |
| **Shortest Route** | Dijkstra's Algorithm | $O((V + E) \log V)$ | Calculates optimal delivery path, turns, and accurate ETAs |

---

## 🔄 End-to-End System Workflow

```text
 1. Customer Places Order (Web Interface / Cart)
        ↓
 2. Payment Gateway Verification (COD / UPI / Card)
        ↓
 3. Order Added to Restaurant FIFO Queue
        ↓
 4. Min-Heap Identifies Nearest Idle Rider
        ↓
 5. Dijkstra Computes Shortest Road Network Path (Restaurant → Customer)
        ↓
 6. 7-Stage Live Order Tracking & Dispatch Simulation
        ↓
 7. Delivery Completed → Rider Returns to Idle Heap
```

---

## 📂 Project Structure

```
Food_Delivery_Dispatch_DS_Project_Scaffold/
├── app.py                      # Main Flask application & API routes
├── models.py                   # Data models (Order, Rider, Restaurant, Customer, Refund)
├── graph.py                    # Graph class, Adjacency List, Dijkstra & BFS implementations
├── order_queue.py              # FIFO Restaurant Order Queue & Urgent Priority Queue
├── registry.py                 # In-memory Hash Map registries
├── dispatch.py                 # Core dispatch and assignment logic
├── simulation.py               # Pre-populated city vertices, riders, restaurants & demo dataset
├── requirements.txt            # Python dependencies
├── static/
│   ├── style.css               # Global stylesheets, glassmorphism & responsive design
│   └── ...
├── templates/
│   ├── index.html              # Homepage & interactive dispatch simulation
│   ├── login.html              # Modern split-screen Auth (Login, Sign Up, Forgot Password)
│   ├── profile.html            # Profile dashboard & Avatar Studio
│   ├── restaurant.html         # Restaurant catalog & dish selection
│   ├── cart.html               # Shopping cart & order review
│   ├── checkout.html           # Delivery details & graph node selection
│   ├── payment.html            # Payment gateway simulation (COD, UPI, Card)
│   ├── orders.html             # Order history, cancellation & action hub
│   ├── tracking.html           # 7-stage live tracking & Dijkstra route visualization
│   ├── refund_status.html      # 3-stage refund tracker & timeline
│   ├── faq.html                # FAQ accordion with live search
│   ├── help.html               # Help center & support ticket submitter
│   ├── contact.html            # Contact us form
│   ├── privacy.html            # Privacy policy
│   ├── terms.html              # Terms & conditions
│   └── refund_policy.html      # Cancellation & refund rules policy
└── tests/
    ├── test_core_dispatch.py   # Unit tests for Graph, Dijkstra, Min-Heap & FIFO
    ├── test_enhanced_features.py # Unit tests for web routes, payments & refunds
    └── test_auth_profile.py    # Unit tests for authentication & profile lifecycles
```

---

## 🚀 Getting Started Locally

### 1. Prerequisites
- **Python 3.10+** installed on your system.
- `git` installed.

### 2. Clone the Repository
```bash
git clone https://github.com/singhriyaanand659-web/QuickBite-Food-Delivery-Dispatch.git
cd QuickBite-Food-Delivery-Dispatch
```

### 3. Create & Activate Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
```bash
python app.py
```

Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`** (or **`http://localhost:5000`**)

---

## 🔑 Demo Login Accounts

QuickBite comes with pre-configured accounts for testing:

| Email | Password | Role / Location |
| :--- | :--- | :--- |
| `rahul@quickbite.com` | `password123` | Dadar Hub (Customer) |
| `priya@quickbite.com` | `password123` | Bandra Hub (Customer) |
| `rohit@quickbite.com` | `password123` | Andheri Hub (Customer) |

*(You can also use the **"⚡ 1-Click Demo Login"** buttons directly on the Login page!)*

---

## 🧪 Running Automated Tests

Run the complete test suite (18 unit tests):

```bash
python -m unittest discover tests
```

Expected output:
```
..................
----------------------------------------------------------------------
Ran 18 tests in 1.1s

OK
```

---

## 📄 License
This project is open source and available under the [MIT License](LICENSE).