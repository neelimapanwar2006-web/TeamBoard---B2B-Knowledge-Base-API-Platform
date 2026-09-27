from django.contrib import admin
from django.urls import path
from api.views import (
    RegisterView,
    LoginView,
    KBQueryView,
    UsageSummaryView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/login/", LoginView.as_view(), name="login"),
    path("api/kb/query/", KBQueryView.as_view(), name="kb-query"),
    path("api/admin/usage-summary/", UsageSummaryView.as_view(), name="usage-summary"),
]
