from config import (user_data, MAX_TOKENS_IN_SESSION, TEMPERATURE, MAX_TOKENS, FOLDER_ID, URL, HEADERS, SYSTEM_PROMPT,
                    END_STORY, logger)

import requests


def ask_gpt(user_id, user_prompt, assistant_prompt):
    data = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": TEMPERATURE,
            "maxTokens": MAX_TOKENS
        },
        "messages": [
            {'role': 'user', 'text': user_prompt},
            {'role': 'sistem', 'text': SYSTEM_PROMPT},
            {'role': 'assistant', 'text': assistant_prompt}
        ]
    }

    try:
        response = requests.post(url=URL, headers=HEADERS, json=data)
        if response.status_code != 200:
            logger.debug(f'wrong response from API, code {response.status_code}')
            return f'Ошибка! Код {response.status_code}'

        if not response.json().get('result'):
            logger.debug(f'wrong response from API, code {response.status_code}')
            return f'Ошибка при выдаче ответа! Код {response.status_code}'

        tokens = len(
            requests.post(
                "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenizeCompletion", json=data,
                headers=HEADERS).json()["tokens"])
        if tokens > MAX_TOKENS_IN_SESSION:
            return ('Потрачено максимальное количество токенов для данной истории!\n'
                    ' Введите /make_prompt для создания новой!')

        result = response.json()['result']['alternatives'][0]['message']['text']

        if user_prompt == END_STORY:
            del user_data[user_id]['messages']
        else:
            data['messages'][2]['text'] += result
            if not user_data[user_id].get('messages'):
                user_data[user_id]['messages'] = []
            user_data[user_id]['messages'].append(data['messages'])

    except Exception as e:
        logger.error(f'An unexpected error occured: {e}')
        result = "Произошла непредвиденная ошибка. Подробности см. в журнале."

    return result
