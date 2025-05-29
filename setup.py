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
        "requests>=2.25.0",  # HTTP 클라이언트
        "urllib3>=1.26.0",  # requests의 의존성이지만 Retry 로직을 위해 명시
        "pydantic>=2.0.0",  # 데이터 검증 및 직렬화
        "configparser>=5.0.0",  # 설정 파일 파싱
    ],
) 