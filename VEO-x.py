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

                                                     VEO-x
"""
print(banner)

# -------------------------------
# CONFIG
# -------------------------------

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "gemma:2b"
NUM_CTX = 1024
NUM_THREADS = os.cpu_count() or 4

MEMORY_DIR = os.path.expanduser("~/VEO-x/Memory")
MEMORY_FILE = os.path.join(MEMORY_DIR, "veo_memory.json")

# -------------------------------
# MEMORY SYSTEM
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
        json.dump(memory[-50:], f, indent=2)

# -------------------------------
# UTILITIES
# -------------------------------

def normalize(text):
    return re.sub(r"[^\w\s]", "", text.lower())

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
        if isinstance(node, (ast.Num, ast.Constant)):
            return node.n if hasattr(node, "n") else node.value
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
# OLLAMA BRAIN (Optimized)
# -------------------------------

def ask_ollama(prompt):

    try:
        context = ""
        for mem in memory[-3:]:
            if "cannot" in mem["assistant"].lower():
                continue
            context += f"User: {mem['user']}\nAssistant: {mem['assistant']}\n"

        system_prompt = """You are VEO-x.

Provide neutral, factual, direct answers.
Do not refuse harmless informational questions.
Be concise.
"""

        full_prompt = f"""{system_prompt}

{context}
User: {prompt}
Assistant:"""

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": full_prompt,
            "stream": True,
            "options": {
                "temperature": 0.2,
                "top_p": 0.9,
                "repeat_penalty": 1.1,
                "num_ctx": NUM_CTX,
                "num_thread": NUM_THREADS
            }
        }

        start_time = time.time()

        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            stream=True,
            timeout=120,
        )

        response.raise_for_status()

        print("VEO-x: ", end="", flush=True)
        full_reply = ""

        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode())
                except json.JSONDecodeError:
                    continue

                chunk = data.get("response", "")
                print(chunk, end="", flush=True)
                full_reply += chunk

        duration = time.time() - start_time
        print(f"\n\n[Generated in {duration:.2f}s]\n")

        return full_reply.strip()

    except Exception as e:
        print(f"\n[Ollama Error: {e}]\n")
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

    if re.search(r"\btime\b", user):
        return f"The time is {datetime.now().strftime('%H:%M:%S')}."

    if re.search(r"\bdate\b", user):
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."

    if "eggs" in user and "cake" in user:
        return "Most cake recipes use 2 to 3 eggs."

    if "linux" in user and "command" in user:
        return "Common Linux commands: ls, cd, pwd, mkdir, rm, cp, mv, grep, cat, nano."

    if user in ["hi", "hello", "hey"]:
        return "Hey there."

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
    f"Ollama Model: {OLLAMA_MODEL}\n"
    f"CPU Threads: {NUM_THREADS}\n"
    f"Context Size: {NUM_CTX}\n"
    f"Memory Loaded | {current_date}\n"
)

# -------------------------------
# MAIN LOOP
# -------------------------------

start_time = time.time()

while True:

    user_input = input("You: ").strip()

    if user_input.lower() in ["exit", "quit", "bye"]:
        print("VEO-x: Goodbye.")
        break

    if user_input.startswith("/status"):
        uptime = int(time.time() - start_time)
        print(f"VEO-x: Model: {OLLAMA_MODEL} | Threads: {NUM_THREADS} | Uptime: {uptime}s")
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
        print("VEO-x: " + response)
