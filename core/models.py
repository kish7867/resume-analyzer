from django.db import models
from django.contrib.auth.models import AbstractUser


# Custom User model that inherits from Django's built-in AbstractUser
class User(AbstractUser):
    pass

# Defines the database model for storing uploaded resumes.

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Provides a human-readable name for the object, useful in the Django admin panel.
        return f"Resume for {self.user.username} uploaded at {self.uploaded_at.strftime('%Y-%m-%d')}"

# Defines the model for storing job descriptions that users paste.
class JobDescription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        # Returns the first 50 characters of the JD for a concise representation.
        return f"JD for {self.user.username}: {self.text[:50]}..."

# Defines the model to store the results of the AI analysis.
class Analysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    job_description = models.ForeignKey(JobDescription, on_delete=models.CASCADE)

    # A field specifically designed to store JSON data.
    result = models.JSONField()
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for {self.user.username} on {self.analyzed_at.strftime('%Y-%m-%d')}"
