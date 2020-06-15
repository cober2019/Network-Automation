from setuptools import  setup, find_packages

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name="ACIOps",
    version="2.0.0",
    author="Chris Oberdalhoff",
    author_email="cober91130@gmail.com",
    description="ACIOps allows you to fetch basic ACI information.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cober2019/Network-Automation/tree/master/DataCenter%20(ACI)/ACIOperations",
    packages=find_packages(),
    py_modules=["ACIOPs"],
    install_requires=("ipaddress"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)