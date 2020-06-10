from setuptools import  setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="IpRanges", # Replace with your own username
    version="1.0.0",
    author="Chris Oberdalhoff",
    author_email="cober91130@gmail.com",
    description="Converts strings of IP addresses/Ranges to list",
    long_description="IpRanges was designed for Network Engineer to quickly unpack IP ranges. The intention is to avoid spreadsheets, and other methods of IP importing"    ,
    long_description_content_type="text/markdown",
    url="https://github.com/cober2019/Network-Automation/tree/master/IpRanges",
    packages=find_packages(),
    py_modules=["IpRanges"],
    install_requires=("ipaddress"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)