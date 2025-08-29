from django.urls import path
from .views import RegisterView, ResumeUploadView, JobMatchView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Endpoint for user registration.
    path('register/', RegisterView.as_view(), name='register'),

    # Endpoint to get a JWT token pair (access and refresh).
    # This is the login endpoint. Users send their username and password here to get a token.
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Endpoint to get a new access token using a refresh token.
    # Access tokens are short-lived for security. This allows clients to get a new one without forcing the user to log in again.
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Endpoint for uploading a resume.
    path('upload/', ResumeUploadView.as_view(), name='resume-upload'),

    # Endpoint for matching a job description.
    path('match/', JobMatchView.as_view(), name='job-match'),
]
