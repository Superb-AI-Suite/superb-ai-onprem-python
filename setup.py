from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="superb-ai-onprem",
    version="0.1.0",
    author="Superb AI",
    author_email="",  # Add appropriate email
    description="Superb AI On-premise SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Superb-AI-Suite/superb-ai-onprem-python",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        # Add your dependencies here
    ],
) 