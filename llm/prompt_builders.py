import os
from abc import ABC, abstractmethod

from config import CONCEPTION_CONTENT


class ConceptionPromptBuilder(ABC):

    def __init__(self):
        self.model = os.getenv('LLM_MODEL')
        self.response_format = {'type': 'json_object'}

    @abstractmethod
    def build_prompt(self, survey_answers: dict) -> dict:
        pass

    def __get_base_prompt(self) -> dict:
        return {'model': self.model, 'response_format': self.response_format}

    def construct_prompt(self, content: str):
        prompt = self.__get_base_prompt()
        messages = [{'role': "system", "content": "You are a helpful assistant. You response in JSON format"},
                    {'role': 'user', "content": content}]
        prompt.update({'messages': messages})
        return prompt


class EventPromptBuilder(ConceptionPromptBuilder):

    def __init__(self, event_type: str):
        self.event_type = event_type
        super().__init__()

    def build_prompt(self, survey_answers: dict) -> dict:
        user_content = f"Сгенерируй концепцию для мероприятия типа: '{self.event_type}' на основе следующих ответов: {survey_answers}. " \
                       f"Ответ должен содержать только следующие пункты: {CONCEPTION_CONTENT.get(self.event_type)}. " \
                       f"Значение пунктов должно быть в виде текста"
        return self.construct_prompt(user_content)


class AdvertisingPromptBuilder(ConceptionPromptBuilder):

    def build_prompt(self, survey_answers: dict) -> dict:
        user_content = f"Сгенерируй рекламный видеоролик на основе следующих ответов: {survey_answers}. " \
                       f"Распиши его по пунктам."
        return self.construct_prompt(user_content)
