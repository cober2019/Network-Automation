from setuptools import  setup, find_packages

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name="Prefix-list_Ops",
    version="1.0.0",
    author="Chris Oberdalhoff",
    author_email="cober91130@gmail.com",
    description="Perform operations on network prefix-list",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cober2019/Network-Automation/tree/master/NETCONF-YANG/Prefix-List_Ops",
    packages=find_packages(),
    py_modules=["isr-lists", "asr-lists"],
    install_requires=("ipaddress", "ncclient", "xmltodict", "netmiko"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)