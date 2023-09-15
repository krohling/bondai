from setuptools import setup, find_packages

# If you have a requirements.txt, you can read it to set the install_requires parameter.
with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name="bondai",
    version="0.2.10",
    description="An AI-powered console assistant with a versatile API for seamless integration into applications.",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    author="Kevin Rohling",
    author_email="kevin@kevinrohling.com",
    url="https://github.com/krohling/bondai",
    packages=find_packages(),  # This will include all packages under the bondai directory
    scripts=['scripts/bondai'],
    install_requires=requirements,
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
)
