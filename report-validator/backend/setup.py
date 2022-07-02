from socket import SO_RCVLOWAT
from setuptools import setup

setup(
    name='pro.guap-reports-validator-backend',
    version='0.0.1',
    author='Krutov A.V. 4936',
    author_email='madrid211514@gmail.com',
    description='backend for checking reports',
    scripts=['api/main.py'],
    python_requires='>=3.9.13',
    install_requires=[
        'fastapi==0.78.0',
        'uvicorn==0.18.1',
        'pytest==7.1.2',
        'requests==2.28.0',
        'python-multipart==0.0.5',
        'slowapi'
    ]
)
