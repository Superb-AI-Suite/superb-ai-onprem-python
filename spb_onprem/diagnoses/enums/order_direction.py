from enum import Enum


class OrderDirection(str, Enum):
    """정렬 방향"""
    ASC = "ASC"
    DESC = "DESC"
