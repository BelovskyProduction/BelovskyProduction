import re

from typing import Any
from typing_extensions import Self
from pydantic import BaseModel, Field, ValidationError, field_validator, EmailStr, model_validator, \
    ModelWrapValidatorHandler
from pydantic_core import PydanticCustomError

import text
from service import AnswerTypes


error_messages = {
    'string_too_short': text.answer_min_length_error,
    'string_too_long': text.answer_max_length_error,
    'phone_pattern_mismatch': text.answer_phone_error,
    'email_pattern_mismatch': text.answer_email_error,
    'greater_than': text.answer_greater_than_error,
    'less_than': text.answer_less_than_error,
    'int_parsing': text.answer_int_parsing_error
}


class TextValidator(BaseModel):
    answer: str = Field(min_length=2, max_length=150)


class LargeTextValidator(TextValidator):
    answer: str = Field(min_length=4, max_length=450)


class PhoneValidator(BaseModel):
    answer: str

    @field_validator('answer')
    def validate_answer(cls, value):
        pattern = r'^\+?\d{10,14}$'
        if not re.match(pattern, value):
            raise PydanticCustomError(
                "phone_pattern_mismatch",
                "Phone {answer} doesn't match",
                {"answer": value},
            )
        return value


class EmailValidator(BaseModel):
    answer: EmailStr

    @model_validator(mode='wrap')
    def send_custom_validation_error_for_email(cls, data: Any, handler: ModelWrapValidatorHandler[Self]) -> Self:
        try:
            return handler(data)
        except ValidationError as e:
            raise PydanticCustomError(
                "email_pattern_mismatch",
                "Email {input} doesn't match pattern",
                e.errors()[0],
            )


class NumberValidator(BaseModel):
    answer: int = Field(gt=0, lt=100000)


class AgeValidator(BaseModel):
    answer: int = Field(gt=0, lt=120)


class AnswerValidator:
    validators = {
        AnswerTypes.email: EmailValidator,
        AnswerTypes.text: TextValidator,
        AnswerTypes.phone: PhoneValidator,
        AnswerTypes.number: NumberValidator,
        AnswerTypes.large_text: LargeTextValidator,
        AnswerTypes.age: AgeValidator
    }

    @classmethod
    def validate(cls, data, data_type):
        answer_validator = cls.validators.get(data_type, TextValidator)
        try:
            answer_validator(answer=data)
            return True, None
        except ValidationError as e:
            error_type = e.errors()[0].get('type', None)
            return False, error_messages.get(error_type, text.answer_default_message)


