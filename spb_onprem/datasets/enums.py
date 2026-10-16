from enum import Enum


class DatasetType(str, Enum):
    """
    데이터셋 종류

    서버 GraphQL enum `DatasetType` 과 같다.
    값이 없으면(None) 기존 Computer Vision 데이터셋이다.
    데이터셋을 만들 때만 정할 수 있고 이후에는 바꿀 수 없다.
    """
    VLM = "VLM"
