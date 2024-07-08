import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django_admin_page_api",
    version="1.0.6",
    author="Mateusz Zębala",
    author_email="mateusz.zebala.pl@gmail.com",
    description="Django Admin Page API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mateuszzebala/django-admin-page-api",
    packages=["django_admin_page_api"],
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    include_package_data=True,
    install_requires=["django"],
)
