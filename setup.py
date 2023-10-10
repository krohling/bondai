from setuptools import setup, find_packages

# If you have a requirements.txt, you can read it to set the install_requires parameter.
with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name="bondai",
    use_scm_version=True,
    description="An AI-powered console assistant with a versatile API for seamless integration into applications.",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    author="Kevin Rohling",
    author_email="kevin@kevinrohling.com",
    url="https://bondai.dev",
    packages=find_packages(),  # This will include all packages under the bondai directory
    # scripts=['scripts/bondai'],
    entry_points={
        'console_scripts': [
            'bondai=bondai.main:main',
        ],
    },
    install_requires=requirements,
    include_package_data=True,
    setup_requires=['setuptools_scm'],  # Add this line
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
)
