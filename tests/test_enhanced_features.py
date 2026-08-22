import unittest
import json
from app import app, WEB_ORDERS, WEB_REFUNDS, ORDER_LIFECYCLE_STAGES
from models import OrderStatus, RiderStatus


class TestEnhancedQuickBiteFeatures(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True
        with self.client.session_transaction() as sess:
            sess["user_email"] = "rahul@quickbite.com"

    def test_all_web_pages_load_successfully(self):
        """Verify all separate pages and routes render with HTTP 200."""
        # Test unauthenticated public pages
        public_client = app.test_client()
        unauth_routes = [
            "/",
            "/login",
            "/restaurant/REST001",
            "/cart",
            "/checkout",
            "/payment",
            "/track/O001",
            "/refund-status/O003",
            "/refunds",
            "/faq",
            "/help",
            "/contact",
            "/privacy",
            "/terms",
            "/refund-policy",
            "/health"
        ]
        for route in unauth_routes:
            response = public_client.get(route)
            self.assertEqual(
                response.status_code,
                200,
                f"Expected route '{route}' to return status 200, got {response.status_code}"
            )

        # Test authenticated routes
        auth_routes = ["/profile", "/orders"]
        for route in auth_routes:
            response = self.client.get(route)
            self.assertEqual(
                response.status_code,
                200,
                f"Expected route '{route}' to return status 200, got {response.status_code}"
            )

    def test_payment_and_order_dispatch_api(self):
        """Test placing an order with UPI payment and Dijkstra/Min-Heap dispatch."""
        payload = {
            "customer_name": "Test Customer",
            "customer_location": "Dadar",
            "address": "123 Test Street",
            "restaurant_id": "REST001",
            "payment_method": "upi",
            "payment_details": "UPI ID: test@okhdfcbank",
            "cart": [
                {"id": "food001", "name": "Chicken Biryani", "price": 249, "quantity": 1}
            ]
        }
        response = self.client.post(
            "/api/process-payment",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get("success"))
        self.assertIn("WEB", data.get("order_id", ""))
        self.assertIsNotNone(data.get("rider"))
        self.assertTrue(len(data.get("route", [])) >= 2)
        self.assertGreater(data.get("eta", 0), 0)

        # Check in memory storage
        order_id = data["order_id"]
        self.assertIn(order_id, WEB_ORDERS)
        self.assertEqual(WEB_ORDERS[order_id]["customer"], "Test Customer")
        self.assertEqual(WEB_ORDERS[order_id]["payment_method"], "upi")

    def test_order_status_progression(self):
        """Test order advancing step-by-step through the 7 lifecycle states."""
        # Create a test order
        order_id = "TEST_ORDER_001"
        WEB_ORDERS[order_id] = {
            "order_id": order_id,
            "status": "placed",
            "customer": "Progression Test",
            "total": 249.0,
            "payment_method": "card"
        }

        # Sequence of stages
        expected_sequence = [
            "confirmed",
            "preparing",
            "rider_assigned",
            "picked_up",
            "on_the_way",
            "delivered"
        ]

        for expected_status in expected_sequence:
            res = self.client.post(f"/api/order-status/advance/{order_id}")
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertTrue(data.get("success"))
            self.assertEqual(data.get("status"), expected_status)
            self.assertEqual(WEB_ORDERS[order_id]["status"], expected_status)

    def test_cancellation_and_refund_generation_prepaid(self):
        """Test cancelling a prepaid order triggers cancellation and refund creation."""
        order_id = "TEST_CANCEL_PREPAID"
        WEB_ORDERS[order_id] = {
            "order_id": order_id,
            "status": "preparing",
            "customer": "Cancel Prepaid User",
            "total": 550.0,
            "payment_method": "upi",
            "payment_details": "UPI ID: user@okhdfcbank"
        }

        cancel_payload = {
            "order_id": order_id,
            "reason": "Estimated delivery time is too long"
        }
        res = self.client.post(
            "/api/cancel-order",
            data=json.dumps(cancel_payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("status"), "cancelled")
        self.assertIsNotNone(data.get("refund"))
        self.assertEqual(data["refund"]["amount"], 550.0)
        self.assertIn(order_id, WEB_REFUNDS)

    def test_cancellation_restricted_when_out_for_delivery(self):
        """Test that orders already out for delivery / delivered cannot be cancelled online."""
        order_id = "TEST_CANCEL_RESTRICTED"
        WEB_ORDERS[order_id] = {
            "order_id": order_id,
            "status": "on_the_way",
            "customer": "Late Cancel User",
            "total": 300.0,
            "payment_method": "cod"
        }

        cancel_payload = {
            "order_id": order_id,
            "reason": "Changed mind"
        }
        res = self.client.post(
            "/api/cancel-order",
            data=json.dumps(cancel_payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertFalse(data.get("success"))
        self.assertIn("cannot be cancelled", data.get("message", "").lower())

    def test_support_ticket_and_contact_apis(self):
        """Test support ticket creation and contact form submission."""
        ticket_payload = {
            "category": "Delivery Issue",
            "order_id": "O001",
            "customer_name": "John Doe",
            "contact": "9876543210",
            "description": "Rider has arrived at the wrong gate."
        }
        res = self.client.post(
            "/api/support-ticket",
            data=json.dumps(ticket_payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data.get("success"))
        self.assertIn("TKT-", data.get("ticket_id", ""))

        contact_payload = {
            "name": "Jane Corporate",
            "email": "jane@corp.com",
            "subject": "Corporate Catering",
            "message": "Interested in partnering for corporate lunch delivery."
        }
        res2 = self.client.post(
            "/api/contact",
            data=json.dumps(contact_payload),
            content_type="application/json"
        )
        self.assertEqual(res2.status_code, 200)
        data2 = json.loads(res2.data)
        self.assertTrue(data2.get("success"))


if __name__ == "__main__":
    unittest.main()
