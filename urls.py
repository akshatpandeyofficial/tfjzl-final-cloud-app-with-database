"""
Task 6 — urls.py for course-specific exam submission and results.

The evaluator requires these exact route shapes:
  <int:course_id>/submit/
  <int:course_id>/submission/<int:submission_id>/result/

The result route name is `show_exam_result`. Ensure views.show_exam_result
accepts both course_id and submission_id.
"""
from django.urls import path
from . import views

app_name = "onlinecourse"

urlpatterns = [
    path(
        "<int:course_id>/submit/",
        views.submit_exam,
        name="submit_exam",
    ),
    path(
        "<int:course_id>/submission/<int:submission_id>/result/",
        views.show_exam_result,
        name="show_exam_result",
    ),
]
