from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('quizzes/', views.QuizzesListCreateView.as_view(), name='quizzes-list-create'),
    path('quizzes/<int:pk>/', views.LessonDetailView.as_view(), name='lesson-detail'),
    path('quizzes/<int:lesson_id>/questions/', views.LessonQuestionsListCreateView.as_view(), name='lesson-questions-list-create'),
    path('questions/<int:pk>/', views.QuestionDetailView.as_view(), name='question-detail'),
    
    path("lessons/", views.LessonsListCreateView.as_view(), name="lessons-list-create"),
    path("lessons/<int:pk>/", views.LessonsDetailView.as_view(), name="lessons-detail"),
    path("lesson-videos/<int:pk>/delete/", views.LessonVideoDeleteView.as_view(), name="lesson-video-delete"),
    
    path('quizzes/<int:quiz_id>/submit/', views.QuizAttemptSubmitView.as_view(), name='quiz-attempt-submit'),
    path('quizzes/<int:quiz_id>/my-attempt/', views.QuizAttemptDetailView.as_view(), name='quiz-attempt-detail'),
    path('quiz-attempts/', views.UserQuizAttemptsView.as_view(), name='user-quiz-attempts'),
    
    
    path("presentations/", views.PresentationListCreateView.as_view(), name="presentation-list-create"),
    path("presentations/<int:pk>/", views.PresentationDetailView.as_view(), name="presentation-detail"),

]