from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Count, Q
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Company, KBEntry, QueryLog
from .permissions import IsAdminUser


def get_access_token(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        company_name = request.data.get("company_name")
        email = request.data.get("email", "")

        if not username or not password or not company_name:
            return Response(
                {
                    "detail": "username, password and company_name are required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        from django.contrib.auth.models import User

        if User.objects.filter(username=username).exists():
            return Response(
                {"detail": "Username already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
        )

        company = user.company
        company.company_name = company_name
        company.save(update_fields=["company_name"])

        return Response(
            {
                "username": user.username,
                "company_name": company.company_name,
                "api_key": company.api_key,
                "access": get_access_token(user),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(
            username=username,
            password=password,
        )

        if user is None:
            return Response(
                {"detail": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        company = getattr(user, "company", None)
        if company is None:
            return Response(
                {"detail": "Company profile not found."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "access": get_access_token(user),
                "company_name": company.company_name,
                "api_key": company.api_key,
            },
            status=status.HTTP_200_OK,
        )


class KBQueryView(APIView):
    def post(self, request):
        search_term = request.data.get("search")

        if not isinstance(search_term, str) or not search_term.strip():
            return Response(
                {"detail": "search is required and cannot be blank."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        search_term = search_term.strip()
        company = request.user.company

        with transaction.atomic():
            entries = list(
                KBEntry.objects.filter(
                    Q(question__icontains=search_term)
                    | Q(answer__icontains=search_term)
                ).order_by("id")
            )
            results_count = len(entries)

            QueryLog.objects.create(
                company=company,
                search_term=search_term,
                results_count=results_count,
            )

        results = [
            {
                "id": entry.id,
                "question": entry.question,
                "answer": entry.answer,
                "category": entry.category,
            }
            for entry in entries
        ]

        return Response(
            {
                "search": search_term,
                "count": results_count,
                "results": results,
            },
            status=status.HTTP_200_OK,
        )


class UsageSummaryView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_queries = QueryLog.objects.aggregate(
            total=Count("id")
        )["total"]

        active_companies = (
            QueryLog.objects.values("company")
            .distinct()
            .count()
        )

        top_search_terms = list(
            QueryLog.objects.values("search_term")
            .annotate(count=Count("id"))
            .order_by("-count", "search_term")[:5]
        )

        return Response(
            {
                "total_queries": total_queries,
                "active_companies": active_companies,
                "top_search_terms": top_search_terms,
            },
            status=status.HTTP_200_OK,
        )
