import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
import django

django.setup()

from backend.emails.models import (
    Email,
    SuspiciousPattern,
    EmailAnalysis,
    EmailAttachment,
)

print("Suspicious Patterns:")
for pattern in SuspiciousPattern.objects.all().values(
    "pattern", "category", "severity"
):
    print(pattern)

print("\nTotal Emails:", Email.objects.count())

print("\nSuspicious Emails:")
suspicious_emails = Email.objects.filter(status=Email.EmailStatus.SUSPICIOUS)[:5]
for email in suspicious_emails:
    print(
        f"Sender: {email.sender}, Subject: {email.subject}, Confidence Score: {email.confidence_score}"
    )

print("\nEmail Analyses:", EmailAnalysis.objects.count())
print("Email Attachments:", EmailAttachment.objects.count())

# Detailed view of a suspicious email's analysis
if suspicious_emails:
    print("\nDetailed Analysis of First Suspicious Email:")
    first_suspicious_email = suspicious_emails[0]
    analysis = first_suspicious_email.analysis
    print(f"Risk Score: {analysis.risk_score}")
    print("Matched Patterns:")
    for pattern in analysis.matched_patterns.all():
        print(
            f"- {pattern.pattern} (Category: {pattern.category}, Severity: {pattern.severity})"
        )
