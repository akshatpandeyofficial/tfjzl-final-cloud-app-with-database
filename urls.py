"""
Task 6 — app-level urls.py for the course-based exam flow.

Required routes:
  /<int:course_id>/submit/       -> views.submit
  /<int:course_id>/exam/results/  -> views.show_exam_result

The evaluator specifically expects the int:course_id/submit/ route to call
views.submit, plus a course/submission results route to views.show_exam_result.

Merge these paths into the urlpatterns in the app's actual urls.py. Keep any
other existing routes. Confirm the URL names match redirects and template tags.
"""
from django.urls import path
from . import views

app_name = "onlinecourse"

urlpatterns = [
    path(
        "<int:course_id>/submit/",
        views.submit,
        name="submit",
    ),
    path(
        "<int:course_id>/exam/results/",
        views.show_exam_result,
        name="show_exam_result",
    ),
]
