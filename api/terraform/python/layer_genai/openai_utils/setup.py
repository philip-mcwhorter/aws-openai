# -*- coding: utf-8 -*-
"""Setup for openai_utils package."""
from setuptools import setup, find_packages

from setup_utils import get_semantic_version

setup(
    name="openai_utils",
    version=get_semantic_version(),
    description="Common utilities for OpenAI",
    author="Lawrence McDaniel",
    author_email="lpm0073@gmail.com",
    packages=find_packages(),
    package_data={
        "openai_utils": ["*.md", "data/*"],
    },
    install_requires=["openai>=0.28"],
)
