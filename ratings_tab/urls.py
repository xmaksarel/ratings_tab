# -*- coding: utf-8 -*-


from django.conf.urls import url
from django.conf import settings
from .views import RatingsView

#        r'courses/{}/chat$'.format(

urlpatterns = (
    url(
            r'courses/{}/rating_grade$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        RatingsView.as_view(),
        name='ratings_view',
    ),
)
