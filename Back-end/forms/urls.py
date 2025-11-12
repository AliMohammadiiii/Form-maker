from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import FormViewSet, PublicFormView, ResponseViewSet, SubmitResponseView, FormAnalysisView
from .auth_views import SignupView, LoginView, UserView

router = DefaultRouter()
router.register(r'forms', FormViewSet, basename='form')
router.register(r'responses', ResponseViewSet, basename='response')

urlpatterns = [
    # Authentication routes
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/user/', UserView.as_view(), name='user'),
    # JWT token routes
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Custom routes must come before router.urls to avoid conflicts
    path('forms/public/<uuid:uuid>/', PublicFormView.as_view(), name='public-form'),
    path('forms/<uuid:pk>/analysis/', FormAnalysisView.as_view(), name='form-analysis'),
    # Submit response route - must come before router to avoid 405 conflicts
    path('responses/submit/<uuid:form_id>/', SubmitResponseView.as_view(), name='submit-response'),
    path('', include(router.urls)),
]

