from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Company, KBEntry, QueryLog


class TeamBoardAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        KBEntry.objects.create(
            question="What is select_related in Django ORM?",
            answer="select_related performs a SQL JOIN.",
            category=KBEntry.Category.DATABASE,
        )
        KBEntry.objects.create(
            question="How does transaction.atomic work?",
            answer="It groups database operations into one transaction.",
            category=KBEntry.Category.DATABASE,
        )
        KBEntry.objects.create(
            question="What is a JWT token?",
            answer="A signed token used for authentication.",
            category=KBEntry.Category.API,
        )

    def register(self, username, email, company_name):
        return self.client.post(
            "/api/auth/register/",
            {
                "username": username,
                "password": "securepass123",
                "company_name": company_name,
                "email": email,
            },
            format="json",
        )

    def token_for(self, user):
        return str(RefreshToken.for_user(user).access_token)

    def test_01_register_creates_company_and_api_key(self):
        response = self.register(
            "acme", "dev@acme.com", "Acme Corp"
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["access"])
        self.assertTrue(response.data["api_key"])
        company = Company.objects.get(user__username="acme")
        self.assertEqual(company.company_name, "Acme Corp")
        self.assertEqual(company.role, Company.Role.CLIENT)

    def test_02_duplicate_register_returns_400(self):
        self.register("acme", "dev@acme.com", "Acme Corp")
        response = self.register("acme", "other@acme.com", "Other Corp")
        self.assertEqual(response.status_code, 400)

    def test_03_login_returns_token_and_credentials(self):
        self.register("acme", "dev@acme.com", "Acme Corp")
        response = self.client.post(
            "/api/auth/login/",
            {"username": "acme", "password": "securepass123"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["access"])
        self.assertEqual(response.data["company_name"], "Acme Corp")
        self.assertTrue(response.data["api_key"])

    def test_04_invalid_login_returns_401(self):
        self.register("acme", "dev@acme.com", "Acme Corp")
        response = self.client.post(
            "/api/auth/login/",
            {"username": "acme", "password": "wrong"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_05_query_without_token_returns_401(self):
        response = self.client.post(
            "/api/kb/query/",
            {"search": "select_related"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_06_query_returns_matches_and_logs(self):
        self.register("acme", "dev@acme.com", "Acme Corp")
        user = User.objects.get(username="acme")
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.token_for(user)}"
        )

        response = self.client.post(
            "/api/kb/query/",
            {"search": "SELECT_RELATED"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(QueryLog.objects.count(), 1)
        self.assertEqual(
            QueryLog.objects.first().results_count, 1
        )

    def test_07_blank_query_returns_400_and_does_not_log(self):
        self.register("acme", "dev@acme.com", "Acme Corp")
        user = User.objects.get(username="acme")
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.token_for(user)}"
        )

        response = self.client.post(
            "/api/kb/query/",
            {"search": "   "},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(QueryLog.objects.count(), 0)

    def test_08_zero_result_query_still_logs(self):
        self.register("acme", "dev@acme.com", "Acme Corp")
        user = User.objects.get(username="acme")
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.token_for(user)}"
        )

        response = self.client.post(
            "/api/kb/query/",
            {"search": "does-not-exist"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["results"], [])
        self.assertEqual(QueryLog.objects.count(), 1)

    def test_09_client_cannot_access_admin_summary(self):
        self.register("client", "client@example.com", "Client Corp")
        user = User.objects.get(username="client")
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.token_for(user)}"
        )

        response = self.client.get("/api/admin/usage-summary/")
        self.assertEqual(response.status_code, 403)

    def test_10_admin_can_access_usage_summary(self):
        self.register("admin", "admin@example.com", "Admin Corp")
        admin_user = User.objects.get(username="admin")
        admin_user.company.role = Company.Role.ADMIN
        admin_user.company.save(update_fields=["role"])

        self.register("client", "client@example.com", "Client Corp")
        client_user = User.objects.get(username="client")
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.token_for(client_user)}"
        )
        self.client.post(
            "/api/kb/query/",
            {"search": "select_related"},
            format="json",
        )
        self.client.post(
            "/api/kb/query/",
            {"search": "select_related"},
            format="json",
        )
        self.client.post(
            "/api/kb/query/",
            {"search": "JWT"},
            format="json",
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.token_for(admin_user)}"
        )
        response = self.client.get("/api/admin/usage-summary/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_queries"], 3)
        self.assertEqual(response.data["active_companies"], 1)
        self.assertEqual(response.data["top_search_terms"][0]["search_term"], "select_related")
        self.assertEqual(response.data["top_search_terms"][0]["count"], 2)

    def test_11_query_log_belongs_to_authenticated_company(self):
        self.register("first", "first@example.com", "First Corp")
        first_user = User.objects.get(username="first")
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.token_for(first_user)}"
        )
        self.client.post(
            "/api/kb/query/",
            {"search": "JWT"},
            format="json",
        )

        log = QueryLog.objects.get()
        self.assertEqual(log.company.user.username, "first")
