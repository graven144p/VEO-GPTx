#!/usr/bin/env python3

import random
import re
import time
import os
import json
import ast
import operator
import threading
import requests
from datetime import datetime

# -------------------------------
# ASCII Banner + Startup Status
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

# -------------------------------
# Ollama Configuration
# -------------------------------
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"

def ollama_running():
    try:
        r = requests.get(OLLAMA_TAGS_URL, timeout=3)
        return r.status_code == 200
    except:
        return False

OLLAMA_AVAILABLE = ollama_running()

current_date = datetime.now().strftime('%A, %B %d, %Y')

if OLLAMA_AVAILABLE:
    model_status = f"Ollama detected. Model: {OLLAMA_MODEL}"
else:
    model_status = "Ollama not detected. Running offline brain only."

startup_status = f"{model_status}\nMemory loaded. {current_date}\n"

print(banner)
print(startup_status)

# -------------------------------
# Track start time
# -------------------------------
start_time = time.time()

# -------------------------------
# Memory Setup
# -------------------------------
MEMORY_DIR = os.path.expanduser("~/VEO-GPTx/Memory")
MEMORY_FILE = os.path.join(MEMORY_DIR, "veo_memory.json")
os.makedirs(MEMORY_DIR, exist_ok=True)

preload_memory = [
    {"user": "hi", "assistant": "Hey! How’s it going?"},
    {"user": "hello", "assistant": "Hello! Nice to see you."},
]

if os.path.exists(MEMORY_FILE):
    try:
        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)
    except:
        memory = preload_memory.copy()
else:
    memory = preload_memory.copy()
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

# -------------------------------
# Utilities
# -------------------------------
def normalize(text):
    return re.sub(r'[^\w\s]', '', text.lower())

def type_out(text, delay=0.02):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()

def contains_trigger(user, triggers):
    return any(re.search(rf"\b{t}\b", user) for t in triggers)

# -------------------------------
# Safe Math Engine
# -------------------------------
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg
}

def safe_eval(expr):
    def eval_node(node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            return SAFE_OPERATORS[type(node.op)](
                eval_node(node.left),
                eval_node(node.right)
            )
        elif isinstance(node, ast.UnaryOp):
            return SAFE_OPERATORS[type(node.op)](
                eval_node(node.operand)
            )
        else:
            raise ValueError("Unsafe expression")
    tree = ast.parse(expr, mode='eval')
    return eval_node(tree.body)

# -------------------------------
# Ollama Streaming Brain
# -------------------------------
def ask_ollama(prompt):
    if not OLLAMA_AVAILABLE:
        return None

    try:
        conversation_context = ""
        for mem in memory[-5:]:
            conversation_context += f"User: {mem['user']}\nAssistant: {mem['assistant']}\n"

        full_prompt = conversation_context + f"User: {prompt}\nAssistant:"

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": full_prompt,
            "stream": True
        }

        response = requests.post(OLLAMA_GENERATE_URL, json=payload, stream=True, timeout=120)
        response.raise_for_status()

        full_reply = ""

        print("VEO-GPT: ", end="", flush=True)

        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                chunk = data.get("response", "")
                print(chunk, end="", flush=True)
                full_reply += chunk

        print("\n")
        return full_reply.strip()

    except:
        return None

# -------------------------------
# Offline Brain (Fallback)
# -------------------------------
def offline_brain(user_input):

    # Try Ollama first
    ollama_reply = ask_ollama(user_input)
    if ollama_reply:
        memory.append({"user": user_input, "assistant": ollama_reply})
        save_memory()
        return None

    user = normalize(user_input)
    response = ""

    greeting_triggers = ["hi", "hello", "hey", "yo"]
    gratitude_triggers = ["thank you", "thanks", "thx"]
    joke_triggers = ["joke", "funny"]

    if contains_trigger(user, greeting_triggers):
        response = random.choice(["Hey there!", "Hello!", "Yo!"])
    elif contains_trigger(user, gratitude_triggers):
        response = "You’re welcome!"
    elif contains_trigger(user, joke_triggers):
        response = "Why do programmers prefer dark mode? Because light attracts bugs!"
    elif re.fullmatch(r"[0-9\.\+\-\*\/\(\) ]+", user):
        try:
            result = safe_eval(user)
            response = f"The result is {result}."
        except:
            response = "That math didn’t work."
    elif "time" in user:
        response = f"The current time is {datetime.now().strftime('%H:%M:%S')}."
    elif "date" in user:
        response = f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."
    else:
        response = "I’m listening… tell me more."

    memory.append({"user": user_input, "assistant": response})
    save_memory()
    return response

# -------------------------------
# Idle Thread
# -------------------------------
IDLE_INTERVAL = 180
last_input_time = time.time()
idle_shown = False

def idle_loop():
    global last_input_time, idle_shown
    idle_messages = ["Standing by.", "Idle mode active.", "Listening..."]
    while True:
        time.sleep(1)
        if time.time() - last_input_time > IDLE_INTERVAL and not idle_shown:
            print("VEO-GPT:", random.choice(idle_messages))
            idle_shown = True

threading.Thread(target=idle_loop, daemon=True).start()

# -------------------------------
# Main Loop
# -------------------------------
while True:
    user_input = input("You: ").strip()
    last_input_time = time.time()
    idle_shown = False

    if user_input.lower() in ["exit", "quit", "bye"]:
        print("VEO-GPT: Goodbye! 👋")
        break

    if user_input.startswith("/status"):
        uptime = int(time.time() - start_time)
        brain = "Llama3 (Ollama)" if OLLAMA_AVAILABLE else "Offline Brain"
        print(f"VEO-GPT: Brain: {brain} | Model: {OLLAMA_MODEL} | Uptime: {uptime}s")
        continue

    if user_input.startswith("/model"):
        parts = user_input.split()
        if len(parts) > 1:
            OLLAMA_MODEL = parts[1]
            print(f"VEO-GPT: Model switched to {OLLAMA_MODEL}")
        else:
            print(f"VEO-GPT: Current model is {OLLAMA_MODEL}")
        continue

    response = offline_brain(user_input)

    if response:
        type_out("VEO-GPT: " + response)
