#!/usr/bin/env python3

import re
import time
import os
import json
import ast
import operator
import requests
from datetime import datetime

# -------------------------------
# ASCII Banner
# -------------------------------
banner = r"""
                             xxxxxx
                            +xxxxxx++               +++++xxxx+
                            x+xxxxxxx+           ++xxxxxxxxxxx+x
                             x+xxxxx+xx+xx   x+++xxxxxxxxxxxxxxxxx
                               x++       xxxxxxxxxxxxxxxxxxxxxxxx+
                                            xxxxxxxxxxxxxxxxxxxxxxx
                                             x+xxxxxxxxxxxxxxxxxxx+
                                              +xxxxxxxxxxxxxxxxxxx+
                                               xxxxxxxxxxxxxxxxxxx
                                                +xxxxxxxxxxxxxxx++
                                                  xxxxxxxxxxx+xx
                                                     xxxxxxx

                                                     VEO-GPTx
"""

print(banner)

# -------------------------------
# CONFIG
# -------------------------------

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "gemma:2b"
MEMORY_DIR = os.path.expanduser("~/VEO-GPTx/Memory")
MEMORY_FILE = os.path.join(MEMORY_DIR, "veo_memory.json")

# -------------------------------
# MEMORY
# -------------------------------

os.makedirs(MEMORY_DIR, exist_ok=True)

if os.path.exists(MEMORY_FILE):
    try:
        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)
    except:
        memory = []
else:
    memory = []

def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

# -------------------------------
# UTILITIES
# -------------------------------

def normalize(text):
    return re.sub(r"[^\w\s]", "", text.lower())

def type_out(text, delay=0.01):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()

# -------------------------------
# SAFE MATH
# -------------------------------

SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}

def safe_eval(expr):
    def eval_node(node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            return SAFE_OPERATORS[type(node.op)](
                eval_node(node.left),
                eval_node(node.right),
            )
        elif isinstance(node, ast.UnaryOp):
            return SAFE_OPERATORS[type(node.op)](
                eval_node(node.operand)
            )
        else:
            raise ValueError("Unsafe expression")

    tree = ast.parse(expr, mode="eval")
    return eval_node(tree.body)

# -------------------------------
# OLLAMA CHECK
# -------------------------------

def ollama_available():
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        return r.status_code == 200
    except:
        return False

# -------------------------------
# OLLAMA BRAIN
# -------------------------------

def ask_ollama(prompt):

    if not ollama_available():
        return None

    try:
        conversation = ""
        for mem in memory[-3:]:
            conversation += f"User: {mem['user']}\nAssistant: {mem['assistant']}\n"

        full_prompt = f"""You are VEO-GPT, a helpful and conversational AI assistant.
Respond naturally and directly.

{conversation}
User: {prompt}
Assistant:"""

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": full_prompt,
            "stream": True,
            "options": {
                "temperature": 0.6,
                "top_p": 0.9,
                "repeat_penalty": 1.1
            }
        }

        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            stream=True,
            timeout=120,
        )

        response.raise_for_status()

        full_reply = ""
        print("VEO-GPT: ", end="", flush=True)

        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode())
                chunk = data.get("response", "")
                print(chunk, end="", flush=True)
                full_reply += chunk

        print("\n")
        return full_reply.strip()

    except:
        print("\n[Ollama Error]\n")
        return None

# -------------------------------
# OFFLINE BRAIN
# -------------------------------

def offline_brain(user_input):

    user = normalize(user_input)

    if re.fullmatch(r"[0-9\.\+\-\*\/\(\) ]+", user):
        try:
            result = safe_eval(user)
            return f"The result is {result}."
        except:
            return "Math error."

    elif "time" in user:
        return f"The time is {datetime.now().strftime('%H:%M:%S')}."

    elif "date" in user:
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."

    elif user in ["hi", "hello", "hey"]:
        return "Hey there."

    else:
        return "Offline mode active."

# -------------------------------
# ROUTER
# -------------------------------

def process_input(user_input):

    reply = ask_ollama(user_input)

    if reply:
        memory.append({"user": user_input, "assistant": reply})
        save_memory()
        return None

    reply = offline_brain(user_input)
    memory.append({"user": user_input, "assistant": reply})
    save_memory()
    return reply

# -------------------------------
# STARTUP STATUS
# -------------------------------

current_date = datetime.now().strftime('%A, %B %d, %Y')
print(
    f"{'Ollama Connected' if ollama_available() else 'Offline Mode'} | "
    f"Model: {OLLAMA_MODEL}\n"
    f"Memory Loaded | {current_date}\n"
)

# -------------------------------
# MAIN LOOP
# -------------------------------

start_time = time.time()

while True:
    user_input = input("You: ").strip()

    if user_input.lower() in ["exit", "quit", "bye"]:
        print("VEO-GPT: Goodbye.")
        break

    if user_input.startswith("/status"):
        uptime = int(time.time() - start_time)
        brain = "Gemma 2B (Ollama)" if ollama_available() else "Offline Brain"
        print(f"VEO-GPT: Brain: {brain} | Model: {OLLAMA_MODEL} | Uptime: {uptime}s")
        continue

    if user_input.startswith("/model"):
        parts = user_input.split()
        if len(parts) > 1:
            OLLAMA_MODEL = parts[1]
            print(f"Model switched to {OLLAMA_MODEL}")
        else:
            print(f"Current model: {OLLAMA_MODEL}")
        continue

    response = process_input(user_input)

    if response:
        type_out("VEO-GPT: " + response)
