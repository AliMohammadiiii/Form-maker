#!/usr/bin/env python
"""
Script to create the Superapp Beta Feedback Form
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from forms.models import Form, Section, Question

def create_superapp_form():
    """Create the Superapp Beta Feedback Form"""
    
    # Create form
    form_data = {
        "title": "فرم بازخورد نسخه بتا سوپراپلیکیشن",
        "description": "جمع‌آوری بازخورد کاربران نسخه بتا",
        "status": "draft"
    }
    
    form, created = Form.objects.get_or_create(
        title=form_data["title"],
        defaults=form_data
    )
    
    if not created:
        print(f"Form already exists: {form.title}")
        # Delete existing sections and questions
        form.sections.all().delete()
    
    # Question ID to Question object mapping for visibility dependencies
    question_map = {}
    
    # Section 1: General Experience
    section1 = Section.objects.create(
        form=form,
        title="بخش ۱: تجربه‌ی کلی",
        order=1
    )
    
    # q1_1
    q1_1 = Question.objects.create(
        section=section1,
        text="سؤال ۱.۱: تجربه‌ی کلیت از سوپراپلیکیشن تا الان چطور بوده؟",
        type="rating",
        required=True,
        order=0,
        scale={"min": 1, "max": 5, "labels": ["نیاز به کار", "پایین‌تر از انتظار", "معمولی", "خوب", "عالی"]}
    )
    question_map["q1_1"] = q1_1
    
    # q1_2
    q1_2 = Question.objects.create(
        section=section1,
        text="سؤال ۱.۲: کار با اپ و پیدا کردن امکانات چقدر برات راحت بود؟",
        type="rating",
        required=True,
        order=1,
        scale={"min": 1, "max": 5, "labels": ["خیلی گیج‌کننده", "سخت", "قابل قبول", "راحت", "بدیهی"]}
    )
    question_map["q1_2"] = q1_2
    
    # q1_3
    q1_3 = Question.objects.create(
        section=section1,
        text="سؤال ۱.۳: آیا باگ، هنگ یا خطای فنی دیدی؟",
        type="single_choice",
        required=True,
        order=2,
        options=[
            {"value": "many", "text": "بله، چند مورد زیاد"},
            {"value": "some", "text": "بله، چند مورد کم"},
            {"value": "few", "text": "یکی دو مورد جزئی"},
            {"value": "none", "text": "نه، همه‌چیز خوب بود"}
        ]
    )
    question_map["q1_3"] = q1_3
    
    # q1_3_detail (conditional)
    q1_3_detail = Question.objects.create(
        section=section1,
        text="اگر بله، لطفاً توضیح بده چه اتفاقی افتاد:",
        type="textarea",
        required=False,
        order=3,
        min_length=10,
        visibility={"dependsOn": q1_3.text, "showIfIn": ["many", "some", "few"]}
    )
    question_map["q1_3_detail"] = q1_3_detail
    
    # q1_4
    q1_4 = Question.objects.create(
        section=section1,
        text="سؤال ۱.۴: برداشت اولیه‌ت از طراحی و ظاهر اپ چی بود؟",
        type="single_choice",
        required=True,
        order=4,
        options=[
            {"value": "not_appealing", "text": "جذاب نیست"},
            {"value": "ok_not_exciting", "text": "معمولی، هیجان‌انگیز نیست"},
            {"value": "clean", "text": "تمیز و ساده"},
            {"value": "modern", "text": "مدرن و چشم‌نواز"},
            {"value": "love_it", "text": "خیلی دوستش دارم – حس تازه و خوشایندی داره"}
        ]
    )
    question_map["q1_4"] = q1_4
    
    # q1_5
    q1_5 = Question.objects.create(
        section=section1,
        text="سؤال ۱.۵: اگر بخوای این اپ رو به دوستت معرفی کنی، در یک جمله چی می‌گی؟",
        type="textarea",
        required=False,
        order=5,
        min_length=10
    )
    question_map["q1_5"] = q1_5
    
    # Section 2: Financial Features
    section2 = Section.objects.create(
        form=form,
        title="بخش ۲: امکانات مالی",
        order=2
    )
    
    # q2_1
    q2_1 = Question.objects.create(
        section=section2,
        text="سؤال ۲.۱: از کدوم سرویس‌های مالی استفاده کردی؟",
        type="multi_choice",
        required=False,
        order=0,
        options=[
            {"value": "wallet", "text": "کیف پول"},
            {"value": "payments", "text": "پرداخت"},
            {"value": "p2p", "text": "انتقال فردبه‌فرد"},
            {"value": "bnpl_sod", "text": "خرید اقساطی / حقوق در لحظه (SOD)"},
            {"value": "leasing", "text": "لیزینگ"},
            {"value": "insurance", "text": "بیمه"},
            {"value": "exchange", "text": "صرافی (رمز‌وایز)"},
            {"value": "kyc", "text": "احراز هویت / پروفایل"},
            {"value": "none", "text": "هنوز استفاده نکردم"}
        ],
        exclusive_options=["none"]
    )
    question_map["q2_1"] = q2_1
    
    # q2_2
    q2_2 = Question.objects.create(
        section=section2,
        text="سؤال ۲.۲: از سرویس‌های مالی که استفاده کردی چقدر راضی بودی؟",
        type="rating",
        required=False,
        order=1,
        scale={"min": 1, "max": 5, "labels": ["خیلی ناراضی", "نه چندان راضی", "معمولی", "راضی", "خیلی راضی"]}
    )
    question_map["q2_2"] = q2_2
    
    # q2_3
    q2_3 = Question.objects.create(
        section=section2,
        text="سؤال ۲.۳: در استفاده از امکانات مالی، چقدر احساس اطمینان و امنیت کردی؟",
        type="rating",
        required=False,
        order=2,
        scale={"min": 1, "max": 5, "labels": ["اصلاً", "نگران", "معمولی", "نسبتاً مطمئن", "کاملاً مطمئن"]}
    )
    question_map["q2_3"] = q2_3
    
    # q2_4
    q2_4 = Question.objects.create(
        section=section2,
        text="سؤال ۲.۴: کدوم سرویس مالی برات مفیدتر بود؟",
        type="textarea",
        required=False,
        order=3
    )
    question_map["q2_4"] = q2_4
    
    # q2_5
    q2_5 = Question.objects.create(
        section=section2,
        text="سؤال ۲.۵: چه قابلیت یا خدمتی به نظرت جای خالیش حس می‌شه؟",
        type="textarea",
        required=False,
        order=4
    )
    question_map["q2_5"] = q2_5
    
    # Section 3: Lifestyle Features
    section3 = Section.objects.create(
        form=form,
        title="بخش ۳: امکانات اجتماعی و سبک زندگی",
        order=3
    )
    
    # q3_1
    q3_1 = Question.objects.create(
        section=section3,
        text="سؤال ۳.۱: از کدوم امکانات سبک زندگی یا اجتماعی استفاده کردی؟",
        type="multi_choice",
        required=False,
        order=0,
        options=[
            {"value": "events", "text": "رویدادها"},
            {"value": "shop", "text": "فروشگاه"},
            {"value": "meet", "text": "میت (Meet)"},
            {"value": "chatbot", "text": "چت‌بات"},
            {"value": "news_insights", "text": "اخبار و تحلیل بازار"},
            {"value": "inbl", "text": "خرید هدفمند (INBL)"},
            {"value": "notifications", "text": "اعلان‌ها"},
            {"value": "none", "text": "استفاده نکردم"}
        ],
        exclusive_options=["none"]
    )
    question_map["q3_1"] = q3_1
    
    # q3_2
    q3_2 = Question.objects.create(
        section=section3,
        text="سؤال ۳.۲: این امکانات چقدر مفید و جذاب بودن؟",
        type="rating",
        required=False,
        order=1,
        scale={"min": 1, "max": 5, "labels": ["نامفید", "تا حدی", "مفید", "خیلی مفید", "فوق‌العاده"]}
    )
    question_map["q3_2"] = q3_2
    
    # q3_3
    q3_3 = Question.objects.create(
        section=section3,
        text="سؤال ۳.۳: چت‌بات چقدر برات مفید و قابل تعامل بود؟",
        type="rating",
        required=False,
        order=2,
        scale={"min": 1, "max": 5, "labels": ["گیج‌کننده", "محدود", "قابل قبول", "مفید", "مثل دستیار"]}
    )
    question_map["q3_3"] = q3_3
    
    # q3_4
    q3_4 = Question.objects.create(
        section=section3,
        text="سؤال ۳.۴: از کدوم قابلیت سبک زندگی بیشتر خوشت اومد؟ چرا؟",
        type="textarea",
        required=False,
        order=3
    )
    question_map["q3_4"] = q3_4
    
    # q3_5
    q3_5 = Question.objects.create(
        section=section3,
        text="سؤال ۳.۵: چه قابلیتی باعث می‌شه این اپ برات ضروری بشه؟",
        type="textarea",
        required=False,
        order=4
    )
    question_map["q3_5"] = q3_5
    
    # Section 4: Trust and Brand
    section4 = Section.objects.create(
        form=form,
        title="بخش ۴: اعتماد و برداشت از هویت برند",
        order=4
    )
    
    # q4_1
    q4_1 = Question.objects.create(
        section=section4,
        text="سؤال ۴.۱: چقدر به این اپ در نگهداری اطلاعات مالی و شخصی‌ت اعتماد داری؟",
        type="rating",
        required=False,
        order=0,
        scale={"min": 1, "max": 5, "labels": ["اصلاً", "کمی", "معمولی", "زیاد", "کامل"]}
    )
    question_map["q4_1"] = q4_1
    
    # q4_2
    q4_2 = Question.objects.create(
        section=section4,
        text="سؤال ۴.۲: شفافیت و توضیح سیاست‌های امنیت و حریم خصوصی چطور بود؟",
        type="rating",
        required=False,
        order=1,
        scale={"min": 1, "max": 5, "labels": ["نامشخص", "کمی گیج‌کننده", "قابل‌قبول", "روشن", "کاملاً شفاف"]}
    )
    question_map["q4_2"] = q4_2
    
    # q4_3
    q4_3 = Question.objects.create(
        section=section4,
        text="سؤال ۴.۳: لحن و شخصیت اپ رو چطور توصیف می‌کنی؟",
        type="single_choice",
        required=False,
        order=2,
        options=[
            {"value": "cold", "text": "رسمی یا سرد"},
            {"value": "impersonal", "text": "معمولی، کمی بی‌روح"},
            {"value": "neutral", "text": "خنثی"},
            {"value": "friendly", "text": "دوستانه و نزدیک"},
            {"value": "trusted_friend", "text": "مثل یه دوست یا مشاور قابل‌اعتماد"}
        ]
    )
    question_map["q4_3"] = q4_3
    
    # q4_4
    q4_4 = Question.objects.create(
        section=section4,
        text="سؤال ۴.۴: حس می‌کنی اپ واقعاً به رشد و موفقیتت اهمیت می‌ده؟",
        type="rating",
        required=False,
        order=3,
        scale={"min": 1, "max": 5, "labels": ["اصلاً", "نه خیلی", "تا حدی", "بیشتر مواقع", "کاملاً"]}
    )
    question_map["q4_4"] = q4_4
    
    # q4_5
    q4_5 = Question.objects.create(
        section=section4,
        text="سؤال ۴.۵: با چه کلمه یا جمله‌ای احساس خودت نسبت به این اپ رو توصیف می‌کنی؟",
        type="textarea",
        required=False,
        order=4
    )
    question_map["q4_5"] = q4_5
    
    # Section 5: Suggestions
    section5 = Section.objects.create(
        form=form,
        title="بخش ۵: پیشنهادها و ادامه مسیر",
        order=5
    )
    
    # q5_1
    q5_1 = Question.objects.create(
        section=section5,
        text="اولین چیزی که باید بهبود پیدا کنه چیه؟",
        type="textarea",
        required=False,
        order=0
    )
    question_map["q5_1"] = q5_1
    
    # q5_2
    q5_2 = Question.objects.create(
        section=section5,
        text="چه قابلیتی یا تغییر جدیدی دوست داری در نسخه بعدی ببینی؟",
        type="textarea",
        required=False,
        order=1
    )
    question_map["q5_2"] = q5_2
    
    # q5_3
    q5_3 = Question.objects.create(
        section=section5,
        text="چقدر احتمال داره این اپ رو به دوست یا خانواده‌ت معرفی کنی؟",
        type="rating",
        required=False,
        order=2,
        scale={"min": 1, "max": 5, "labels": ["اصلاً", "کم", "معمولی", "زیاد", "حتماً"]}
    )
    question_map["q5_3"] = q5_3
    
    # q5_4
    q5_4 = Question.objects.create(
        section=section5,
        text="آیا تمایل داری در مصاحبه یا تست کاربری بعدی هم شرکت کنی؟",
        type="single_choice",
        required=False,
        order=3,
        options=[
            {"value": "yes", "text": "بله، خوشحال می‌شم کمک کنم!"},
            {"value": "maybe", "text": "شاید، بستگی به زمانش داره"},
            {"value": "no", "text": "نه، ممنون"}
        ]
    )
    question_map["q5_4"] = q5_4
    
    # q5_4_contact (conditional)
    q5_4_contact = Question.objects.create(
        section=section5,
        text="نام و روش تماس دلخواه:",
        type="textarea",
        required=False,
        order=4,
        visibility={"dependsOn": q5_4.text, "showIfIn": ["yes", "maybe"]}
    )
    question_map["q5_4_contact"] = q5_4_contact
    
    # q5_5
    q5_5 = Question.objects.create(
        section=section5,
        text="هر نکته یا تجربه‌ی دیگری که دوست داری بگی:",
        type="textarea",
        required=False,
        order=5
    )
    question_map["q5_5"] = q5_5
    
    print(f"✅ Form created successfully!")
    print(f"   Title: {form.title}")
    print(f"   ID: {form.id}")
    print(f"   UUID: {form.uuid}")
    print(f"   Sections: {form.sections.count()}")
    print(f"   Total Questions: {Question.objects.filter(section__form=form).count()}")
    print(f"\n📋 Public form URL: /form/{form.uuid}")
    print(f"📝 Edit form URL: /builder/{form.id}")
    
    return form

if __name__ == "__main__":
    create_superapp_form()

