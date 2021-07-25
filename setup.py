from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="pykanka",
    version="0.1.0",
    description="A wrapper for the kanka.io API, currently providing basic get/patch/post functionality for most entity classes",
    author="Spectre",
    packages=["pykanka"],
    install_requires=["requests", "tenacity"]
)
