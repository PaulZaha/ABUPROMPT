from typing import Any, Dict, Iterable, Mapping, Union
import json

from openai import AzureOpenAI

from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_MODEL, AZURE_OPENAI_REASONING_EFFORT


def OpenAI_Call_Improvement(system_prompt: str, user_prompt: str):

    # define the client
    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
    )

    # call the OpenAI API
    response = client.chat.completions.create(
        model=AZURE_OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        reasoning_effort=AZURE_OPENAI_REASONING_EFFORT,
        response_format={"type": "json_object"},
    )

    print("Token usage:", response.usage)

    return response.choices[0].message.content
