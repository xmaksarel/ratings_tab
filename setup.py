# -*- coding: utf-8 -*-


import setuptools

setuptools.setup(
    name="ratings-tab",
    version="0.1.0",
    author="Maxim Tsov",
    license="MIT",
    author_email="mtsov@edu.ektu.kz",
    description="ratings_tab Open edX course_tab",
    long_description="Shows student rating grade in a new tab.",
    url="https://github.com/xmaksarel/ratings_tab",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Platform :: Open edX",
        "Natural Language :: English",
        "Environment :: Web Environment",
    ],
    entry_points={
        "lms.djangoapp": [
            "ratings_tab = ratings_tab.apps:RatingsTabConfig",
        ],
        "openedx.course_tab": [
            "ratings_tab = ratings_tab.plugins:RatingsTab",
        ]
    },
)
