# scripts/chat_module.py
import os
from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

import tiktoken
from scripts.memory_core_module import handle_memory_core_commands
from scripts.chat_utils import summarize_history, inject_long_term_memory

def handle_chat_interaction(user_input, conversation_history, config, log_file):
    # Add user's message
    conversation_history.append(("User", str(user_input)))

    # Summarize if buffer is full
    if len(conversation_history) == conversation_history.maxlen:
        old = [f"{str(s)}: {str(m)}" for s, m in list(conversation_history)[:5]]
        summary = summarize_history(old)
        for _ in range(5): conversation_history.popleft()
        conversation_history.append(("System", summary))

    # Token Management: Trim history to stay under token budget
    def estimate_tokens(text):
        enc = tiktoken.encoding_for_model("gpt-4")
        return len(enc.encode(text))

    token_limit = 7500
    while True:
        history_text = "\n".join([f"{str(s)}: {str(m)}" for s, m in conversation_history])
        if estimate_tokens(history_text) < token_limit:
            break
        # Remove the oldest non-system message
        for i in range(len(conversation_history)):
            if conversation_history[i][0] != "System":
                conversation_history.remove(conversation_history[i])
                break

    # Prepare history context
    history = "\n".join([f"{str(s)}: {str(m)}" for s, m in conversation_history])
    if "earlier you said" in user_input.lower():
        memory = inject_long_term_memory("verity", user_input)
        history += "\nMemory Recall:\n" + str(memory)

    # Send to memory core (replaced with OpenAI call)
    from scripts.memory_core import get_combined_context
    import openai

    # Prepare context
    context = get_combined_context(user_input)
    full_prompt = f"Context:\n{context}\n\nUser: {user_input}\nVerity:"

    print(f"🧠 Full prompt to OpenAI:\n{full_prompt}")

    # Get response from OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are Verity, an intelligent and loyal AI advisor."},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )
    result = response.choices[0].message["content"]

    # Save response
    if not result:
        print("⚠️ Verity memory core returned None or empty result.")
        fallback = "🤖 I'm not sure what to say yet. Try rephrasing."
        conversation_history.append(("Verity", fallback))
        return fallback.strip()

    conversation_history.append(("Verity", str(result)))
    cleaned = str(result).strip()
    if "[💡 Tip:" in cleaned:
        print("💡 Tip detected in response. Full message preserved.")
    return cleaned