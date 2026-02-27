from openai import AzureOpenAI

from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_MODEL, AZURE_OPENAI_REASONING_EFFORT


def OpenAI_Call_Durations(prompt):

    # define the client
    client = AzureOpenAI(
        azure_endpoint = AZURE_OPENAI_ENDPOINT, 
        api_key=AZURE_OPENAI_API_KEY,  
        api_version=AZURE_OPENAI_API_VERSION
    )

    # call the OpenAI API
    chat_completion = client.chat.completions.create(
        model = AZURE_OPENAI_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        reasoning_effort=AZURE_OPENAI_REASONING_EFFORT,
        response_format={"type": "json_object"},
    )
    return chat_completion.choices[0].message.content
