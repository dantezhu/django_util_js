from setuptools import setup
import django_util_js

setup(
    name="django_util_js",
    version=django_util_js.__version__,
    zip_safe=False,
    platforms='any',
    packages=['django_util_js'],
    url="https://github.com/dantezhu/django_util_js",
    license="BSD",
    author="dantezhu",
    author_email="zny2008@gmail.com",
    description="django's util in javascript. such as url_for etc.",
    )
