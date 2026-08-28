from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OX_ALPHA_API_KEY")

print("API key loaded:", bool(api_key))
print("API key length:", len(api_key) if api_key else 0)

client = OpenAI(
    api_key=api_key,
    base_url="https://oxalpha.run/api/v1"
)

response = client.chat.completions.create(
    model="ox-alpha",
    messages=[
        {
            "role": "user",
            "content": "Say hello."
        }
    ]
)

print(response.choices[0].message.content)