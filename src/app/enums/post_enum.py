from enum import Enum

class PostSortEnum(str, Enum):
    LATEST = "LATEST" # 최신순
    OLDEST = "OLDEST" # 오래된순
    VIEWS = "VIEWS" # 조회순

class PostSearchEnum(str, Enum):
    TITLE = "TITLE" # 제목
    CONTENT = "CONTENT" # 내용
    WRITER = "WRITER" # 작성자
    TITLE_CONTENT = "WRITER_CONTENT" # 제목 + 내용
