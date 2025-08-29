from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Resume, Skill, ExtractedSkill
from .serializers import UserSerializer, ResumeSerializer
from .services import extract_text_from_pdf, extract_skills
import os

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

class ResumeUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('resume_file')
        if not file_obj:
                    return Response({"error": "Resume file is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        resume_instance = Resume.objects.create(user=request.user, resume_file=file_obj)
        
        try:
            # Extracts text from the PDF using our service function.
            text = extract_text_from_pdf(resume_instance.resume_file.path)
            resume_instance.content = text
            resume_instance.save()
            # Extracts skills from the text using our service function.
            skills = extract_skills(text)

            for skill_name in skills:
                # 'get_or_create' is efficient. It prevents duplicate skills in our main Skill table. If 'python' already exists, it retrieves it; otherwise, it creates it.
                skill_obj, created = Skill.objects.get_or_create(name=skill_name)
                ExtractedSkill.objects.create(resume=resume_instance, skill=skill_obj)
            
            # Serializes the final resume instance to return as a JSON response.
            serializer = ResumeSerializer(resume_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            # If anything goes wrong during parsing or extraction, we delete the created resume instance to avoid orphaned files and return a meaningful error.
            resume_instance.delete()
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class JobMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Gets the job description text from the request body.
        # This is the text we need to compare against the user's resume.
        job_description = request.data.get('job_description')
        if not job_description:
            return Response({"error": "Job description is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            latest_resume = Resume.objects.filter(user=request.user).latest('uploaded_at')
        except Resume.DoesNotExist:
            return Response({"error": "No resume found. Please upload one first."}, status=status.HTTP_404_NOT_FOUND)
        
        # Extracts required skills from the job description text.
        required_skills = set(extract_skills(job_description))
        if not required_skills:
            return Response({"message": "Could not identify any skills in the job description."}, status=status.HTTP_200_OK)
        
        # Retrieves the skills from the user's resume that are stored in our database.
        user_skills = set(ExtractedSkill.objects.filter(resume=latest_resume).values_list('skill__name', flat=True))

        # Finds the intersection of the two skill sets.
        matched_skills = user_skills.intersection(required_skills)

        # Calculates the match score as a percentage.
        match_percentage = (len(matched_skills) / len(required_skills)) * 100 if required_skills else 0    

        return Response({
            "match_percentage": f"{match_percentage:.2f}%",
            "required_skills": list(required_skills),
            "your_skills": list(user_skills),
            "matched_skills": list(matched_skills)
        }, status=status.HTTP_200_OK)