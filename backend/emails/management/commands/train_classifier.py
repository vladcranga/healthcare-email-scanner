from django.core.management.base import BaseCommand
from backend.emails.models import Email
from backend.emails.ml_service import EmailAnalyzer

class Command(BaseCommand):
    help = 'Train the email classifier using existing emails in the database'

    def handle(self, *args, **options):
        # Get all emails from the database
        emails = Email.objects.all()
        
        if emails.count() == 0:
            self.stdout.write(self.style.WARNING('No emails found in database. Generate sample emails first.'))
            return
        
        # Prepare training data
        email_texts = [email.content for email in emails]
        labels = [email.status for email in emails]
        
        # Initialize and train the analyzer
        analyzer = EmailAnalyzer()
        analyzer.train_model(email_texts, labels)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully trained classifier on {len(email_texts)} emails'))
