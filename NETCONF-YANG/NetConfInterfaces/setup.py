from setuptools import setup, find_packages

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name="NETCONF-Interfaces", # Replace with your own username
    version="1.0.2",
    author="Chris Oberdalhoff",
    author_email="cober91130@gmail.com",
    description="Allows Network Engineer to view interfaces details",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cober2019/Network-Automation/tree/master/NETCONF-YANG/NetConfInterfaces",
    packages=find_packages(),
    py_modules=["NetConfInterfaces"],
    install_requires=("ipaddress", "ncclient", "xmltodict"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)