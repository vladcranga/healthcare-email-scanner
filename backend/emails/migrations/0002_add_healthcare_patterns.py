from django.db import migrations

def add_healthcare_patterns(apps, schema_editor):
    SuspiciousPattern = apps.get_model('emails', 'SuspiciousPattern')
    
    patterns = [
        {
            'pattern': r'\b\d{3}\s*\d{3}\s*\d{4}\b',
            'category': 'NHS_NUMBER',
            'severity': 3,
            'description': 'NHS Number detected - 10 digit identifier for patients in the UK healthcare system',
            'is_regex': True,
            'is_active': True
        },
        {
            'pattern': r'\b[A-Z]{2}\s*\d{10,20}\b',
            'category': 'EHIC_NUMBER',
            'severity': 3,
            'description': 'European Health Insurance Card number detected',
            'is_regex': True,
            'is_active': True
        },
        {
            'pattern': r'\b[A-Z]{1}\d{6}\b',
            'category': 'NHS_PRESCRIPTION',
            'severity': 2,
            'description': 'NHS Prescription code detected',
            'is_regex': True,
            'is_active': True
        },
        {
            'pattern': r'\b[A-Z]{2}/\d{1}/\d{2}/\d{3}/\d{3}\b',
            'category': 'EMA_DRUG_CODE',
            'severity': 2,
            'description': 'European Medicines Agency drug code detected',
            'is_regex': True,
            'is_active': True
        },
        {
            'pattern': r'\b\d{2,3}\.\d{2}\.\d{2}\.\d{3}\b',
            'category': 'BNF_CODE',
            'severity': 2,
            'description': 'British National Formulary (BNF) code detected',
            'is_regex': True,
            'is_active': True
        },
        {
            'pattern': r'\b\d{6,18}\b',
            'category': 'SNOMED_CT',
            'severity': 2,
            'description': 'Possible SNOMED CT code detected',
            'is_regex': True,
            'is_active': True
        },
        # Additional patterns for common variations
        {
            'pattern': r'\bNHS\s*#?\s*\d{3}\s*\d{3}\s*\d{4}\b',
            'category': 'NHS_NUMBER_WITH_PREFIX',
            'severity': 3,
            'description': 'NHS Number with prefix detected',
            'is_regex': True,
            'is_active': True
        },
        {
            'pattern': r'\bEHIC\s*#?\s*[A-Z]{2}\s*\d{10,20}\b',
            'category': 'EHIC_NUMBER_WITH_PREFIX',
            'severity': 3,
            'description': 'EHIC Number with prefix detected',
            'is_regex': True,
            'is_active': True
        }
    ]
    
    for pattern_data in patterns:
        SuspiciousPattern.objects.create(**pattern_data)

def remove_healthcare_patterns(apps, schema_editor):
    SuspiciousPattern = apps.get_model('emails', 'SuspiciousPattern')
    categories = [
        'NHS_NUMBER', 'EHIC_NUMBER', 'NHS_PRESCRIPTION',
        'EMA_DRUG_CODE', 'BNF_CODE', 'SNOMED_CT',
        'NHS_NUMBER_WITH_PREFIX', 'EHIC_NUMBER_WITH_PREFIX'
    ]
    SuspiciousPattern.objects.filter(category__in=categories).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('emails', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_healthcare_patterns, remove_healthcare_patterns),
    ]
