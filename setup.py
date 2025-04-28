
from setuptools import setup, find_packages

setup(
    name="clapikit",
    version="0.1.0",
    description="CLI tool for OpenAPI specifications",
    author="youyo",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0",
        "requests>=2.0.0",
        "pydantic>=2.0.0",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "clapikit=clapikit.cli:main",
        ],
    },
)
