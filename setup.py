import imp
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


here = os.path.abspath(os.path.dirname(__file__))

try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
except Exception:
    README = ''
    CHANGES = ''

# Use imp to avoid sift/__init__.py
version_mod = imp.load_source('__tmp', os.path.join(here, 'sift/version.py'))

setup(
    name='Sift',
    description='Python bindings for Sift Science\'s API',
    version=version_mod.VERSION,
    url='https://siftscience.com',

    author='Sift Science',
    author_email='support@siftscience.com',
    long_description=README + '\n\n' + CHANGES,

    packages=['sift'],
    install_requires=[
        "requests >= 0.14.1",
    ],
    extras_require={
        'test': [
            'mock >= 1.0.1',
        ],
    },

    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
