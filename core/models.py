from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # we are not adding any new fields right now. It inherits everything from AbstractUser.
    pass

class Resume(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Resume for {self.user.username} uploaded at {self.uploaded_at.strftime('%Y-%m-%d')}"
    
class JobDescription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        # Returns the first 50 characters of the JD for a concise representation.
        return f"JD for {self.user.username}: {self.text[:50]}..."
    
class Analysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    job_description = models.ForeignKey(JobDescription, on_delete=models.CASCADE)

    # What: A field specifically designed to store JSON data.
    # Why: The AI will give us a structured result (score, skills, suggestions). JSONField is the perfect, native way to store this flexible data in the database.
    # Consequence if not done: We'd have to store it as a plain text field and manually parse the JSON every time we read it, which is inefficient and brittle.
    result = models.JSONField()
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for {self.user.username} on {self.analyzed_at.strftime('%Y-%m-%d')}"
