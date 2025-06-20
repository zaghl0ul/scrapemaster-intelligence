#!/usr/bin/env python3
"""
Setup script for ScrapeMaster Intelligence Platform
"""

from setuptools import setup, find_packages
import os
import re

# Read the README file
def read_readme():
    """Read README.md file."""
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements from requirements.txt
def read_requirements():
    """Read requirements from requirements.txt file."""
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Get version from __init__.py
def get_version():
    """Get version from src/core/__init__.py."""
    init_file = os.path.join("src", "core", "__init__.py")
    with open(init_file, "r", encoding="utf-8") as fh:
        content = fh.read()
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", content, re.M)
        if version_match:
            return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

# Project metadata
PROJECT_NAME = "scrapemaster-intelligence"
PROJECT_DESCRIPTION = "Enterprise-Grade Web Scraping SaaS Platform"
PROJECT_LONG_DESCRIPTION = read_readme()
PROJECT_URL = "https://github.com/yourusername/scrapemaster-intelligence"
PROJECT_AUTHOR = "ScrapeMaster Team"
PROJECT_AUTHOR_EMAIL = "team@scrapemaster.com"
PROJECT_LICENSE = "MIT"
PROJECT_CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: Information Technology",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Text Processing :: Markup :: HTML",
    "Topic :: Internet :: WWW/HTTP :: Browsers",
    "Topic :: Scientific/Engineering :: Information Analysis",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
    "Framework :: Streamlit",
    "Environment :: Web Environment",
    "Natural Language :: English",
]

# Project keywords
PROJECT_KEYWORDS = [
    "web-scraping",
    "data-extraction",
    "automation",
    "saas",
    "streamlit",
    "beautifulsoup",
    "proxy",
    "stealth",
    "enterprise",
    "dashboard",
    "monitoring",
    "analytics",
    "client-management",
    "revenue-tracking",
]

# Setup configuration
setup(
    name=PROJECT_NAME,
    version=get_version(),
    author=PROJECT_AUTHOR,
    author_email=PROJECT_AUTHOR_EMAIL,
    description=PROJECT_DESCRIPTION,
    long_description=PROJECT_LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url=PROJECT_URL,
    project_urls={
        "Bug Reports": f"{PROJECT_URL}/issues",
        "Source": PROJECT_URL,
        "Documentation": f"{PROJECT_URL}/blob/main/README.md",
        "Changelog": f"{PROJECT_URL}/blob/main/CHANGELOG.md",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=PROJECT_CLASSIFIERS,
    keywords=PROJECT_KEYWORDS,
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "pre-commit>=3.3.0",
        ],
        "test": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "pytest-asyncio>=0.21.0",
            "responses>=0.23.0",
            "freezegun>=1.2.0",
        ],
        "docs": [
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
            "myst-parser>=2.0.0",
        ],
        "production": [
            "gunicorn>=21.2.0",
            "psycopg2-binary>=2.9.7",
            "redis>=4.6.0",
            "celery>=5.3.0",
            "sentry-sdk>=1.39.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "scrapemaster=src.app:main",
            "scrapemaster-cli=src.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "scrapemaster": [
            "config/*.json",
            "config/*.yaml",
            "config/*.yml",
            "templates/*.html",
            "static/*",
        ],
    },
    data_files=[
        ("config", [
            "config/env.example",
            "config/production_proxies.json.example",
        ]),
        ("scripts", [
            "start.sh",
            "start_scrapemaster.bat",
            "start_scrapemaster.ps1",
        ]),
        ("docs", [
            "README.md",
            "CONTRIBUTING.md",
            "CHANGELOG.md",
            "LICENSE",
        ]),
    ],
    zip_safe=False,
    license=PROJECT_LICENSE,
    platforms=["any"],
    maintainer=PROJECT_AUTHOR,
    maintainer_email=PROJECT_AUTHOR_EMAIL,
    download_url=f"{PROJECT_URL}/archive/refs/tags/v{get_version()}.tar.gz",
    provides=["scrapemaster"],
    requires_python=">=3.8",
    setup_requires=[
        "setuptools>=45",
        "wheel",
    ],
    test_suite="tests",
    tests_require=[
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0",
    ],
    options={
        "bdist_wheel": {
            "universal": True,
        },
    },
) 