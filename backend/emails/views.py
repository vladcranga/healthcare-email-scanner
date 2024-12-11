from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Email, EmailAttachment, SuspiciousPattern, EmailAnalysis
from .serializers import (
    EmailSerializer, EmailListSerializer, EmailAttachmentSerializer,
    SuspiciousPatternSerializer, EmailAnalysisSerializer
)
from .permissions import IsAdminOrReadOnly
from .ml_service import EmailAnalyzer, train_email_classifier
from django.db import models
from rest_framework.pagination import PageNumberPagination
from .services.import_export import (
    validate_file_extension,
    export_emails_to_json,
    export_emails_to_csv,
    import_emails_from_json,
    import_emails_from_csv
)


class EmailViewSet(viewsets.ModelViewSet):
    queryset = Email.objects.all()
    serializer_class = EmailSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_quarantined', 'has_attachments']
    search_fields = ['sender', 'subject', 'content']
    ordering_fields = ['received_date', 'status', 'confidence_score']
    ordering = ['-received_date']
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return EmailListSerializer
        return EmailSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Email.objects.filter(assigned_to=user)
        status = self.request.query_params.get('status', None)
        
        if status:
            if status == 'dangerous':
                queryset = queryset.filter(
                    models.Q(status='dangerous') | 
                    models.Q(confidence_score__gte=0.7)
                )
                # Update status for high confidence emails
                high_risk_emails = queryset.filter(
                    confidence_score__gte=0.7,
                    status='suspicious'
                )
                high_risk_emails.update(status='dangerous')
            else:
                queryset = queryset.filter(status=status)
        
        # Add debugging
        total_count = queryset.count()
        print(f"Total emails: {total_count}")
        if status:
            print(f"Filtered by status '{status}': {queryset.count()}")
        
        return queryset.order_by('-received_date')

    @action(detail=True, methods=['post'])
    def quarantine(self, request, pk=None):
        email = self.get_object()
        email.is_quarantined = True
        email.save()
        return Response({'status': 'email quarantined'})

    @action(detail=True, methods=['post'])
    def release(self, request, pk=None):
        if request.user.profile.role != 'admin':
            return Response(
                {'error': 'Only admins can release emails'},
                status=status.HTTP_403_FORBIDDEN
            )
        email = self.get_object()
        email.is_quarantined = False
        email.save()
        return Response({'status': 'email released'})

    @action(detail=False, methods=['post'])
    def analyze_email(self, request):
        """
        Analyze an incoming email for potential security risks
        """
        # Get email content from request
        email_content = request.data.get('content', '')
        
        if not email_content:
            return Response({
                'error': 'No email content provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Initialize email analyzer (in production, this would be a pre-trained model)
        try:
            analyzer = train_email_classifier()
            
            if not analyzer:
                return Response({
                    'error': 'ML model not trained. Generate sample emails first.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Perform ML analysis
            analysis_result = analyzer.predict(email_content)
            
            # Create Email and EmailAnalysis records
            email = Email.objects.create(
                content=email_content,
                status=Email.EmailStatus.SUSPICIOUS if analysis_result['risk_score'] > 0.5 else Email.EmailStatus.SAFE,
                confidence_score=analysis_result['ml_confidence'],
                assigned_to=self.request.user
            )
            
            # Create suspicious patterns if keywords found
            suspicious_keywords = analysis_result['suspicious_keywords']
            matched_patterns = []
            
            for keyword in suspicious_keywords:
                pattern, _ = SuspiciousPattern.objects.get_or_create(
                    pattern=keyword,
                    defaults={
                        'category': 'dynamic',
                        'severity': 6,
                        'description': f'Dynamically detected suspicious keyword: {keyword}'
                    }
                )
                matched_patterns.append(pattern)
            
            # Create email analysis
            email_analysis = EmailAnalysis.objects.create(
                email=email,
                risk_score=analysis_result['risk_score'],
                ml_prediction={
                    'confidence': analysis_result['ml_confidence'],
                    'suspicious_keywords': suspicious_keywords
                }
            )
            
            # Add matched patterns
            if matched_patterns:
                email_analysis.matched_patterns.set(matched_patterns)
            
            return Response({
                'email_id': email.id,
                'risk_score': analysis_result['risk_score'],
                'ml_confidence': analysis_result['ml_confidence'],
                'suspicious_keywords': suspicious_keywords,
                'status': email.status
            })
        
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def suspicious_summary(self, request):
        """
        Provide a summary of suspicious emails
        """
        # Get base queryset for current user
        user_emails = Email.objects.filter(assigned_to=request.user)
        
        # Total emails
        total_emails = user_emails.count()
        
        # Suspicious emails (excluding dangerous ones)
        suspicious_emails = user_emails.filter(status=Email.EmailStatus.SUSPICIOUS).count()
        
        # Dangerous emails (high-risk)
        dangerous_emails = user_emails.filter(
            models.Q(status=Email.EmailStatus.DANGEROUS) | 
            models.Q(confidence_score__gte=0.7)
        ).count()
        
        # Update status for high confidence emails
        high_risk_emails = user_emails.filter(
            confidence_score__gte=0.7,
            status='suspicious'
        )
        high_risk_emails.update(status='dangerous')
        
        # Calculate detection rate based on confidence scores
        # A score closer to 0 for safe emails and closer to 1 for dangerous emails indicates better detection
        emails_with_scores = user_emails.filter(confidence_score__isnull=False)
        if emails_with_scores.exists():
            correct_predictions = (
                # Count safe emails with low confidence scores (< 0.3)
                emails_with_scores.filter(status='safe', confidence_score__lt=0.3).count() +
                # Count suspicious emails with medium confidence scores (0.3 - 0.7)
                emails_with_scores.filter(status='suspicious', confidence_score__gte=0.3, confidence_score__lt=0.7).count() +
                # Count dangerous emails with high confidence scores (>= 0.7)
                emails_with_scores.filter(status='dangerous', confidence_score__gte=0.7).count()
            )
            detection_rate = correct_predictions / emails_with_scores.count()
        else:
            detection_rate = 0
        
        # Add debugging
        print(f"User: {request.user.username}")
        print(f"Total emails: {total_emails}")
        print(f"Suspicious emails: {suspicious_emails}")
        print(f"Dangerous emails: {dangerous_emails}")
        print(f"Detection rate: {detection_rate}")
        
        return Response({
            'total_emails': total_emails,
            'suspicious_emails': suspicious_emails,
            'high_risk_emails': dangerous_emails,
            'detection_rate': detection_rate
        })

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def public_stats(self, request):
        """
        Provide public statistics about the system
        """
        # Total emails
        total_emails = Email.objects.count()
        
        # Suspicious emails (excluding dangerous ones)
        suspicious_emails = Email.objects.filter(status=Email.EmailStatus.SUSPICIOUS).count()
        
        # Dangerous emails
        dangerous_emails = Email.objects.filter(status=Email.EmailStatus.DANGEROUS).count()
        
        # Calculate detection rate based on confidence scores across all emails
        emails_with_scores = Email.objects.filter(confidence_score__isnull=False)
        if emails_with_scores.exists():
            correct_predictions = (
                # Safe emails with low confidence scores (<0.3)
                emails_with_scores.filter(status='safe', confidence_score__lt=0.3).count() +
                # Suspicious emails with medium scores (0.3-0.7)
                emails_with_scores.filter(
                    status='suspicious', confidence_score__gte=0.3, confidence_score__lt=0.7).count() +
                # Dangerous emails with high scores (>=0.7)
                emails_with_scores.filter(status='dangerous', confidence_score__gte=0.7).count()
            )
            detection_rate = correct_predictions / emails_with_scores.count()
        else:
            detection_rate = 0
        
        return Response({
            'total_emails': total_emails,
            'suspicious_emails': suspicious_emails,
            'high_risk_emails': dangerous_emails,
            'detection_rate': detection_rate
        })


class EmailAttachmentViewSet(viewsets.ModelViewSet):
    queryset = EmailAttachment.objects.all()
    serializer_class = EmailAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EmailAttachment.objects.filter(email__assigned_to=self.request.user)


class SuspiciousPatternViewSet(viewsets.ModelViewSet):
    queryset = SuspiciousPattern.objects.all()
    serializer_class = SuspiciousPatternSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['pattern', 'category', 'description']


class EmailAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EmailAnalysis.objects.all()
    serializer_class = EmailAnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.profile.role == 'admin':
            return EmailAnalysis.objects.all()
        return EmailAnalysis.objects.filter(email__assigned_to=user)


@api_view(['GET'])
def export_emails(request, format='json'):
    """Export emails in JSON format"""
    emails = Email.objects.filter(assigned_to=request.user)
    
    if not emails.exists():
        return Response(
            {'error': 'No emails found to export'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    content = export_emails_to_json(emails)
    response = HttpResponse(content, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="emails.json"'
    
    return response


@api_view(['POST'])
def import_emails(request):
    """Import emails from JSON or CSV file"""
    if not request.FILES:
        return Response(
            {'error': 'No file uploaded'},
            status=status.HTTP_400_BAD_REQUEST
        )

    file = request.FILES['file']
    file_type = validate_file_extension(file)
    content = file.read().decode('utf-8')

    try:
        print(f"Importing emails for user: {request.user.username}")
        print(f"File type: {file_type}")
        print(f"Content: {content[:200]}...")  # Print first 200 chars
        
        if file_type == 'json':
            email_data = import_emails_from_json(content)
        else:  # csv
            email_data = import_emails_from_csv(content)

        print(f"Parsed {len(email_data)} emails")
        print("Sample email data:", email_data[0] if email_data else "No emails")
        
        # Assign emails to the current user
        for email in email_data:
            email['assigned_to'] = request.user.id
            print(f"Email status: {email.get('status')}, confidence: {email.get('confidence_score')}")
            
        serializer = EmailSerializer(data=email_data, many=True)
        if serializer.is_valid():
            print("Serializer is valid")
            print("Validated data:", serializer.validated_data[0] if serializer.validated_data else "No data")
            emails = serializer.save()
            print("Saved email status:", emails[0].status if emails else "No emails")
            return Response({'message': f'Successfully imported {len(email_data)} emails'})
            
        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print("Import error:", str(e))
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
