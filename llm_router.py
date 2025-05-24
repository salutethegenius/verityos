import os
import openai

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

def query_model(prompt: str) -> str:
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"🔥 OpenAI error: {str(e)}"