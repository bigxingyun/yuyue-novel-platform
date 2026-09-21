"""评论 Schema。"""



from pydantic import BaseModel, Field





class CommentOut(BaseModel):

    id: int

    user: str

    user_id: int

    avatar: str = ""

    level: int = 1

    title: str = "门外读者"

    content: str

    is_pinned: bool = False

    parent_id: int | None = None

    replies: list["CommentOut"] = []





class ParagraphCommentQuery(BaseModel):

    chapter_id: int

    paragraph_index: int





class CreateParagraphCommentRequest(BaseModel):

    chapter_id: int

    paragraph_index: int = Field(ge=0)

    content: str = Field(min_length=1, max_length=500)

    parent_id: int | None = Field(default=None, ge=1)





class CreateChapterCommentRequest(BaseModel):

    chapter_id: int

    content: str = Field(min_length=1, max_length=500)

    parent_id: int | None = Field(default=None, ge=1)





class CreateBookCommentRequest(BaseModel):

    content: str = Field(min_length=1, max_length=500)

    parent_id: int | None = Field(default=None, ge=1)


CommentOut.model_rebuild()

