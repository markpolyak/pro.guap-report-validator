from setuptools import setup, find_packages

setup(
    name="report_validator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask",
        "python-docx",
        "python-dateutil",
        "flask-cors",
        "pytest"
    ],
)
