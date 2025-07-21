import asyncio
import functools
import os
import logging

from openai import AsyncOpenAI, OpenAIError
from .prompt_builders import ConceptionPromptBuilder

logger = logging.getLogger()


@functools.lru_cache(maxsize=1)
def get_open_ai_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=os.getenv('OPEN_AI_TOKEN'), base_url=os.getenv('BASE_AI_URL'), max_retries=0)


async def get_conception(prompt_builder: ConceptionPromptBuilder, survey_answers, retries):
    delay_in_seconds = int(os.getenv('RETRY_DELAY_MINUTES', 2)) * 60
    while retries > 0:
        try:
            return await create_completion(prompt_builder, survey_answers)
        except OpenAIError as e:
            logger.error('Conception generation error: %s', e.args)
            await asyncio.sleep(delay_in_seconds)
            retries -= 1


async def create_completion(prompt_builder, survey_answers):
    gpt_client = get_open_ai_client()
    prompt = prompt_builder.build_prompt(survey_answers)
    completion = await gpt_client.chat.completions.create(**prompt)
    return completion.choices[0].message.content

