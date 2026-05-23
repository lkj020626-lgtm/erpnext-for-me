from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="starmake",
    version="0.1.0",
    description="StarMake - Lightweight ERP for small manufacturers",
    author="StarMake",
    author_email="dev@starmake.local",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
