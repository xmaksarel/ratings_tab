# -*- coding: utf-8 -*-

from lms.djangoapps.courseware.courses import get_course_with_access
from django.template.loader import render_to_string
from web_fragments.fragment import Fragment
from openedx.core.djangoapps.plugin_api.views import EdxFragmentView
from opaque_keys.edx.keys import CourseKey
from lms.djangoapps.courseware.access import has_access
from common.djangoapps.student.models import CourseEnrollment
from django.contrib.auth.models import AnonymousUser
from .grades import get_grades_for_student
from django.db.models import Q

def get_course_enrolled_users(course_key):
    queryset = CourseEnrollment.objects

    filter_args = [
        Q(course_id=course_key) & Q(is_active=True)
    ]
    queryset = queryset.filter(*filter_args)
    users = []
    for query in queryset:
        users.append(query.user)
    return users

class RatingsView(EdxFragmentView):
    def render_to_fragment(self, request, course_id, **kwargs):

        course_key = CourseKey.from_string(course_id)
        course = get_course_with_access(request.user, "load", course_key)
        user = request.user
        display_name_course = course.display_name

        staff_access = bool(has_access(request.user, 'staff', course))
        user_is_enrolled = CourseEnrollment.is_enrolled(user, course.id)

        # Check for AnonymousUser user
        if (isinstance(user, AnonymousUser)):
            user_email = ""
            user_display_name = ""
        else:
            profile = user.profile
            user_email = user.email
            user_display_name = profile.name
            # Additional profile fields
            # https://github.com/openedx/edx-platform/blob/master/common/djangoapps/student/models.py

        ratings = None
        if staff_access:
            students = get_course_enrolled_users(course_key)
            ratings = []
            i = 1
            for student in students:
                grades = {'№': i, 'Username' :student.username}
                grades.update(get_grades_for_student(course_key, student))
                ratings.append(grades)
                i = i + 1
        elif user_is_enrolled:
            grades = {'№': 1, 'Username' :user.username}
            grades.update(get_grades_for_student(course_key, user))
            ratings = [grades]
        # For ratings_tab.html
        context = {
            "course": course,           # must in the root level to avoid "proctored exam error"
            "user_info": {
                "username": user.username,
                "email": user_email,
                "display_name": user_display_name,
                "is_staff": staff_access,
                "is_enrolled": user_is_enrolled,
            },
            "course_info": {
                "course": course,
                "name": display_name_course,
                "key": course_key,
            },
            "ratings": ratings
        }

        html = render_to_string(
            'ratings_tab/ratings_tab.html', context, )
        fragment = Fragment(html)

        return fragment
    