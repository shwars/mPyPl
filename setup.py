#!/usr/bin/env python

import setuptools
import mPyPl

with open('README.md') as readme_file:
    readme = readme_file.read()
    
setuptools.setup(
    name='mPyPl',
    packages=setuptools.find_packages(),
    version=mPyPl.__version__,
    install_requires=['pipe>=1.5.0','numpy>=1.11','opencv-python','matplotlib'],
    description='Monadic Pipeline Library for Python',
    author='Dmitri Soshnikov',
    author_email='dmitri@soshnikov.com',
    url='https://github.com/shwars/mPyPl',
#    download_url='https://github.com/JulienPalard/Pipe/tarball/master',
    long_description=readme,
    long_description_content_type='text/markdown; charset=UTF-8',
    license='MIT license',
    classifiers=[
        "Programming Language :: Python :: 3",
#        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)