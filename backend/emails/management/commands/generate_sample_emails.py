import json
import csv
from django.core.management.base import BaseCommand
from backend.emails.models import (
    Email,
    EmailAttachment,
    SuspiciousPattern,
    EmailAnalysis,
)
from faker import Faker
import re
import argparse
import random
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = "Generate sample healthcare-related emails"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count", type=int, default=50, help="Number of emails to generate"
        )
        parser.add_argument(
            "--format",
            type=str,
            choices=["json", "csv"],
            default="json",
            help="Output format (json or csv)",
        )
        parser.add_argument(
            "--output", type=str, required=True, help="Output file path"
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing emails before generating new ones",
        )

    def generate_healthcare_content(self, fake, is_suspicious, is_dangerous=False):
        """Generate healthcare-related email content"""
        if is_dangerous:
            # High-risk content for dangerous emails
            templates = [
                "URGENT: Your NHS account has been compromised! Click here to verify: {url}",
                "WARNING: Critical medical test results require immediate payment: {url}",
                "FINAL NOTICE: Your medical records will be deleted unless you act now: {url}",
                "Security Alert: Unauthorized access to your healthcare portal detected: {url}",
                "IMMEDIATE ACTION REQUIRED: Your prescription benefits are suspended: {url}",
            ]
            content = random.choice(templates).format(url=fake.url())
            subject = content.split("\n")[0]

        elif is_suspicious:
            # Moderately suspicious content
            templates = [
                "Save up to 80% on NHS prescriptions!\n\nNo prescription needed for:\n- {drug1}\n- {drug2}\n\nNext day delivery - No questions asked!\nOrder now: {url}",
                "Skip NHS waiting times!\n\nPrivate consultations available for:\n- {specialty1}\n- {specialty2}\n\nBook now: {url}",
                "Exclusive medical offer!\n\nGet immediate access to:\n- {treatment1}\n- {treatment2}\n\nLimited time offer: {url}",
            ]
            content = random.choice(templates).format(
                drug1=fake.word(),
                drug2=fake.word(),
                specialty1=fake.word(),
                specialty2=fake.word(),
                treatment1=fake.word(),
                treatment2=fake.word(),
                url=fake.url(),
            )
            subject = (
                "Discount Prescription Medication"
                if "prescription" in content
                else "Private Healthcare Offer"
            )
        else:
            # Safe content
            templates = [
                "Your NHS appointment is confirmed for {date} at {time}.\nLocation: {location}\nDoctor: Dr. {doctor}",
                "Reminder: Your prescription for {medication} is ready for collection at {pharmacy}.",
                "NHS Newsletter: Updates on {topic1} and {topic2}\n\nRead more about our services at {url}",
            ]
            content = random.choice(templates).format(
                date=fake.date(),
                time=fake.time(),
                location=fake.company(),
                doctor=fake.name(),
                medication=fake.word(),
                pharmacy=fake.company(),
                topic1=fake.word(),
                topic2=fake.word(),
                url=fake.url(),
            )
            subject = "NHS: " + content.split("\n")[0]

        return subject, content

    def create_suspicious_patterns(self):
        """Create healthcare-specific suspicious patterns"""
        patterns = [
            {
                "pattern": r"\b\d{3}\s*\d{3}\s*\d{4}\b",
                "category": "NHS_NUMBER",
                "severity": 9,
                "description": "NHS Number in plain text",
                "is_regex": True,
            },
            {
                "pattern": r"\b[A-Z]{2}\s*\d{10,20}\b",
                "category": "EHIC_NUMBER",
                "severity": 8,
                "description": "EHIC Number in plain text",
                "is_regex": True,
            },
            {
                "pattern": "skip nhs waiting",
                "category": "SERVICE_SCAM",
                "severity": 7,
                "description": "Private healthcare scam",
            },
            {
                "pattern": "no prescription needed",
                "category": "MEDICATION_SCAM",
                "severity": 8,
                "description": "Illegal medication sale",
            },
            {
                "pattern": "discount prescription",
                "category": "MEDICATION_SCAM",
                "severity": 7,
                "description": "Medication discount scam",
            },
            {
                "pattern": "urgent test results",
                "category": "EMERGENCY_SCAM",
                "severity": 8,
                "description": "Urgent medical results scam",
            },
            {
                "pattern": "ehic renewal",
                "category": "INSURANCE_SCAM",
                "severity": 7,
                "description": "EHIC renewal scam",
            },
            {
                "pattern": "urgent transfer",
                "category": "phishing",
                "severity": 8,
                "description": "Urgent financial transfer request",
            },
            {
                "pattern": "account suspended",
                "category": "phishing",
                "severity": 7,
                "description": "Warning about account suspension",
            },
            {
                "pattern": "click here immediately",
                "category": "spam",
                "severity": 9,
                "description": "Urgent call to action",
            },
            {
                "pattern": "wire transfer",
                "category": "fraud",
                "severity": 6,
                "description": "Suspicious wire transfer request",
            },
            {
                "pattern": "confidential information",
                "category": "data-leak",
                "severity": 5,
                "description": "Request for sensitive information",
            },
        ]

        for pattern_data in patterns:
            SuspiciousPattern.objects.get_or_create(
                pattern=pattern_data["pattern"],
                defaults={
                    "category": pattern_data["category"],
                    "severity": pattern_data["severity"],
                    "description": pattern_data["description"],
                    "is_regex": pattern_data.get("is_regex", False),
                },
            )

    def handle(self, *args, **options):
        fake = Faker("en_GB")  # Use UK English locale
        count = options["count"]
        output_format = options["format"]
        output_path = options["output"]

        if options["clear"]:
            Email.objects.all().delete()
            EmailAttachment.objects.all().delete()
            EmailAnalysis.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Cleared all existing emails"))

        generated_emails = []

        # Calculate counts for each type
        dangerous_count = count // 5  # 20% dangerous
        suspicious_count = count // 3  # ~33% suspicious
        safe_count = count - dangerous_count - suspicious_count  # remainder safe

        # Generate dangerous emails
        for _ in range(dangerous_count):
            subject, content = self.generate_healthcare_content(
                fake, is_suspicious=True, is_dangerous=True
            )
            email_data = {
                "sender": fake.email(),
                "subject": subject,
                "content": content,
                "status": "dangerous",
                "confidence_score": random.uniform(0.7, 1.0),
                "received_date": (
                    datetime.now() - timedelta(days=random.randint(0, 30))
                ).isoformat(),
                "is_quarantined": True,
            }
            generated_emails.append(email_data)

        # Generate suspicious emails
        for _ in range(suspicious_count):
            subject, content = self.generate_healthcare_content(
                fake, is_suspicious=True
            )
            email_data = {
                "sender": fake.email(),
                "subject": subject,
                "content": content,
                "status": "suspicious",
                "confidence_score": random.uniform(0.3, 0.7),
                "received_date": (
                    datetime.now() - timedelta(days=random.randint(0, 30))
                ).isoformat(),
                "is_quarantined": True,
            }
            generated_emails.append(email_data)

        # Generate safe emails
        for _ in range(safe_count):
            subject, content = self.generate_healthcare_content(
                fake, is_suspicious=False
            )
            email_data = {
                "sender": fake.email(),
                "subject": subject,
                "content": content,
                "status": "safe",
                "confidence_score": random.uniform(0.0, 0.3),
                "received_date": (
                    datetime.now() - timedelta(days=random.randint(0, 30))
                ).isoformat(),
                "is_quarantined": False,
            }
            generated_emails.append(email_data)

        # Shuffle the emails to randomize their order
        random.shuffle(generated_emails)

        # Write to file
        if output_format == "json":
            with open(output_path, "w") as f:
                json.dump(generated_emails, f, indent=2)
        else:  # csv
            with open(output_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=generated_emails[0].keys())
                writer.writeheader()
                writer.writerows(generated_emails)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully generated {count} emails and saved to {output_path}"
            )
        )
