from rest_framework import serializers
from .models import User, Resume, Analysis, JobDescription

# A serializer for our custom User model.
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        # Marks the password field as write-only.
        # This is a security measure. Never send the password hash back out in an API response.
        extra_kwargs = {'password': {'write_only': True}}
    
    # Django's default User model requires a hashed password, not a plain text one. This method takes the plain text password from the request and creates the user with a properly hashed password.
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

# A serializer for the Resume model. 
class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ('id', 'file', 'uploaded_at')

# What: A serializer for the Analysis model
class AnalysisSerializer(serializers.ModelSerializer):
    job_description_text = serializers.CharField(source='job_description.text', read_only=True)

    class Meta:
        model = Analysis
        fields = ('id', 'result', 'analyzed_at', 'job_description_text')