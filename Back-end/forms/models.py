from django.db import models
from django.contrib.auth.models import User
import uuid


class Form(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    welcome_message = models.TextField(blank=True, null=True)  # Welcome screen content
    thank_you_message = models.TextField(blank=True, null=True)  # Thank you screen content
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forms', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Section(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(Form, related_name='sections', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        unique_together = ['form', 'order']
    
    def __str__(self):
        return f"{self.form.title} - {self.title}"


class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('text', 'Text'),
        ('textarea', 'Textarea'),
        ('single_choice', 'Single Choice'),
        ('multi_choice', 'Multi Choice'),
        ('rating', 'Rating'),
        ('scale', 'Scale'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey(Section, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    options = models.JSONField(default=list, blank=True, null=True)  # For choice questions: [{"value": "opt1", "text": "Option 1"}]
    required = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    min_length = models.IntegerField(blank=True, null=True)  # For text/textarea
    max_length = models.IntegerField(blank=True, null=True)  # For text/textarea
    scale = models.JSONField(default=dict, blank=True, null=True)  # For rating/scale: {"min": 1, "max": 5, "labels": [...]}
    visibility = models.JSONField(default=dict, blank=True, null=True)  # {"dependsOn": "q1_3", "showIfIn": ["many", "some"]}
    exclusive_options = models.JSONField(default=list, blank=True, null=True)  # ["none"] - options that exclude others
    
    class Meta:
        ordering = ['order', 'id']
        unique_together = ['section', 'order']
    
    def __str__(self):
        return f"{self.section.title} - {self.text[:50]}"


class Response(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(Form, related_name='responses', on_delete=models.CASCADE)
    user_id = models.CharField(max_length=255, blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"Response to {self.form.title} - {self.submitted_at}"


class Answer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    response = models.ForeignKey(Response, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.JSONField()  # Can store string, number, or array
    
    class Meta:
        unique_together = ['response', 'question']
    
    def __str__(self):
        return f"Answer to {self.question.text[:30]}"
