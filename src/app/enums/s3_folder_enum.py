from enum import Enum

class S3Folder(str, Enum):
    # 게시판, 썸네일
    POST = "post"
    PROFILE = "profile"


