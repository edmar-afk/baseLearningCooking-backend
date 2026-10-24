
from django.contrib.auth import get_user_model

from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from .models import UserExtraInfo, Quizzes, QuestionsAndAnswers, Lessons, LessonVideos, QuizAttempt, Presentation
from .serializers import (
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    UserExtraInfoSerializer,  QuizzesSerializer,
        LessonDetailSerializer,
        QuestionsAndAnswersSerializer, LessonsSerializer, LessonVideoSerializer, PresentationSerializer
)
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        extra_info = UserExtraInfo.objects.get(user=user)

        return Response(
            {
                "message": "Registration successful.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                    "extra_info": UserExtraInfoSerializer(
                        extra_info
                    ).data,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user

        extra_info, _ = UserExtraInfo.objects.get_or_create(
            user=user,
            defaults={"role": "student"},
        )

        return Response(
            {
                "access": serializer.validated_data["access"],
                "refresh": serializer.validated_data["refresh"],
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                    "extra_info": UserExtraInfoSerializer(
                        extra_info
                    ).data,
                },
            },
            status=status.HTTP_200_OK,
        )



# ==========================================================
# Quizzes: LIST AND CREATE
# ==========================================================

class QuizzesListCreateView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        quizzes = Quizzes.objects.all().order_by("-id")
        serializer = QuizzesSerializer(quizzes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = QuizzesSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )



# ==========================================================
# Quizzes: RETRIEVE, UPDATE, DELETE
# ==========================================================
class LessonDetailView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, pk):
        lesson = get_object_or_404(Quizzes, pk=pk)
        serializer = LessonDetailSerializer(lesson)
        return Response(serializer.data)

    def put(self, request, pk):
        lesson = get_object_or_404(Quizzes, pk=pk)
        serializer = QuizzesSerializer(
            lesson,
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        lesson = get_object_or_404(Quizzes, pk=pk)
        serializer = QuizzesSerializer(
            lesson,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        lesson = get_object_or_404(Quizzes, pk=pk)
        lesson.delete()

        return Response(
            {"message": "Lesson deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ==========================================================
# QUESTIONS: LIST BY LESSON AND CREATE
# ==========================================================
class LessonQuestionsListCreateView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, lesson_id):
        lesson = get_object_or_404(Quizzes, pk=lesson_id)
        questions = lesson.questions.all().order_by("id")

        serializer = QuestionsAndAnswersSerializer(
            questions,
            many=True,
        )
        return Response(serializer.data)

    def post(self, request, lesson_id):
        lesson = get_object_or_404(Quizzes, pk=lesson_id)

        # The lesson is determined by the URL, not the request body.
        data = request.data.copy()
        data["lesson"] = lesson.pk

        serializer = QuestionsAndAnswersSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
# QUESTIONS: RETRIEVE, UPDATE, DELETE
# ==========================================================
class QuestionDetailView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, pk):
        question = get_object_or_404(
            QuestionsAndAnswers,
            pk=pk,
        )
        serializer = QuestionsAndAnswersSerializer(question)
        return Response(serializer.data)

    def put(self, request, pk):
        question = get_object_or_404(
            QuestionsAndAnswers,
            pk=pk,
        )
        serializer = QuestionsAndAnswersSerializer(
            question,
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        question = get_object_or_404(
            QuestionsAndAnswers,
            pk=pk,
        )
        serializer = QuestionsAndAnswersSerializer(
            question,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        question = get_object_or_404(
            QuestionsAndAnswers,
            pk=pk,
        )
        question.delete()

        return Response(
            {"message": "Question deleted successfully."},
            status=status.HTTP_200_OK,
        )



class LessonsListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Lessons.objects.prefetch_related("videos").all().order_by("-id")
    serializer_class = LessonsSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class LessonsDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    queryset = Lessons.objects.prefetch_related("videos").all()
    serializer_class = LessonsSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class LessonVideoDeleteView(generics.DestroyAPIView):
    permission_classes = [AllowAny]
    queryset = LessonVideos.objects.all()




class QuizAttemptSubmitView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, quiz_id):
        quiz = get_object_or_404(Quizzes, pk=quiz_id)

        # Expected format: {"answers": {"1": "A", "2": "C"}}
        answers = request.data.get("answers", {})

        if not isinstance(answers, dict):
            return Response(
                {"error": "Answers must be an object."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        questions = list(quiz.questions.all())
        total_questions = len(questions)

        if total_questions == 0:
            return Response(
                {"error": "This quiz has no questions."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Calculate the score using answers stored in Django.
        score = sum(
            1
            for question in questions
            if answers.get(str(question.id), answers.get(question.id))
            == question.correct_answer
        )

        # The authenticated JWT user is used automatically.
        attempt = QuizAttempt.objects.create(
            user=request.user,
            lesson=quiz,
            score=score,
            total_questions=total_questions,
        )

        return Response(
            {
                "message": "Quiz submitted successfully.",
                "score": attempt.score,
                "total_questions": attempt.total_questions,
                "percentage": attempt.percentage,
                "attempt_id": attempt.id,
                "completed_at": attempt.completed_at,
            },
            status=status.HTTP_201_CREATED,
        )




class QuizAttemptDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, quiz_id):
        quiz = get_object_or_404(Quizzes, pk=quiz_id)

        attempt = QuizAttempt.objects.filter(
            user=request.user,
            lesson=quiz,
        ).first()

        if attempt is None:
            return Response(
                {"detail": "No saved attempt found for this quiz."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "id": attempt.id,
                "score": attempt.score,
                "total_questions": attempt.total_questions,
                "percentage": attempt.percentage,
                "completed_at": attempt.completed_at,
            },
            status=status.HTTP_200_OK,
        )



class UserQuizAttemptsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        attempts = QuizAttempt.objects.filter(
            user=request.user
        ).select_related("lesson").order_by("-completed_at")

        data = []

        for attempt in attempts:
            percentage = (
                round((attempt.score / attempt.total_questions) * 100, 2)
                if attempt.total_questions > 0
                else 0
            )

            data.append({
                "id": attempt.id,
                "quiz_id": attempt.lesson_id,
                "quiz_title": attempt.lesson.title,
                "category": attempt.lesson.difficulty or "General",
                "score": attempt.score,
                "total_questions": attempt.total_questions,
                "percentage": percentage,
                "completed_at": attempt.completed_at,
            })

        return Response(data)
    
    


def is_teacher(user):
    extra_info = getattr(user, "userextrainfo", None)
    return (
        extra_info is not None
        and (getattr(extra_info, "role", "") or "").lower() == "teacher"
    )


class PresentationListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        presentations = Presentation.objects.all()
        serializer = PresentationSerializer(
            presentations,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    def post(self, request):
        if not is_teacher(request.user):
            return Response(
                {"detail": "Only teachers can upload presentations."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = PresentationSerializer(
            data=request.data,
            context={"request": request},
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PresentationDetailView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, pk):
        if not is_teacher(request.user):
            return Response(
                {"detail": "Only teachers can delete presentations."},
                status=status.HTTP_403_FORBIDDEN,
            )

        presentation = get_object_or_404(Presentation, pk=pk)

        if presentation.file:
            presentation.file.delete(save=False)

        presentation.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)