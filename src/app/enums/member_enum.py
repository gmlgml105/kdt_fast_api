from enum import Enum

class MemberProvider(str, Enum):
    LOCAL = "LOCAL"
    GOOGLE = "GOOGLE"
    KAKAO = "KAKAO"
    NAVER = "NAVER"