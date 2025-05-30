from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="superb-ai-onprem",
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    author="Superb AI",
    author_email="support@superb-ai.com",
    description="Python SDK for Superb AI On-premise",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Superb-AI-Suite/superb-ai-onprem-python",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.22.0",  # Python 3.7 지원 시작 버전
        "urllib3>=1.21.1",  # Retry 기능 안정화 버전
        "pydantic>=1.8.0",  # Python 3.7 지원 안정 버전
    ],
) 