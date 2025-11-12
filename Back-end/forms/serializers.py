from rest_framework import serializers
from .models import Form, Section, Question, Response, Answer


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'id', 'text', 'type', 'options', 'required', 'order',
            'min_length', 'max_length', 'scale', 'visibility', 'exclusive_options'
        ]
    
    def validate(self, data):
        question_type = data.get('type')
        options = data.get('options', [])
        scale = data.get('scale', {})
        
        # Validate options for choice questions
        if question_type in ['single_choice', 'multi_choice']:
            if not options or len(options) == 0:
                raise serializers.ValidationError(
                    f"{question_type} questions must have at least one option"
                )
            # Validate option format
            for option in options:
                if not isinstance(option, dict) or 'value' not in option or 'text' not in option:
                    raise serializers.ValidationError(
                        "Options must be objects with 'value' and 'text' fields"
                    )
        
        # Validate scale for rating/scale questions
        if question_type in ['rating', 'scale']:
            if not scale or 'min' not in scale or 'max' not in scale:
                raise serializers.ValidationError(
                    f"{question_type} questions must have a scale with 'min' and 'max'"
                )
            if scale.get('min', 0) >= scale.get('max', 0):
                raise serializers.ValidationError(
                    "Scale min must be less than max"
                )
        
        return data


class SectionSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, required=False)
    
    class Meta:
        model = Section
        fields = ['id', 'title', 'description', 'order', 'questions', 'created_at']
    
    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        # Filter out questions with empty text
        questions_data = [
            q for q in questions_data 
            if q.get('text') and q.get('text', '').strip()
        ]
        # Remove 'id' from validated_data if present (it's auto-generated)
        section_data_clean = {k: v for k, v in validated_data.items() if k != 'id'}
        section = Section.objects.create(**section_data_clean)
        for question_data in questions_data:
            # Remove 'id' from question_data if present (it's auto-generated)
            question_data_clean = {k: v for k, v in question_data.items() if k != 'id'}
            Question.objects.create(section=section, **question_data_clean)
        return section
    
    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', None)
        
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.order = validated_data.get('order', instance.order)
        instance.save()
        
        if questions_data is not None:
            # Update questions
            existing_question_ids = [q.id for q in instance.questions.all()]
            new_question_ids = [q.get('id') for q in questions_data if q.get('id')]
            
            # Delete removed questions
            for question_id in existing_question_ids:
                if question_id not in new_question_ids:
                    Question.objects.filter(id=question_id).delete()
            
            # Create or update questions (filter out empty questions)
            for question_data in questions_data:
                # Skip questions with empty text
                if not question_data.get('text') or not question_data.get('text', '').strip():
                    continue
                    
                question_id = question_data.get('id')
                if question_id and Question.objects.filter(id=question_id, section=instance).exists():
                    question = Question.objects.get(id=question_id, section=instance)
                    for key, value in question_data.items():
                        if key != 'id':
                            setattr(question, key, value)
                    question.save()
                else:
                    Question.objects.create(section=instance, **{k: v for k, v in question_data.items() if k != 'id'})
        
        return instance


class FormSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, required=False)
    
    class Meta:
        model = Form
        fields = ['id', 'title', 'description', 'status', 'uuid', 'sections', 'welcome_message', 'thank_you_message', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['uuid', 'created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        sections_data = validated_data.pop('sections', [])
        # Set created_by from request user
        validated_data['created_by'] = self.context['request'].user
        # Normalize empty strings to None for welcome_message and thank_you_message
        if 'welcome_message' in validated_data and not validated_data['welcome_message']:
            validated_data['welcome_message'] = None
        if 'thank_you_message' in validated_data and not validated_data['thank_you_message']:
            validated_data['thank_you_message'] = None
        form = Form.objects.create(**validated_data)
        for section_data in sections_data:
            questions_data = section_data.pop('questions', [])
            # Filter out questions with empty text
            questions_data = [
                q for q in questions_data 
                if q.get('text') and q.get('text', '').strip()
            ]
            # Remove 'id' from section_data if present (it's auto-generated)
            section_data_clean = {k: v for k, v in section_data.items() if k != 'id'}
            section = Section.objects.create(form=form, **section_data_clean)
            for question_data in questions_data:
                # Remove 'id' from question_data if present (it's auto-generated)
                question_data_clean = {k: v for k, v in question_data.items() if k != 'id'}
                Question.objects.create(section=section, **question_data_clean)
        return form
    
    def update(self, instance, validated_data):
        sections_data = validated_data.pop('sections', None)
        
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.status = validated_data.get('status', instance.status)
        
        # Handle welcome_message and thank_you_message (allow empty strings to clear)
        if 'welcome_message' in validated_data:
            instance.welcome_message = validated_data['welcome_message'] or None
        if 'thank_you_message' in validated_data:
            instance.thank_you_message = validated_data['thank_you_message'] or None
        
        instance.save()
        
        if sections_data is not None:
            # Update sections
            existing_section_ids = [s.id for s in instance.sections.all()]
            new_section_ids = [s.get('id') for s in sections_data if s.get('id')]
            
            # Delete removed sections
            for section_id in existing_section_ids:
                if section_id not in new_section_ids:
                    Section.objects.filter(id=section_id).delete()
            
            # Create or update sections
            for section_data in sections_data:
                section_id = section_data.get('id')
                if section_id and Section.objects.filter(id=section_id, form=instance).exists():
                    section = Section.objects.get(id=section_id, form=instance)
                    section_serializer = SectionSerializer(section, data=section_data, partial=True)
                    if section_serializer.is_valid():
                        section_serializer.save()
                else:
                    questions_data = section_data.pop('questions', [])
                    # Filter out questions with empty text
                    questions_data = [
                        q for q in questions_data 
                        if q.get('text') and q.get('text', '').strip()
                    ]
                    section = Section.objects.create(form=instance, **{k: v for k, v in section_data.items() if k != 'id'})
                    for question_data in questions_data:
                        Question.objects.create(section=section, **{k: v for k, v in question_data.items() if k != 'id'})
        
        return instance


class FormDetailSerializer(serializers.ModelSerializer):
    """Optimized serializer for public form view"""
    sections = SectionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Form
        fields = ['id', 'title', 'description', 'status', 'uuid', 'sections', 'welcome_message', 'thank_you_message', 'created_by', 'created_at', 'updated_at']


class AnswerSerializer(serializers.ModelSerializer):
    question_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Answer
        fields = ['id', 'question_id', 'value']
    
    def validate(self, data):
        question_id = data.get('question_id')
        value = data.get('value')
        
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            raise serializers.ValidationError("Question does not exist")
        
        # Validate based on question type
        if question.type == 'single_choice':
            if not isinstance(value, str):
                raise serializers.ValidationError("Single choice answers must be a string")
            valid_values = [opt['value'] for opt in question.options or []]
            if value not in valid_values:
                raise serializers.ValidationError(f"Invalid choice. Must be one of: {valid_values}")
        
        elif question.type == 'multi_choice':
            if not isinstance(value, list):
                raise serializers.ValidationError("Multi choice answers must be an array")
            valid_values = [opt['value'] for opt in question.options or []]
            for v in value:
                if v not in valid_values:
                    raise serializers.ValidationError(f"Invalid choice: {v}")
            
            # Check exclusive options
            if question.exclusive_options:
                for exclusive in question.exclusive_options:
                    if exclusive in value and len(value) > 1:
                        raise serializers.ValidationError(
                            f"Option '{exclusive}' is exclusive and cannot be selected with other options"
                        )
        
        elif question.type in ['rating', 'scale']:
            if not isinstance(value, (int, float)):
                raise serializers.ValidationError("Rating/scale answers must be a number")
            scale = question.scale or {}
            min_val = scale.get('min', 1)
            max_val = scale.get('max', 5)
            if value < min_val or value > max_val:
                raise serializers.ValidationError(f"Value must be between {min_val} and {max_val}")
        
        elif question.type in ['text', 'textarea']:
            if not isinstance(value, str):
                raise serializers.ValidationError("Text answers must be a string")
            if question.min_length and len(value) < question.min_length:
                raise serializers.ValidationError(f"Text must be at least {question.min_length} characters")
            if question.max_length and len(value) > question.max_length:
                raise serializers.ValidationError(f"Text must be at most {question.max_length} characters")
        
        return data
    
    def create(self, validated_data):
        question_id = validated_data.pop('question_id')
        question = Question.objects.get(id=question_id)
        validated_data['question'] = question
        return super().create(validated_data)


class ResponseSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, write_only=True)
    form_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Response
        fields = ['id', 'form_id', 'user_id', 'answers', 'submitted_at', 'ip_address']
        read_only_fields = ['submitted_at', 'ip_address']
    
    def validate(self, data):
        form_id = data.get('form_id')
        answers_data = data.get('answers', [])
        
        try:
            form = Form.objects.get(id=form_id)
        except Form.DoesNotExist:
            raise serializers.ValidationError("Form does not exist")
        
        if form.status != 'published':
            raise serializers.ValidationError("Form is not published")
        
        # Collect all questions from all sections
        all_questions = []
        for section in form.sections.all():
            for question in section.questions.all():
                all_questions.append(question)
        
        # Check required questions
        answered_question_ids = [a.get('question_id') for a in answers_data]
        
        # Evaluate conditional visibility
        visible_questions = []
        answers_dict = {a.get('question_id'): a.get('value') for a in answers_data}
        
        for question in all_questions:
            if question.visibility:
                depends_on_id = question.visibility.get('dependsOn')
                show_if_in = question.visibility.get('showIfIn', [])
                
                if depends_on_id:
                    # Find the question this depends on
                    depends_on_question = next(
                        (q for q in all_questions if str(q.id) == str(depends_on_id) or q.text.startswith(depends_on_id)),
                        None
                    )
                    if depends_on_question:
                        depends_answer = answers_dict.get(depends_on_question.id)
                        if depends_answer in show_if_in:
                            visible_questions.append(question)
                    else:
                        # If dependency not found, show by default
                        visible_questions.append(question)
                else:
                    visible_questions.append(question)
            else:
                visible_questions.append(question)
        
        # Check required visible questions
        for question in visible_questions:
            if question.required and question.id not in answered_question_ids:
                raise serializers.ValidationError(
                    f"Required question '{question.text}' is not answered"
                )
        
        return data
    
    def create(self, validated_data):
        form_id = validated_data.pop('form_id')
        answers_data = validated_data.pop('answers')
        form = Form.objects.get(id=form_id)
        
        # Get IP address from request
        request = self.context.get('request')
        ip_address = None
        if request:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
        
        validated_data['form'] = form
        validated_data['ip_address'] = ip_address
        response = Response.objects.create(**validated_data)
        
        # Create answers
        for answer_data in answers_data:
            Answer.objects.create(
                response=response,
                question_id=answer_data['question_id'],
                value=answer_data['value']
            )
        
        return response


class ResponseListSerializer(serializers.ModelSerializer):
    """Serializer for listing responses"""
    answer_count = serializers.SerializerMethodField()
    form_title = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Response
        fields = ['id', 'form', 'form_title', 'user_id', 'submitted_at', 'answer_count', 'display_name']
    
    def get_answer_count(self, obj):
        return obj.answers.count()
    
    def get_form_title(self, obj):
        return obj.form.title if obj.form else None
    
    def get_display_name(self, obj):
        """Extract a name from answers if available, otherwise use user_id or response ID"""
        # Try to find a name field in answers
        for answer in obj.answers.all():
            question = answer.question
            # Check if question text contains name-related keywords
            question_text_lower = question.text.lower()
            if any(keyword in question_text_lower for keyword in ['نام', 'name', 'اسم']):
                if answer.value:
                    return str(answer.value)
        
        # Fallback to user_id if available
        if obj.user_id:
            return obj.user_id
        
        # Final fallback to response ID
        return f"پاسخ #{obj.id}"


class ResponseDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed response view"""
    answers = serializers.SerializerMethodField()
    
    class Meta:
        model = Response
        fields = ['id', 'form', 'user_id', 'submitted_at', 'ip_address', 'answers']
    
    def get_answers(self, obj):
        answers = []
        for answer in obj.answers.all():
            question = answer.question
            answers.append({
                'question_id': question.id,
                'question_text': question.text,
                'question_type': question.type,
                'value': answer.value
            })
        return answers

