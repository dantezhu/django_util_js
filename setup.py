from setuptools import setup

setup(
    name="django_util_js",
    version='0.0.15',
    zip_safe=False,
    platforms='any',
    packages=['django_util_js'],
    install_requires=['django'],
    url="https://github.com/dantezhu/django_util_js",
    license="BSD",
    author="dantezhu",
    author_email="zny2008@gmail.com",
    description="django's util in javascript. such as url_for etc.",
    )
