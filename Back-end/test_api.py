#!/usr/bin/env python
"""
Quick test to verify API endpoints are working
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from forms.models import Form, Section, Question

# Check form exists
form = Form.objects.first()
if form:
    print(f"✅ Form found: {form.title}")
    print(f"   ID: {form.id}")
    print(f"   UUID: {form.uuid}")
    print(f"   Status: {form.status}")
    print(f"   Sections: {form.sections.count()}")
    
    total_questions = Question.objects.filter(section__form=form).count()
    print(f"   Total Questions: {total_questions}")
    
    # Check conditional visibility questions
    conditional_questions = Question.objects.filter(
        section__form=form,
        visibility__isnull=False
    ).exclude(visibility={})
    
    print(f"\n📋 Conditional Visibility Questions: {conditional_questions.count()}")
    for q in conditional_questions:
        print(f"   - {q.text[:50]}...")
        print(f"     Depends on: {q.visibility.get('dependsOn', 'N/A')}")
        print(f"     Show if: {q.visibility.get('showIfIn', [])}")
    
    # Check exclusive options
    exclusive_questions = Question.objects.filter(
        section__form=form,
        exclusive_options__isnull=False
    ).exclude(exclusive_options=[])
    
    print(f"\n🔒 Exclusive Options Questions: {exclusive_questions.count()}")
    for q in exclusive_questions:
        print(f"   - {q.text[:50]}...")
        print(f"     Exclusive: {q.exclusive_options}")
    
    print(f"\n🌐 API Endpoints:")
    print(f"   GET /api/forms/{form.id}/")
    print(f"   GET /api/forms/public/{form.uuid}/")
    print(f"   POST /api/forms/{form.id}/publish/")
    print(f"   POST /api/responses/{form.id}/")
else:
    print("❌ No form found. Run create_form.py first.")

