from lms.djangoapps.grades.api import CourseGradeFactory
from lms.djangoapps.grades.course_data import CourseData
from lms.djangoapps.grades.api import context as grades_context

from django.urls import reverse
from lms.djangoapps.program_enrollments.api import get_external_key_by_user_and_course
from xmodule.util.misc import get_default_short_labeler
from openedx.core.lib.courses import get_course_by_id


def get_grades_for_student(course_key, grade_user):
    def _gradebook_entry(user, course, graded_subsections, course_grade):
        """
        Returns a dictionary of course- and subsection-level grade data for
        a given user in a given course.
        Args:
            user: A User object.
            course: A Course Descriptor object.
            graded_subsections: A list of graded subsections in the given course.
            course_grade: A CourseGrade object.
        """
        user_entry = _serialize_user_grade(user, course.id, course_grade)
        breakdown = _section_breakdown(course, graded_subsections, course_grade)

        user_entry['section_breakdown'] = breakdown
        user_entry['progress_page_url'] = reverse(
            'student_progress',
            kwargs=dict(course_id=str(course.id), student_id=user.id)
        )
        user_entry['user_id'] = user.id
        user_entry['full_name'] = user.profile.name

        external_user_key = get_external_key_by_user_and_course(user, course.id)
        if external_user_key:
            user_entry['external_user_key'] = external_user_key

        return user_entry

    def _section_breakdown(course, graded_subsections, course_grade):
        """
        Given a course_grade and a list of graded subsections for a given course,
        returns a list of grade data broken down by subsection.

        Args:
            course: A Course Descriptor object
            graded_subsections: A list of graded subsection objects in the given course.
            course_grade: A CourseGrade object.
        """
        breakdown = []
        default_labeler = get_default_short_labeler(course)

        for subsection in graded_subsections:
            subsection_grade = course_grade.subsection_grade(subsection.location)
            short_label = default_labeler(subsection_grade.format)

            attempted = False
            score_earned = 0
            score_possible = 0

            # For ZeroSubsectionGrades, we don't want to crawl the subsection's
            # subtree to find the problem scores specific to this user
            # (ZeroSubsectionGrade.attempted_graded is always False).
            # We've already fetched the whole course structure in a non-user-specific way
            # when creating `graded_subsections`.  Looking at the problem scores
            # specific to this user (the user in `course_grade.user`) would require
            # us to re-fetch the user-specific course structure from the modulestore,
            # which is a costly operation.  So we only drill into the `graded_total`
            # attribute if the user has attempted this graded subsection, or if there
            # has been a grade override applied.
            if subsection_grade.attempted_graded or subsection_grade.override:
                attempted = True
                score_earned = subsection_grade.graded_total.earned
                score_possible = subsection_grade.graded_total.possible

            # TODO: https://openedx.atlassian.net/browse/EDUCATOR-3559 -- Some fields should be renamed, others removed:
            # 'displayed_value' should maybe be 'description_percent'
            # 'grade_description' should be 'description_ratio'
            breakdown.append({
                'attempted': attempted,
                'category': subsection_grade.format,
                'label': short_label,
                'module_id': str(subsection_grade.location),
                'percent': subsection_grade.percent_graded,
                'score_earned': score_earned,
                'score_possible': score_possible,
                'subsection_name': subsection_grade.display_name,
            })
        return breakdown
    
    def _serialize_user_grade(user, course_key, course_grade):
        """
        Serialize a single grade to dict to use in Responses
        """
        return {
            'username': user.username,
            # per business requirements, email should only be visible for students in masters track only
            'email': user.email if getattr(user, 'enrollment_mode', '') == 'masters' else '',
            'course_id': str(course_key),
            'passed': course_grade.passed,
            'percent': course_grade.percent,
            'letter_grade': course_grade.letter_grade,
        }

    def calculate_ratings(grades, grading_info):
        grading_info_sorted = {}
        grades_sorted = {}

        for assignment in grading_info:
            grading_info_sorted[assignment['type']]=assignment
            grades_sorted[assignment['type']] = []

            if 'R1' in assignment['short_label']:
                grading_info_sorted[assignment['type']]['rating']='R1'
            elif 'R2' in assignment['short_label']:
                grading_info_sorted[assignment['type']]['rating']='R2'
            elif 'Exam' in assignment['short_label']:
                grading_info_sorted[assignment['type']]['rating']='Exam'

        for grades_subsection in grades['section_breakdown']:
            grades_sorted[grades_subsection['category']].append(grades_subsection['percent'])

        # Removes lowest grades if there is 'drop_count'
        for assignment_type in grades_sorted:
            grades_sorted[assignment_type].sort(reverse=True)
            for _ in range(grading_info_sorted[assignment_type]['drop_count']):
                grades_sorted[assignment_type].pop()


        ratings = {'R1':{'average':0,'weights_sum':0}, 'R2':{'average':0,'weights_sum':0}, 'Exam':{'average':0,'weights_sum':0}}
        for assignment_type in grades_sorted:
            rating = grading_info_sorted[assignment_type]['rating']
            weight = grading_info_sorted[assignment_type]['weight']
            ratings[rating]['weights_sum'] = ratings[rating]['weights_sum'] + weight

        for assignment_type in grades_sorted:
            rating = grading_info_sorted[assignment_type]['rating']
            if(len(grades_sorted[assignment_type]) != 0):
                average = sum(grades_sorted[assignment_type]) / len(grades_sorted[assignment_type])
                weight = grading_info_sorted[assignment_type]['weight']
                ratings[rating]['average'] = ratings[rating]['average'] + average * weight

        for rating in ratings:
            if(ratings[rating]['weights_sum'] != 0):
                ratings[rating] = round(ratings[rating]['average'] * 100 / ratings[rating]['weights_sum'])
            else:
                ratings[rating] = round(ratings[rating]['average'] * 100)

        # Makes exam grade a zero if student didn't passed ratings
        if(ratings['R1'] + ratings['R2'] < 100):
            ratings['Exam'] = 0
        return ratings

    course = get_course_by_id(course_key, depth=None)
    course_data = CourseData(user=None, course=course)
    graded_subsections = list(grades_context.graded_subsections_for_course(course_data.collected_structure))

    if grade_user:
        course_grade = CourseGradeFactory().read(
            grade_user,
            course,
            collected_block_structure=course_data.collected_structure
        )

        entry = _gradebook_entry(grade_user, course, graded_subsections, course_grade)
        ratings = calculate_ratings(entry, course.grading_policy['GRADER'])
        return ratings
