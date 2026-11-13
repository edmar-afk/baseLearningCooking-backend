
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import UserExtraInfo, Quizzes, QuestionsAndAnswers, Lessons, LessonVideos, Presentation, LessonProgress

User = get_user_model()


class UserExtraInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserExtraInfo
        fields = ["year_level", "section", "role"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    year_level = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    section = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    # Accept the role selected in the React registration form.
    role = serializers.ChoiceField(
        choices=[
            ("student", "Student"),
            ("teacher", "Teacher"),
        ],
        write_only=True,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "year_level",
            "section",
            "role",
        ]
        read_only_fields = ["id"]

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "This username is already taken."
            )
        return value

    def validate_email(self, value):
        if value and User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "This email is already registered."
            )
        return value

    def validate(self, attrs):
        role = attrs.get("role")

        # Require an email for teachers.
        if role == "teacher" and not attrs.get("email", "").strip():
            raise serializers.ValidationError({
                "email": "Email is required for teacher accounts."
            })

        # Prevent student-only data from being saved for teachers.
        if role == "teacher":
            attrs["year_level"] = ""
            attrs["section"] = ""

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        year_level = validated_data.pop("year_level", None)
        section = validated_data.pop("section", None)
        role = validated_data.pop("role")
        password = validated_data.pop("password")

        # Create a regular account without staff/admin privileges.
        user = User(**validated_data)
        user.set_password(password)
        user.is_staff = False
        user.is_superuser = False
        user.save()

        # Save the actual selected role.
        UserExtraInfo.objects.create(
            user=user,
            year_level=year_level or "",
            section=section or "",
            role=role,
        )

        return user



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        extra_info, _ = UserExtraInfo.objects.get_or_create(
            user=user,
            defaults={"role": "student"},
        )

        # Custom claims included in the JWT.
        token["username"] = user.username
        token["email"] = user.email
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        token["is_staff"] = user.is_staff
        token["is_superuser"] = user.is_superuser

        token["year_level"] = extra_info.year_level
        token["section"] = extra_info.section
        token["role"] = extra_info.role

        return token



class QuestionsAndAnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionsAndAnswers
        fields = [
            "id",
            "lesson",
            "question_text",
            "choice_a",
            "choice_b",
            "choice_c",
            "choice_d",
            "correct_answer",
            "explanation",
            "date_added",
        ]
        read_only_fields = ["id", "date_added"]


class QuizzesSerializer(serializers.ModelSerializer):
    number_of_questions = serializers.IntegerField(read_only=True)

    class Meta:
        model = Quizzes
        fields = [
            "id",
            "title",
            "difficulty",
            "number_of_questions",
        ]
        read_only_fields = ["id", "number_of_questions"]


class LessonDetailSerializer(serializers.ModelSerializer):
    questions = QuestionsAndAnswersSerializer(many=True, read_only=True)
    number_of_questions = serializers.IntegerField(read_only=True)

    class Meta:
        model = Quizzes
        fields = [
            "id",
            "title",
            "difficulty",
            "number_of_questions",
            "questions",
        ]
        read_only_fields = ["id", "number_of_questions", "questions"]




class LessonVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonVideos
        fields = ["id", "video"]


class LessonsSerializer(serializers.ModelSerializer):
    videos = LessonVideoSerializer(many=True, read_only=True)
    uploaded_videos = serializers.ListField(child=serializers.FileField(), write_only=True, required=False)
    delete_video_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = Lessons
        fields = ["id", "title", "description", "topic", "image", "videos", "uploaded_videos", "delete_video_ids"]

    def create(self, validated_data):
        uploaded_videos = validated_data.pop("uploaded_videos", [])
        validated_data.pop("delete_video_ids", None)

        lesson = Lessons.objects.create(**validated_data)

        for video in uploaded_videos:
            LessonVideos.objects.create(lesson=lesson, video=video)

        return lesson

    def update(self, instance, validated_data):
        uploaded_videos = validated_data.pop("uploaded_videos", [])
        delete_video_ids = validated_data.pop("delete_video_ids", [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if delete_video_ids:
            instance.videos.filter(id__in=delete_video_ids).delete()

        for video in uploaded_videos:
            LessonVideos.objects.create(lesson=instance, video=video)

        return instance
    
    
    
class PresentationSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Presentation
        fields = ["id", "title", "file", "file_url", "uploaded_at"]
        read_only_fields = ["id", "file_url", "uploaded_at"]

    def get_file_url(self, obj):
        if not obj.file:
            return None

        request = self.context.get("request")
        url = obj.file.url

        return request.build_absolute_uri(url) if request else url



class LessonProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    completed = serializers.SerializerMethodField()

    class Meta:
        model = LessonProgress
        fields = [
            "id",
            "lesson",
            "lesson_title",
            "progress_percent",
            "completed",
            "updated_at",
        ]
        read_only_fields = ["id", "lesson_title", "completed", "updated_at"]

    def get_completed(self, obj):
        return obj.progress_percent >= 100