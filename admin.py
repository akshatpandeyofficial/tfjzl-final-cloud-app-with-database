"""
Task 2 — admin.py for the django-online-course project.

Includes the seven required model imports and the requested admin classes:
QuestionInline, ChoiceInline, QuestionAdmin, and LessonAdmin.

Check model field names against your actual models.py before using this file.
Merge with your existing admin.py instead of deleting unrelated registrations.
"""
from django.contrib import admin
from .models import (
    Choice,
    Course,
    Instructor,
    Learner,
    Lesson,
    Question,
    Submission,
)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_text", "course", "grade")
    list_filter = ("course",)
    search_fields = ("question_text",)
    inlines = [ChoiceInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course")
    list_filter = ("course",)
    search_fields = ("title",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    inlines = [QuestionInline]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("choice_text", "question", "is_correct")
    list_filter = ("is_correct",)
    search_fields = ("choice_text",)


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ("id",)


@admin.register(Learner)
class LearnerAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user__username",)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("learner", "question", "submitted_at")
    list_filter = ("submitted_at",)
    search_fields = ("learner__user__username", "question__question_text")
