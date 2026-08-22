import unittest
import json
from app import app, USERS, get_current_user


class TestAuthProfileSystem(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_login_flow(self):
        """Test login with valid and invalid credentials."""
        # 1. Invalid credentials
        res = self.client.post(
            "/api/login",
            data=json.dumps({"email": "rahul@quickbite.com", "password": "wrongpassword"}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 401)
        data = json.loads(res.data)
        self.assertFalse(data.get("success"))

        # 2. Valid credentials
        res = self.client.post(
            "/api/login",
            data=json.dumps({"email": "rahul@quickbite.com", "password": "password123"}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("user", {}).get("email"), "rahul@quickbite.com")

    def test_signup_flow(self):
        """Test creating a new account."""
        signup_payload = {
            "name": "Ananya Sen",
            "email": "ananya@example.com",
            "phone": "9876500000",
            "location": "Bandra",
            "password": "securepassword123"
        }
        res = self.client.post(
            "/api/signup",
            data=json.dumps(signup_payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data.get("success"))
        self.assertIn("ananya@example.com", USERS)

        # Duplicate signup should fail
        res_dup = self.client.post(
            "/api/signup",
            data=json.dumps(signup_payload),
            content_type="application/json"
        )
        self.assertEqual(res_dup.status_code, 400)

    def test_forgot_password_flow(self):
        """Test forgot password API."""
        res = self.client.post(
            "/api/forgot-password",
            data=json.dumps({"email": "rahul@quickbite.com"}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data.get("success"))

        res_unknown = self.client.post(
            "/api/forgot-password",
            data=json.dumps({"email": "nonexistent@user.com"}),
            content_type="application/json"
        )
        self.assertEqual(res_unknown.status_code, 404)

    def test_protected_routes_require_login(self):
        """Verify that /profile and /orders redirect unauthenticated users to /login."""
        # Unauthenticated access
        res_profile = self.client.get("/profile")
        self.assertEqual(res_profile.status_code, 302)
        self.assertIn("/login", res_profile.headers["Location"])

        res_orders = self.client.get("/orders")
        self.assertEqual(res_orders.status_code, 302)
        self.assertIn("/login", res_orders.headers["Location"])

    def test_profile_view_and_edit_authenticated(self):
        """Test authenticated user viewing and editing their profile."""
        with self.client:
            # Login first
            self.client.post(
                "/api/login",
                data=json.dumps({"email": "rahul@quickbite.com", "password": "password123"}),
                content_type="application/json"
            )

            # View Profile
            res_profile = self.client.get("/profile")
            self.assertEqual(res_profile.status_code, 200)
            self.assertIn(b"Rahul Sharma", res_profile.data)

            # Edit Profile
            update_payload = {
                "name": "Rahul S. Sharma",
                "phone": "+91 99999 88888",
                "dob": "1997-08-20",
                "address": "Penthouse 901, Worli Sea Face",
                "city": "Bandra",
                "pincode": "400050",
                "avatar": "🧑‍💻"
            }
            res_edit = self.client.post(
                "/api/profile",
                data=json.dumps(update_payload),
                content_type="application/json"
            )
            self.assertEqual(res_edit.status_code, 200)
            data = json.loads(res_edit.data)
            self.assertTrue(data.get("success"))
            self.assertEqual(USERS["rahul@quickbite.com"]["name"], "Rahul S. Sharma")
            self.assertEqual(USERS["rahul@quickbite.com"]["city"], "Bandra")
            self.assertEqual(USERS["rahul@quickbite.com"]["avatar"], "🧑‍💻")

            # View My Orders
            res_orders = self.client.get("/orders")
            self.assertEqual(res_orders.status_code, 200)

    def test_full_auth_lifecycle(self):
        """Test Login -> Signup -> Logout -> Login -> Profile -> Edit Details -> My Orders."""
        client = app.test_client()

        # 1. Login as default user
        res = client.post(
            "/api/login",
            data=json.dumps({"email": "rahul@quickbite.com", "password": "password123"}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)

        # 2. Signup new user
        signup_data = {
            "name": "Karan Malhotra",
            "email": "karan@malhotra.com",
            "phone": "9123456789",
            "location": "Andheri",
            "password": "mypassword123"
        }
        res = client.post(
            "/api/signup",
            data=json.dumps(signup_data),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)

        # 3. Logout
        res = client.get("/logout")
        self.assertEqual(res.status_code, 302)

        # 4. Login as newly created user
        res = client.post(
            "/api/login",
            data=json.dumps({"email": "karan@malhotra.com", "password": "mypassword123"}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)

        # 5. Access Profile
        res = client.get("/profile")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Karan Malhotra", res.data)

        # 6. Edit details
        edit_payload = {
            "name": "Karan Malhotra Jr.",
            "phone": "9123456780",
            "dob": "1999-12-31",
            "address": "12, Palm Grove, Andheri West",
            "city": "Andheri",
            "pincode": "400053",
            "avatar": "🍕"
        }
        res = client.post(
            "/api/profile",
            data=json.dumps(edit_payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(USERS["karan@malhotra.com"]["avatar"], "🍕")

        # 7. Access My Orders
        res = client.get("/orders")
        self.assertEqual(res.status_code, 200)


if __name__ == "__main__":
    unittest.main()
