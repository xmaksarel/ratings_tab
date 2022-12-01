# -*- coding: utf-8 -*-


from django.conf import settings
from django.utils.translation import ugettext_noop

from lms.djangoapps.courseware.tabs import EnrolledTab
from xmodule.tabs import TabFragmentViewMixin

class RatingsTab(TabFragmentViewMixin, EnrolledTab):
    type = 'ratings_tab'
    title = ugettext_noop('Рейтинговые оценки')
    priority = None
    view_name = 'ratings_view'
    is_hideable = True
    # is_default = True
    # body_class = 'rocketchat'
    # online_help_token = 'rocketchat'
    # True if this tab should be displayed only for instructors
    # course_staff_only = True

    @classmethod
    def is_enabled(cls, course, user=None):
        """
        Returns true if the specified user has staff access.
        """
        return True
       
