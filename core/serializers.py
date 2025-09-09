from rest_framework import serializers
from .models import User, Resume, Analysis, JobDescription

# A serializer for our custom User model.
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        # Marks the password field as write-only.
        # This is a security measure. We never want to send the password hash back out in an API response.
        extra_kwargs = {'password': {'write_only': True}}

    # Overrides the default create method.
    # We need to handle password creation properly. Django's default User model requires a hashed password, not a plain text one. This method takes the plain text password from the request and creates the user with a properly hashed password.
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

# A serializer for the Resume model.
# To handle the serialization of Resume objects, especially for listing them and showing their details.
class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ('id', 'user', 'file', 'uploaded_at')
        # We make the user field read-only because it will be set automatically based on the logged-in user.
        read_only_fields = ('user',)

# A serializer for the Analysis model.
# To convert the results of our AI analysis into a clean JSON format to be sent to the frontend.
class AnalysisSerializer(serializers.ModelSerializer):
    job_description_text = serializers.CharField(source='job_description.text', read_only=True)

    class Meta:
        model = Analysis
        fields = ('id', 'result', 'analyzed_at', 'job_description_text')
