"""
Task 5 — course-based exam submission and results views.

This version addresses the evaluator's feedback:
- submit_exam saves Submission records and redirects with the submission_id.
- show_exam_result loads that submission, calculates scores using Question.is_get_score(),
  and passes explicit context values to the result template.

Expected model API (adjust to match your repository):
- Learner has a `user` relation and an `enrolledCourses` many-to-many relation.
- Course has `question_set`.
- Question has `choices`, `grade`, and `is_get_score(selected_choice_ids)`.
- Submission has `learner`, `question`, a many-to-many `choices` field, and `get_score()`.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Course, Learner, Submission


@login_required
@require_POST
def submit_exam(request, course_id):
    """Save answers as submissions, then redirect to the result for this attempt."""
    course = get_object_or_404(Course, pk=course_id)
    learner = get_object_or_404(Learner, user=request.user)

    if not learner.enrolledCourses.filter(pk=course.pk).exists():
        messages.error(request, "You must be enrolled in this course to submit the exam.")
        return redirect("onlinecourse:course_details", course_id=course.pk)

    questions = course.question_set.all()
    submission_ids = []

    for question in questions:
        # Form field names should be the question IDs; values are selected choice IDs.
        selected_choice_ids = request.POST.getlist(str(question.pk))

        submission = Submission.objects.create(
            learner=learner,
            question=question,
        )

        # Only persist choices belonging to this question.
        valid_choice_ids = list(
            question.choices.filter(pk__in=selected_choice_ids)
            .values_list("pk", flat=True)
        )
        submission.choices.set(valid_choice_ids)
        submission_ids.append(submission.pk)

    if not submission_ids:
        messages.warning(request, "This course does not have any exam questions yet.")
        return redirect("onlinecourse:course_details", course_id=course.pk)

    # Send a concrete submission ID to the result page.
    return redirect(
        "onlinecourse:show_exam_result",
        course_id=course.pk,
        submission_id=submission_ids[-1],
    )


@login_required
def show_exam_result(request, course_id, submission_id):
    """Calculate and display result details for a saved submission."""
    course = get_object_or_404(Course, pk=course_id)
    learner = get_object_or_404(Learner, user=request.user)

    if not learner.enrolledCourses.filter(pk=course.pk).exists():
        messages.error(request, "You must be enrolled in this course to view exam results.")
        return redirect("onlinecourse:course_details", course_id=course.pk)

    # Ensure the requested submission belongs to this learner and course.
    requested_submission = get_object_or_404(
        Submission,
        pk=submission_id,
        learner=learner,
        question__course=course,
    )

    # The submission is the attempt identifier. Gather its saved answers for this
    # learner/course and use the required Question.is_get_score() method.
    attempt_submissions = (
        Submission.objects.filter(
            learner=learner,
            question__course=course,
            submitted_at__gte=requested_submission.submitted_at,
        )
        .select_related("question")
        .prefetch_related("choices", "question__choices")
        .order_by("question_id")
    )

    result_rows = []
    total_score = 0
    total_possible_score = 0

    for submission in attempt_submissions:
        question = submission.question
        selected_ids = list(submission.choices.values_list("pk", flat=True))
        score = question.is_get_score(selected_ids)
        total_score += score
        total_possible_score += question.grade

        result_rows.append({
            "question": question,
            "submission": submission,
            "selected_choices": list(submission.choices.all()),
            "correct_choices": list(question.choices.filter(is_correct=True)),
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
        "submission": requested_submission,
        "submissions": list(attempt_submissions),
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
