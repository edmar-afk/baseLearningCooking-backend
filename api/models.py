from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model

User = get_user_model()

class UserExtraInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    year_level = models.TextField(blank=True, null=True)
    section = models.TextField(blank=True, null=True)
    role = models.TextField(blank=True, null=True)
    
    

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Quizzes(models.Model):
    DIFFICULTY_CHOICES = [
        ("Easy", "Easy"),
        ("Medium", "Medium"),
        ("Hard", "Hard"),
    ]

    title = models.CharField(max_length=255)
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default="Easy",
    )

    def __str__(self):
        return self.title

    @property
    def number_of_questions(self):
        return self.questions.count()


class QuestionsAndAnswers(models.Model):
    ANSWER_CHOICES = [
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
    ]

    lesson = models.ForeignKey(
        Quizzes,
        on_delete=models.CASCADE,
        related_name="questions",
    )

    question_text = models.TextField()

    choice_a = models.CharField(max_length=500)
    choice_b = models.CharField(max_length=500)
    choice_c = models.CharField(max_length=500)
    choice_d = models.CharField(max_length=500)

    correct_answer = models.CharField(
        max_length=1,
        choices=ANSWER_CHOICES,
    )

    explanation = models.TextField(blank=True, default="")

    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lesson.title} - {self.question_text[:50]}"

    class Meta:
        verbose_name = "Question and Answer"
        verbose_name_plural = "Questions and Answers"
        ordering = ["id"]




class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quiz_attempts")
    lesson = models.ForeignKey(Quizzes, on_delete=models.CASCADE, related_name="quiz_attempts")
    score = models.PositiveIntegerField()
    total_questions = models.PositiveIntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)

    @property
    def percentage(self):
        return round((self.score / self.total_questions) * 100, 2) if self.total_questions > 0 else 0

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} - {self.score}/{self.total_questions}"

    class Meta:
        ordering = ["-completed_at"]
        
        
        


class Lessons(models.Model):
    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    topic = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="lessons/images/", blank=True, null=True)

    def __str__(self):
        return self.title or f"Lesson {self.pk}"


class LessonVideos(models.Model):
    lesson = models.ForeignKey(Lessons, on_delete=models.CASCADE, related_name="videos")
    video = models.FileField(upload_to="lessons/videos/")

    def __str__(self):
        return f"Video for {self.lesson.title or self.lesson.pk}"


class Presentation(models.Model):
    title = models.TextField(blank=True, null=True)
    file = models.FileField(
        upload_to="presentations/",
        validators=[
            FileExtensionValidator(allowed_extensions=["ppt", "pptx"])
        ]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or self.file.name

    class Meta:
        ordering = ["-uploaded_at"]
        
        
        
from django.core.validators import MinValueValidator, MaxValueValidator

class LessonProgress(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="lesson_progress_records",
    )
    lesson = models.ForeignKey(
        Lessons,
        on_delete=models.CASCADE,
        related_name="student_progress_records",
    )
    progress_percent = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "lesson"],
                name="unique_student_lesson_progress",
            )
        ]

    @property
    def completed(self):
        return self.progress_percent >= 100

    def __str__(self):
        return f"{self.user.username} - {self.lesson_id}: {self.progress_percent}%"        