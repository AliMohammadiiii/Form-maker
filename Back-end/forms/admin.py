from django.contrib import admin
from .models import Form, Section, Question, Response, Answer


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description']


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'form', 'order']
    list_filter = ['form']
    ordering = ['form', 'order']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'section', 'type', 'required', 'order']
    list_filter = ['type', 'required', 'section__form']
    ordering = ['section', 'order']


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ['form', 'user_id', 'submitted_at']
    list_filter = ['form', 'submitted_at']
    readonly_fields = ['submitted_at']


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'response', 'value']
    list_filter = ['question__section__form']
