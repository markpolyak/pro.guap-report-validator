from setuptools import setup

setup(
   name='report-checker',
   version='1.0',
   description='A useful module',
   author='Van Huan',
   author_email='foomail@foo.example',
   packages=['report-checker'],
   install_requires=['wheel', 'bar', 'greek'], #external packages as dependencies
)