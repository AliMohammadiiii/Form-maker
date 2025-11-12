from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Form, Response as FormResponse, Question, Answer
from .serializers import (
    FormSerializer, FormDetailSerializer,
    ResponseSerializer, ResponseListSerializer, ResponseDetailSerializer
)
from collections import Counter
import re


class FormViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing forms (CRUD operations)
    Users can only see and manage their own forms
    """
    serializer_class = FormSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only forms created by the current user"""
        return Form.objects.filter(created_by=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return FormDetailSerializer
        return FormSerializer
    
    def get_serializer_context(self):
        """Add request to serializer context"""
        context = super().get_serializer_context()
        if hasattr(self, 'request'):
            context['request'] = self.request
        return context
    
    def create(self, request, *args, **kwargs):
        """Override create to add better error handling"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                instance = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                import traceback
                print(f"Error creating form: {e}")
                print(traceback.format_exc())
                return Response(
                    {'detail': f'Error creating form: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            print(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """Override update to ensure user owns the form"""
        instance = self.get_object()
        if instance.created_by != request.user:
            return Response(
                {'detail': 'You do not have permission to perform this action.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Override destroy to ensure user owns the form"""
        instance = self.get_object()
        if instance.created_by != request.user:
            return Response(
                {'detail': 'You do not have permission to perform this action.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """
        Publish a form (set status to published)
        POST /forms/{id}/publish/
        """
        form = self.get_object()
        # Ensure user owns this form
        if form.created_by != request.user:
            return Response(
                {'detail': 'You do not have permission to perform this action.'},
                status=status.HTTP_403_FORBIDDEN
            )
        form.status = 'published'
        form.save()
        serializer = self.get_serializer(form)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        """
        Unpublish a form (set status to draft)
        POST /forms/{id}/unpublish/
        """
        form = self.get_object()
        # Ensure user owns this form
        if form.created_by != request.user:
            return Response(
                {'detail': 'You do not have permission to perform this action.'},
                status=status.HTTP_403_FORBIDDEN
            )
        form.status = 'draft'
        form.save()
        serializer = self.get_serializer(form)
        return Response(serializer.data)


class PublicFormView(APIView):
    """
    Get a published form by UUID (public access - no authentication required)
    GET /forms/public/{uuid}/
    """
    permission_classes = [AllowAny]
    
    def get(self, request, uuid):
        form = get_object_or_404(Form, uuid=uuid, status='published')
        serializer = FormDetailSerializer(form)
        return Response(serializer.data)


class ResponseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing form responses
    Users can only see responses to their own forms
    GET /responses/ - List all responses for user's forms
    GET /responses/{id}/ - Get specific response
    GET /responses/?form_id=1 - Filter by form
    """
    serializer_class = ResponseListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ResponseDetailSerializer
        return ResponseListSerializer
    
    def get_queryset(self):
        """
        Filter responses to only show responses for forms created by the user
        GET /responses/?form_id=1
        """
        # Get all forms created by the user
        user_forms = Form.objects.filter(created_by=self.request.user)
        queryset = FormResponse.objects.filter(form__in=user_forms)
        
        # Filter by form_id if provided
        form_id = self.request.query_params.get('form_id', None)
        if form_id is not None:
            # Ensure the form belongs to the user
            if not user_forms.filter(id=form_id).exists():
                return FormResponse.objects.none()
            queryset = queryset.filter(form_id=form_id)
        return queryset


class SubmitResponseView(APIView):
    """
    Submit a response to a form (public access - no authentication required)
    POST /responses/submit/{form_id}/
    """
    permission_classes = [AllowAny]
    
    def post(self, request, form_id):
        data = request.data.copy()
        data['form_id'] = form_id
        serializer = ResponseSerializer(
            data=data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FormAnalysisView(APIView):
    """
    Get analysis data for a form
    GET /forms/{id}/analysis/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        form = get_object_or_404(Form, id=pk)
        
        # Ensure user owns this form
        if form.created_by != request.user:
            return Response(
                {'detail': 'You do not have permission to perform this action.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get all responses for this form
        responses = FormResponse.objects.filter(form=form)
        total_responses = responses.count()
        
        if total_responses == 0:
            return Response({
                'total_responses': 0,
                'questions': []
            })
        
        # Get all questions from all sections
        all_questions = []
        for section in form.sections.all():
            for question in section.questions.all():
                all_questions.append(question)
        
        # Analyze each question
        question_analyses = []
        for question in all_questions:
            answers = Answer.objects.filter(
                question=question,
                response__in=responses
            )
            
            analysis = {
                'question_id': question.id,
                'question_text': question.text,
                'question_type': question.type,
                'total_answers': answers.count(),
                'data': self._analyze_question(question, answers)
            }
            question_analyses.append(analysis)
        
        return Response({
            'total_responses': total_responses,
            'questions': question_analyses
        })
    
    def _analyze_question(self, question, answers):
        """Analyze answers based on question type"""
        if question.type == 'single_choice':
            return self._analyze_single_choice(question, answers)
        elif question.type == 'multi_choice':
            return self._analyze_multi_choice(question, answers)
        elif question.type in ['rating', 'scale']:
            return self._analyze_rating_scale(question, answers)
        elif question.type == 'text':
            return self._analyze_text(question, answers, short=True)
        elif question.type == 'textarea':
            return self._analyze_text(question, answers, short=False)
        return {}
    
    def _analyze_single_choice(self, question, answers):
        """Analyze single choice questions"""
        option_counts = Counter()
        for answer in answers:
            value = answer.value
            if isinstance(value, str):
                option_counts[value] += 1
        
        # Get option texts
        options_map = {opt['value']: opt['text'] for opt in (question.options or [])}
        
        distribution = []
        for value, count in option_counts.most_common():
            distribution.append({
                'value': value,
                'label': options_map.get(value, value),
                'count': count,
                'percentage': round((count / len(answers)) * 100, 1) if answers.count() > 0 else 0
            })
        
        return {
            'distribution': distribution,
            'total': len(answers)
        }
    
    def _analyze_multi_choice(self, question, answers):
        """Analyze multiple choice questions"""
        option_counts = Counter()
        total_selections = 0
        co_occurrence = {}
        
        for answer in answers:
            values = answer.value
            if isinstance(values, list):
                total_selections += len(values)
                for value in values:
                    option_counts[value] += 1
                
                # Track co-occurrence
                for i, v1 in enumerate(values):
                    if v1 not in co_occurrence:
                        co_occurrence[v1] = Counter()
                    for v2 in values[i+1:]:
                        co_occurrence[v1][v2] += 1
                        if v2 not in co_occurrence:
                            co_occurrence[v2] = Counter()
                        co_occurrence[v2][v1] += 1
        
        options_map = {opt['value']: opt['text'] for opt in (question.options or [])}
        
        distribution = []
        for value, count in option_counts.most_common():
            distribution.append({
                'value': value,
                'label': options_map.get(value, value),
                'count': count,
                'percentage': round((count / len(answers)) * 100, 1) if answers.count() > 0 else 0
            })
        
        # Build co-occurrence matrix
        co_occurrence_matrix = []
        for value1 in option_counts.keys():
            row = []
            for value2 in option_counts.keys():
                if value1 == value2:
                    row.append(option_counts[value1])
                else:
                    row.append(co_occurrence.get(value1, Counter()).get(value2, 0))
            co_occurrence_matrix.append({
                'option': value1,
                'label': options_map.get(value1, value1),
                'co_occurrences': row
            })
        
        return {
            'distribution': distribution,
            'total_responses': len(answers),
            'total_selections': total_selections,
            'average_selections': round(total_selections / len(answers), 2) if answers.count() > 0 else 0,
            'co_occurrence_matrix': co_occurrence_matrix
        }
    
    def _analyze_rating_scale(self, question, answers):
        """Analyze rating/scale questions"""
        values = []
        for answer in answers:
            value = answer.value
            if isinstance(value, (int, float)):
                values.append(float(value))
        
        if not values:
            return {
                'distribution': [],
                'statistics': {}
            }
        
        # Distribution
        scale = question.scale or {}
        min_val = scale.get('min', 1)
        max_val = scale.get('max', 5)
        labels = scale.get('labels', [])
        
        distribution = []
        for i in range(int(min_val), int(max_val) + 1):
            count = values.count(i)
            distribution.append({
                'value': i,
                'label': labels[i - int(min_val)] if i - int(min_val) < len(labels) else str(i),
                'count': count,
                'percentage': round((count / len(values)) * 100, 1) if values else 0
            })
        
        # Statistics
        sorted_values = sorted(values)
        mean = sum(values) / len(values)
        median = sorted_values[len(sorted_values) // 2] if sorted_values else 0
        
        # Calculate standard deviation
        variance = sum((x - mean) ** 2 for x in values) / len(values) if values else 0
        std_dev = variance ** 0.5
        
        # NPS-style scoring (promoters vs detractors)
        mid_point = (min_val + max_val) / 2
        promoters = sum(1 for v in values if v >= max_val - 1)
        detractors = sum(1 for v in values if v <= min_val + 1)
        nps_score = ((promoters - detractors) / len(values)) * 100 if values else 0
        
        return {
            'distribution': distribution,
            'statistics': {
                'mean': round(mean, 2),
                'median': round(median, 2),
                'std_dev': round(std_dev, 2),
                'min': min(values) if values else 0,
                'max': max(values) if values else 0,
                'nps_score': round(nps_score, 1),
                'promoters': promoters,
                'detractors': detractors
            },
            'total': len(values)
        }
    
    def _analyze_text(self, question, answers, short=False):
        """Analyze text/textarea questions"""
        texts = []
        for answer in answers:
            value = answer.value
            if isinstance(value, str) and value.strip():
                texts.append(value.strip())
        
        if not texts:
            return {
                'total': 0,
                'frequency': [],
                'word_cloud': []
            }
        
        if short:
            # For short text: frequency analysis
            word_freq = Counter()
            for text in texts:
                # Simple word extraction (split by spaces, remove punctuation)
                words = re.findall(r'\b\w+\b', text.lower())
                word_freq.update(words)
            
            top_words = word_freq.most_common(20)
            frequency = [{'word': word, 'count': count} for word, count in top_words]
            
            return {
                'total': len(texts),
                'frequency': frequency,
                'word_cloud': frequency[:10]  # Top 10 for word cloud
            }
        else:
            # For long text: sentiment and theme analysis (simplified)
            # In a real implementation, you'd use NLP libraries
            word_freq = Counter()
            for text in texts:
                words = re.findall(r'\b\w+\b', text.lower())
                word_freq.update(words)
            
            top_words = word_freq.most_common(30)
            frequency = [{'word': word, 'count': count} for word, count in top_words]
            
            # Simple sentiment (placeholder - in production use proper NLP)
            # For now, just return word frequency
            return {
                'total': len(texts),
                'frequency': frequency,
                'word_cloud': frequency[:15],
                'sample_responses': texts[:5]  # Show first 5 responses as samples
            }
