from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmailViewSet,
    EmailAttachmentViewSet,
    SuspiciousPatternViewSet,
    EmailAnalysisViewSet,
    export_emails,
    import_emails,
)

router = DefaultRouter()
router.register(r"emails", EmailViewSet)
router.register(r"attachments", EmailAttachmentViewSet)
router.register(r"patterns", SuspiciousPatternViewSet)
router.register(r"analysis", EmailAnalysisViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # Export/Import endpoints
    path("export/", export_emails, name="export-emails"),
    path("import/", import_emails, name="import-emails"),
]
