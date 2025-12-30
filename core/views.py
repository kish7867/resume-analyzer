from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .serializers import UserSerializer, ResumeSerializer, AnalysisSerializer
from .models import User, Resume, JobDescription, Analysis
from .services import extract_text_from_pdf, analyze_resume_with_llama

# An API view for user registration.
# This provides a public endpoint (no authentication required) for new users to create an account.
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

# An API view for uploading resume files.
# This provides a secure endpoint for authenticated users to upload their PDF resumes.
class ResumeUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Creates a serializer instance with the uploaded file data.
        # The serializer validates the incoming data (ensuring a file was actually uploaded) before we attempt to save it.
        serializer = ResumeSerializer(data=request.data)
        if serializer.is_valid():
            # Saves the new Resume object, associating it with the currently logged-in user.
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# The main API view to trigger the resume analysis.
# This endpoint connects all the pieces: it takes a resume ID and JD text, calls our AI service 
class AnalyzeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        resume_id = request.data.get('resume_id')
        jd_text = request.data.get('jd_text')

        # Basic validation to ensure the required data was sent.
        if not resume_id or not jd_text:
            return Response({'error': 'Resume ID and Job Description are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieves the Resume object from the database, ensuring it exists and belongs to the current user.
        resume = get_object_or_404(Resume, pk=resume_id, user=request.user)

        try:
            # Calls the text extraction service 
            resume_text = extract_text_from_pdf(resume.file)
            if not resume_text:
                return Response({'error': 'Could not extract text from PDF.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Creates and saves the JobDescription object.
            job_description = JobDescription.objects.create(user=request.user, text=jd_text)

            # Calls the Gemini analysis service 
            # This is the core step where the actual AI analysis happens.
            analysis_result = analyze_resume_with_llama(resume_text, job_description.text)
            if not analysis_result:
                return Response({'error': 'Failed to get analysis from AI service.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Creates and saves the Analysis object with the result from Gemini.
            analysis = Analysis.objects.create(
                user=request.user,
                resume=resume,
                job_description=job_description,
                result=analysis_result
            )

            # Serializes the final analysis object to be sent back as a JSON response.
            serializer = AnalysisSerializer(analysis)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# An API view to list all past analyses for the logged-in user.
# To populate the "History" page in our frontend.
class AnalysisHistoryView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AnalysisSerializer

    def get_queryset(self):
        # Filters the queryset to return only Analysis objects belonging to the current user.
        return Analysis.objects.filter(user=self.request.user).order_by('-analyzed_at')
