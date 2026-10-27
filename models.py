"""
Task 1 — models.py for the django-online-course project.

This version uses the field names called out by the evaluator:
- Question.question_text
- Choice.choice_text
- Submission with learner/question relationship and a string format.

IMPORTANT: compare with your repository's existing models.py before replacing it.
If Course, Learner, or other models already exist, merge these definitions instead
of creating duplicate model classes. Ensure your views/admin use these same fields.
"""
from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.get_username()


class Learner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course, blank=True, related_name="learners")

    def __str__(self):
        return self.user.get_username()


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="questions")
    question_text = models.CharField(max_length=1000)
    grade = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.question_text

    def is_get_score(self, selected_choices):
        """
        Return the grade if selected choices exactly match the correct choices.
        `selected_choices` may be a queryset, iterable of Choice objects, or IDs.
        """
        correct_ids = set(
            self.choices.filter(is_correct=True).values_list("id", flat=True)
        )
        selected_ids = set()
        for item in selected_choices:
            selected_ids.add(item.pk if hasattr(item, "pk") else int(item))
        return self.grade if correct_ids == selected_ids else 0


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    choice_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text


class Submission(models.Model):
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE, related_name="submissions")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="submissions")
    choices = models.ManyToManyField(Choice, blank=True, related_name="submissions")
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.learner} — {self.question}"

    def get_score(self):
        return self.question.is_get_score(self.choices.all())

    def __str__(self):
        return f"{self.learner} — {self.question}"
