import re
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

import tensorflow as tf
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder

class EmailAnalyzer:
    def __init__(self):
        # Healthcare-specific scam patterns
        self.scam_patterns = {
            'EMERGENCY_SCAM': [
                r'urgent\s+(?:test|lab|scan)\s+results?',
                r'critical\s+(?:medical|health)\s+(?:finding|record)s?',
                r'immediate\s+medical\s+attention\s+required',
                r'important\s+health\s+update',
            ],
            'INSURANCE_SCAM': [
                r'(?:nhs|healthcare|medical)\s+refund\s+available',
                r'ehic\s+(?:renewal|expir)',
                r'insurance\s+claim\s+(?:pending|approved)',
                r'outstanding\s+(?:medical|health)\s+(?:bill|payment)',
                r'healthcare\s+tax\s+refund',
            ],
            'MEDICATION_SCAM': [
                r'(?:cheap|discount)\s+(?:prescription|medication|drug)s?',
                r'buy\s+medicines?\s+online',
                r'no\s+prescription\s+(?:needed|required)',
                r'miracle\s+(?:cure|treatment)',
                r'covid.*(?:cure|treatment|medicine)',
            ],
            'SERVICE_SCAM': [
                r'(?:private|exclusive)\s+(?:gp|doctor)\s+slots?',
                r'skip\s+(?:nhs|hospital)\s+waiting\s+list',
                r'fast\s*track\s+(?:surgery|treatment)',
                r'exclusive\s+medical\s+(?:offer|treatment)',
            ],
            'GENERAL_SCAM': [
                r'limited\s+time\s+offer',
                r'act\s+(?:now|fast|quickly)',
                r'special\s+(?:offer|discount)',
                r'guaranteed\s+(?:cure|treatment)',
                r'revolutionary\s+(?:treatment|therapy)',
            ]
        }
        
        # Initialize feature extractors
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 3),  # Include phrases up to 3 words
            stop_words='english'
        )
        self.label_encoder = LabelEncoder()
        
        # Placeholder for ML model
        self.model = None
    
    def preprocess_email(self, email_text: str) -> str:
        """
        Preprocess email text by cleaning and normalizing
        """
        # Convert to lowercase
        text = email_text.lower()
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Normalize common variations
        text = text.replace('£', 'GBP ')
        text = text.replace('€', 'EUR ')
        text = re.sub(r'\d+%', 'PERCENTAGE', text)
        
        return text
    
    def check_patterns(self, email_text: str) -> Dict[str, List[str]]:
        """
        Check for all types of suspicious patterns in the email
        """
        email_text = self.preprocess_email(email_text)
        matches = defaultdict(list)
        
        # Check each category of scam patterns
        for category, patterns in self.scam_patterns.items():
            for pattern in patterns:
                if re.search(pattern, email_text, re.IGNORECASE):
                    matches[category].append(pattern)
        
        return dict(matches)
    
    def analyze_urgency(self, email_text: str) -> float:
        """
        Analyze the urgency level of the email
        """
        urgency_indicators = [
            r'urgent', r'immediate', r'emergency', r'critical',
            r'act now', r'limited time', r'expires?', r'deadline'
        ]
        
        email_text = self.preprocess_email(email_text)
        urgency_count = sum(1 for indicator in urgency_indicators 
                          if re.search(indicator, email_text, re.IGNORECASE))
        
        return min(urgency_count * 0.2, 1.0)  # Cap at 1.0
    
    def analyze_pressure_tactics(self, email_text: str) -> float:
        """
        Analyze pressure tactics used in the email
        """
        pressure_indicators = [
            r'only\s+\d+\s+left',
            r'limited\s+(?:time|offer|availability)',
            r'exclusive\s+offer',
            r'special\s+price',
            r'one\s+time\s+(?:offer|opportunity)',
            r'today\s+only',
            r'act\s+(?:now|fast|quickly)',
        ]
        
        email_text = self.preprocess_email(email_text)
        pressure_count = sum(1 for indicator in pressure_indicators 
                           if re.search(indicator, email_text, re.IGNORECASE))
        
        return min(pressure_count * 0.15, 1.0)  # Cap at 1.0
    
    def calculate_risk_score(self, email_text: str, ml_confidence: float) -> Tuple[float, Dict]:
        """
        Calculate a comprehensive risk score with detailed analysis
        """
        # Get pattern matches
        pattern_matches = self.check_patterns(email_text)
        
        # Calculate component scores
        pattern_score = min(len([match for matches in pattern_matches.values() 
                               for match in matches]) * 0.15, 1.0)
        urgency_score = self.analyze_urgency(email_text)
        pressure_score = self.analyze_pressure_tactics(email_text)
        
        # Weighted combination of scores
        risk_score = (
            0.4 * ml_confidence +      # ML model confidence
            0.3 * pattern_score +      # Suspicious patterns
            0.2 * urgency_score +      # Urgency indicators
            0.1 * pressure_score       # Pressure tactics
        )
        
        analysis_details = {
            'pattern_matches': pattern_matches,
            'component_scores': {
                'ml_confidence': ml_confidence,
                'pattern_score': pattern_score,
                'urgency_score': urgency_score,
                'pressure_score': pressure_score
            }
        }
        
        return min(risk_score, 1.0), analysis_details
    
    def extract_features(self, emails: List[str]) -> np.ndarray:
        """
        Extract TF-IDF features from email texts
        """
        # Preprocess emails
        processed_emails = [self.preprocess_email(email) for email in emails]
        
        # Vectorize emails
        features = self.tfidf_vectorizer.fit_transform(processed_emails)
        
        return features.toarray()
    
    def train_model(self, emails: List[str], labels: List[str]):
        """
        Train a simple neural network for email classification
        """
        # Preprocess and extract features
        X = self.extract_features(emails)
        y = self.label_encoder.fit_transform(labels)
        
        # Split data
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        
        # Build a simple neural network
        self.model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(X.shape[1],)),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        
        self.model.compile(
            optimizer='adam', 
            loss='binary_crossentropy', 
            metrics=['accuracy']
        )
        
        # Train the model
        self.model.fit(
            X_train, y_train, 
            epochs=10, 
            batch_size=32, 
            validation_split=0.2,
            verbose=0
        )
        
        # Evaluate
        loss, accuracy = self.model.evaluate(X_test, y_test)
        print(f"Model Accuracy: {accuracy}")
    
    def predict(self, email_text: str) -> Dict[str, float]:
        """
        Predict the likelihood of an email being suspicious
        """
        if not self.model:
            raise ValueError("Model not trained. Call train_model() first.")
        
        # Preprocess and extract features
        features = self.extract_features([email_text])
        
        # Predict
        ml_confidence = self.model.predict(features)[0][0]
        
        # Calculate comprehensive risk score
        risk_score, analysis_details = self.calculate_risk_score(email_text, ml_confidence)
        
        return {
            'ml_confidence': float(ml_confidence),
            'risk_score': risk_score,
            'analysis_details': analysis_details
        }

# Utility function to load training data
def load_training_data() -> tuple:
    """
    Load training data for the email classifier
    Simulates loading from a dataset
    """
    from backend.emails.models import Email
    
    # Fetch emails from database
    safe_emails = Email.objects.filter(status=Email.EmailStatus.SAFE)
    suspicious_emails = Email.objects.filter(status=Email.EmailStatus.SUSPICIOUS)
    
    emails = [
        *[email.content for email in safe_emails],
        *[email.content for email in suspicious_emails]
    ]
    
    labels = [
        *['safe'] * safe_emails.count(),
        *['suspicious'] * suspicious_emails.count()
    ]
    
    return emails, labels

def train_email_classifier():
    """
    Train the email classifier using existing email data
    """
    analyzer = EmailAnalyzer()
    emails, labels = load_training_data()
    
    if len(emails) > 0:
        analyzer.train_model(emails, labels)
        return analyzer
    else:
        print("Not enough training data. Generate more sample emails first.")
        return None
