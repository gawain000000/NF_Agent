from typing import List


def update_system_prompt(messages, system_prompt):
    """
    Update the system prompt in the messages list.

    Args:
        messages (list): A list of dictionaries representing the message history.
                         It may start with a system message or just a user message.
        file_path (str): Path to the file containing the new system prompt.

    Returns:
        list: The updated messages list.
    """
    # Check if the first message is a system message
    if messages and messages[0].get("role") == "system":
        messages[0]["content"] = system_prompt  # Update the system message content
    else:
        # Insert a new system message at the beginning of the list
        messages.insert(0, {"role": "system", "content": system_prompt})

    return messages


async def restrict_to_json_format(llm_client, llm_settings, messages: List[dict]):
    messages.append({
        "role": "user",
        "content": (
            "Please ensure that your output is a valid JSON format. "
            "Your response must contain only JSON, and no additional text or commentary."
        )
    })
    response = await llm_client.chat.completions.create(
        model=llm_settings.CHAT_LLM_MODEL,
        messages=messages,
        stream=False,
        temperature=llm_settings.temperature,
        top_p=llm_settings.top_p
    )
    return response
