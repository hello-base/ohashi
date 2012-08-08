#/usr/bin/env python
import os
import sys

from setuptools import setup, find_packages


if 'publish' in sys.argv:
    os.system('python setup.py sdist upload')
    sys.exit()

# Dynamically calculate the version based on ohashi.VERSION.
version = __import__('ohashi').get_version()

setup(
    name='ohashi',
    version=version,
    description='Yet another opinionated utilities kit for Django projects.',
    author='Bryan Veloso',
    author_email='bryan@revyver.com',
    license='BSD',
    url='http://github.com/revyver/ohashi',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'django>=1.4'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities'
    ]
)
