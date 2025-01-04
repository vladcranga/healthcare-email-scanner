import json
import csv
import io
from typing import List, Dict, Any
from django.core.exceptions import ValidationError
from ..models import Email
from ..ml_service import EmailAnalyzer
from datetime import datetime


def validate_file_extension(file) -> str:
    """Validate file extension and return file type"""
    filename = file.name.lower()
    if filename.endswith(".json"):
        return "json"
    elif filename.endswith(".csv"):
        return "csv"
    else:
        raise ValidationError(
            "Unsupported file type. Only JSON and CSV files are allowed."
        )


def export_emails_to_json(emails: List[Email]) -> str:
    """Export emails to JSON format"""
    email_list = []
    for email in emails:
        email_list.append(
            {
                "sender": email.sender,
                "subject": email.subject,
                "content": email.content,
                "status": email.status,
                "confidence_score": email.confidence_score,
                "received_date": email.received_date.isoformat(),
                "is_quarantined": email.is_quarantined,
            }
        )
    return json.dumps(email_list, indent=2)


def export_emails_to_csv(emails: List[Email]) -> str:
    """Export emails to CSV format"""
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(
        [
            "sender",
            "subject",
            "content",
            "status",
            "confidence_score",
            "received_date",
            "is_quarantined",
        ]
    )

    # Write data
    for email in emails:
        writer.writerow(
            [
                email.sender,
                email.subject,
                email.content,
                email.status,
                email.confidence_score,
                email.received_date.isoformat(),
                email.is_quarantined,
            ]
        )

    return output.getvalue()


def import_emails_from_json(content: str) -> List[Dict[str, Any]]:
    """Import emails from JSON format"""
    try:
        data = json.loads(content)
        if not isinstance(data, list):
            raise ValidationError("Invalid JSON format. Expected a list of emails.")

        emails = []
        current_time = datetime.now()
        analyzer = EmailAnalyzer()  # Initialize analyzer once for all emails

        for item in data:
            # Validate required fields
            required_fields = ["sender", "subject", "content"]
            for field in required_fields:
                if field not in item:
                    raise ValidationError(f"Missing required field: {field}")

            # Always set received_date to current time
            item["received_date"] = current_time

            # If no status is provided or it's invalid, classify the email
            if "status" not in item or item["status"] not in [
                "safe",
                "suspicious",
                "dangerous",
            ]:
                # Use EmailAnalyzer to classify the content
                analysis = analyzer.analyze_email(item["content"])
                item["status"] = analysis["status"]
                item["confidence_score"] = analysis["confidence_score"]
            else:
                # Keep original confidence_score or set default based on status
                if "confidence_score" not in item or item["confidence_score"] is None:
                    item["confidence_score"] = (
                        0.5
                        if item["status"] == "suspicious"
                        else (0.8 if item["status"] == "dangerous" else 0.2)
                    )

            # Set quarantine status based on status
            item["is_quarantined"] = item["status"] in ["suspicious", "dangerous"]

            emails.append(item)

        return emails
    except json.JSONDecodeError:
        raise ValidationError("Invalid JSON format")


def import_emails_from_csv(content: str) -> List[Dict[str, Any]]:
    """Import emails from CSV format"""
    try:
        csv_file = io.StringIO(content)
        reader = csv.DictReader(csv_file)

        emails = []
        for row in reader:
            # Validate required fields
            required_fields = ["sender", "subject", "content"]
            for field in required_fields:
                if field not in row or not row[field]:
                    raise ValidationError(f"Missing required field: {field}")

            # Parse dates and set defaults for optional fields
            if "received_date" in row and row["received_date"]:
                row["received_date"] = datetime.fromisoformat(row["received_date"])
            else:
                row["received_date"] = datetime.now()

            row.setdefault("status", "suspicious")
            row.setdefault("confidence_score", None)
            row.setdefault("is_quarantined", False)

            emails.append(row)

        return emails
    except csv.Error:
        raise ValidationError("Invalid CSV format")
