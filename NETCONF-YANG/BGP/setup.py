from setuptools import setup, find_packages

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name="NETCONF BGP",
    version="1.0.0",
    author="Chris Oberdalhoff",
    author_email="cober91130@gmail.com",
    description="View and create BGP configurations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cober2019/Network-Automation/tree/master/NETCONF-YANG/BGP",
    packages=find_packages(),
    install_requires=("ncclient", "xmltodict"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6')