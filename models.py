"""
Task 1 — models.py reference for the django-online-course project.

This version uses:
- Question.question_text
- Choice.choice_text
- Submission.learner and Submission.question foreign keys
- Submission.__str__() returning a string
- Question.is_get_score() for evaluating selected choices

IMPORTANT: compare this with your repository's existing models.py before
replacing anything. Merge with existing Course/Learner/Instructor/Lesson models
rather than defining duplicate classes. Update related views/admin if needed.
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
    enrolledCourses = models.ManyToManyField(Course, blank=True, related_name="learners")

    def __str__(self):
        return self.user.get_username()


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="question_set")
    question_text = models.CharField(max_length=1000)
    grade = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.question_text

    def is_get_score(self, selected_choices):
        """Return grade if selected choices exactly match all correct choices."""
        correct_ids = set(
            self.choices.filter(is_correct=True).values_list("pk", flat=True)
        )
        selected_ids = set()
        for choice in selected_choices:
            selected_ids.add(choice.pk if hasattr(choice, "pk") else int(choice))
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

    def get_score(self):
        """Calculate the score from this submission's saved choices."""
        return self.question.is_get_score(self.choices.all())

    def __str__(self):
        return f"{self.learner} — {self.question}"
