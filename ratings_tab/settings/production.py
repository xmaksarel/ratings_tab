# -*- coding: utf-8 -*-


def plugin_settings(settings):
    """
    Defines settings when app is used as a plugin to edx-platform.
    See: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.RATING_VAR = getattr(settings, 'ENV_TOKENS', {}).get(
        'RATING_VAR',
        settings.RATING_VAR
    )
