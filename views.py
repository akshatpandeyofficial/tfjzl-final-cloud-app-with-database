"""
Task 5 — course/enrollment-based exam views for django-online-course.

This implementation follows the course-based flow: the learner must be
enrolled in the course, answers are saved as Submission records, and the result
is calculated from the saved submissions for that course.

Expected model API (adjust names if your repository differs):
- Learner.user and Learner.enrolledCourses
- Course.question_set
- Question.choices and Question.is_get_score(selected_choice_ids)
- Submission(learner, question), with a ManyToManyField named choices
- Submission.get_score()

Merge these functions into the actual app's views.py. Keep your other views.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Course, Learner, Submission


@login_required
@require_POST
def submit_exam(request, course_id):
    """Save a learner's answers for the selected course and open the results."""
    course = get_object_or_404(Course, pk=course_id)
    learner = get_object_or_404(Learner, user=request.user)

    # Only enrolled learners may submit an exam for this course.
    if not learner.enrolledCourses.filter(pk=course.pk).exists():
        messages.error(request, "You must be enrolled in this course to submit its exam.")
        return redirect("onlinecourse:course_details", course_id=course.pk)

    questions = course.question_set.all()

    for question in questions:
        # The exam form should use each question ID as the input name and
        # submit the selected choice IDs as values.
        selected_choice_ids = request.POST.getlist(str(question.pk))

        submission = Submission.objects.create(
            learner=learner,
            question=question,
        )

        # Restrict submitted IDs to choices belonging to this question.
        valid_choice_ids = question.choices.filter(
            pk__in=selected_choice_ids
        ).values_list("pk", flat=True)
        submission.choices.set(valid_choice_ids)

    return redirect(
        "onlinecourse:show_exam_result",
        course_id=course.pk,
    )


@login_required
def show_exam_result(request, course_id):
    """Calculate and display the current learner's result for one course."""
    course = get_object_or_404(Course, pk=course_id)
    learner = get_object_or_404(Learner, user=request.user)

    if not learner.enrolledCourses.filter(pk=course.pk).exists():
        messages.error(request, "You must be enrolled in this course to view its exam results.")
        return redirect("onlinecourse:course_details", course_id=course.pk)

    # Use the latest submission for each question to avoid counting older attempts.
    submissions = (
        Submission.objects.filter(
            learner=learner,
            question__course=course,
        )
        .select_related("question")
        .prefetch_related("choices", "question__choices")
        .order_by("question_id", "-submitted_at")
    )

    latest_by_question = {}
    for submission in submissions:
        latest_by_question.setdefault(submission.question_id, submission)

    result_rows = []
    total_score = 0
    total_possible_score = 0

    for question in course.question_set.all():
        submission = latest_by_question.get(question.pk)
        if submission is None:
            continue

        score = submission.get_score()
        total_score += score
        total_possible_score += question.grade

        selected_choices = list(submission.choices.all())
        correct_choices = list(question.choices.filter(is_correct=True))
        result_rows.append({
            "question": question,
            "submission": submission,
            "selected_choices": selected_choices,
            "correct_choices": correct_choices,
            "score": score,
            "grade": question.grade,
            "is_correct": score == question.grade,
        })

    percentage = (
        round(total_score * 100 / total_possible_score, 2)
        if total_possible_score
        else 0
    )
    passed = percentage >= 70

    context = {
        "course": course,
        "submissions": [row["submission"] for row in result_rows],
        "results": result_rows,
        "total_score": total_score,
        "total_possible_score": total_possible_score,
        "score": total_score,
        "total": total_possible_score,
        "percentage": percentage,
        "passed": passed,
        "show_congratulations": passed,
    }
    return render(request, "onlinecourse/exam_result_bootstrap.html", context)
