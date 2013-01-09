import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


here = os.path.abspath(os.path.dirname(__file__))

try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
except:
    README = ''
    CHANGES = ''


setup(
    name='Sift',
    description='Python bindings for Sift Science\'s REST event API',
    version='0.1.0',
    url='https://siftscience.com',

    author='Sift Science',
    author_email='support@siftscience.com',
    long_description=README + '\n\n' + CHANGES,

    packages=['sift'],
    install_requires=[
        "requests >= 0.14.1",
    ],
)
