from openai import OpenAI

from core.config import agent_settings, chat_llm_settings

agent_url = "http://192.168.1.6:19000/api/v1/agent/nf_agent"

prompt = "What is the current status of the planning application on New Brent Street?"
messages = [
    {"role": "user", "content": prompt}
]

client = OpenAI(base_url=agent_url,
                     api_key="aaa"
                     )

stream = True

response = client.chat.completions.create(model="some_model",
                                          messages=messages,
                                          stream=stream,
                                          top_p=0.6,
                                          temperature=0.1,
                                          max_tokens=8192,
                                          )
if stream:
    for chunk in response:
        print(chunk.choices[0].delta.content or "", end="", flush=True)
else:
    print(f"{response.choices[0].message.content}")