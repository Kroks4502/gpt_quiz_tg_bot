from pydantic import Field, constr, field_validator, BaseModel
from pydantic_core.core_schema import ValidationInfo


class QuizQuestion(BaseModel):
    title: str = Field(min_length=1, max_length=2000, description='Unique and clear quiz question, maximum of 300 characters.')
    answers: list[constr(min_length=1, max_length=100)] = Field(max_length=9, description="Options, option maximum of 100 characters, maximum 9 options.")
    correct_answer: int = Field(ge=0, le=9, description='Correct answer.')
    solution: str | None = Field(None, min_length=1, max_length=200, description='Optional brief explanation of the correct answer, maximum of 200 characters.')

    @field_validator("correct_answer")
    def interest_not_empty(cls, v: int, info: ValidationInfo):
        answers = info.data.get("answers")
        if answers and v >= len(answers):
            raise ValueError("The answer must be less than the number of answers")
        return v


class QuizQuestionGpt(BaseModel):
    title: str = Field(description='Unique and clear quiz question, maximum of 300 characters.')
    answers: list[str] = Field(description="Options, option maximum of 100 characters, maximum 9 options.")
    correct_answer: int = Field(description='Correct answer.')
    solution: str | None = Field(None, description='Optional brief explanation of the correct answer, maximum of 200 characters.')


class UserAnswer(BaseModel):
    question: str
    correct: bool = Field(description='Correct answer.')


if __name__ == "__main__":
    # Схема для https://platform.openai.com/playground/
    import json
    from openai.lib._parsing import type_to_response_format_param
    print(json.dumps(type_to_response_format_param(QuizQuestionGpt)["json_schema"]))
