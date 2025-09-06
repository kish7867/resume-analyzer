from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .serializers import UserSerializer, ResumeSerializer, AnalysisSerializer
from .models import Resume, JobDescription, Analysis,User
from .services import extract_text_from_pdf, analyze_resume_with_gemini

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
        serializer = ResumeSerializer(data=request.data)
        if serializer.is_valid():
            # What: Saves the new Resume object, associating it with the currently logged-in user.
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# The main API view to trigger the resume analysis.
# This endpoint connects all the pieces: it takes a resume ID and JD text, calls our AI service and saves the results to the database.
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
            # We need to get the resume text before we can send it to the AI.
            resume_text = extract_text_from_pdf(resume.file)
            if not resume_text:
                return Response({'error': 'Could not extract text from PDF.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Creates and saves the JobDescription object.
            # To keep a record of the JD used for this analysis.
            job_description = JobDescription.objects.create(user=request.user, text=jd_text)

            # Calls the Gemini analysis service 
            # This is the core step where the actual AI analysis happens.
            analysis_result = analyze_resume_with_gemini(resume_text, job_description.text)
            if not analysis_result:
                return Response({'error': 'Failed to get analysis from AI service.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Creates and saves the Analysis object with the result from Gemini.
            # To persist the analysis results in our database for the user's history.
            analysis = Analysis.objects.create(
                user=request.user,
                resume=resume,
                job_description=job_description,
                result=analysis_result
            )

            # Serializes the final analysis object to be sent back as a JSON response.
            # Provides the frontend with a structured response containing the analysis ID and its results.
            serializer = AnalysisSerializer(analysis)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# An API view to list all past analyses for the logged-in user.

class AnalysisHistoryView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AnalysisSerializer

    def get_queryset(self):
        # Filters the queryset to return only Analysis objects belonging to the current user.
        return Analysis.objects.filter(user=self.request.user).order_by('-analyzed_at')


