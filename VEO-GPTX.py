#!/usr/bin/env python3

import random
import re
import time
import os
import json
import ast
import operator
import threading
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
current_date = datetime.now().strftime('%A, %B %d, %Y')
startup_status = f"OpenAI unavailable. Running offline mode only.\nMemory loaded. {current_date}\n"

print(banner)
print(startup_status)

# -------------------------------
# Track start time
# -------------------------------
start_time = time.time()

# -------------------------------
# Memory Setup
# -------------------------------
MEMORY_DIR = "/home/user/VEO-GPTx/Memory"
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
    except Exception:
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
# Offline Brain (SMART UPGRADE)
# -------------------------------
def offline_brain(user_input):
    user = normalize(user_input)
    response = ""

    # --- Triggers ---
    gratitude_triggers = ["thank you", "thanks", "thx", "ty"]
    greeting_triggers = ["hi", "hello", "hey", "yo", "sup", "hola"]
    how_triggers = ["how are you", "how are u", "how r u", "hows it going", "how you doing"]
    mood_triggers = ["bored", "tired", "happy", "sad", "excited", "angry"]
    joke_triggers = ["joke", "funny", "make me laugh"]
    advice_triggers = ["should i", "what do you think", "what's your opinion"]
    linux_triggers = ["linux commands", "show me linux commands", "basic linux commands", "linux tips"]

    # --- SMART MEMORY RECALL ---
    for mem in memory[-10:]:  # look at last 10 messages
        if user in normalize(mem["user"]):
            response = f"As we discussed earlier: {mem['assistant']}"
            break

    # --- SMART RESPONSE LOGIC ---
    if not response:
        if contains_trigger(user, gratitude_triggers):
            response = random.choice(["You’re welcome! 😊", "No problem!", "Anytime!"])
        elif contains_trigger(user, how_triggers):
            response = random.choice(["I'm doing great! How about you?", "All good here. How’s your day?", "Feeling awesome! And you?"])
        elif "time" in user:
            response = f"The current time is {datetime.now().strftime('%H:%M:%S')}."
        elif "date" in user or "today" in user:
            response = f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."
        elif re.fullmatch(r"[0-9\.\+\-\*\/\(\) ]+", user):
            try:
                result = safe_eval(user)
                response = f"The result is {result}."
            except:
                response = "Hmm… that math didn’t work 😅"
        elif contains_trigger(user, greeting_triggers):
            response = random.choice(["Hey there! How’s it going?", "Hi! Nice to see you.", "Hello! How’s your day?", "Yo! What’s up?"])
        elif contains_trigger(user, mood_triggers):
            response = random.choice(["I see… hope you’re having a good one!", "Thanks for sharing!", "Sounds like you’ve got some energy there!"])
        elif contains_trigger(user, joke_triggers):
            response = random.choice([
                "Why did the computer go to therapy? Too many bytes of stress!",
                "I would tell you a joke about UDP… but you might not get it.",
                "Why do programmers prefer dark mode? Because light attracts bugs!"
            ])
        elif contains_trigger(user, advice_triggers):
            response = random.choice(["Hmm… I’d weigh the options carefully.", "It depends… tell me more.", "Think it through before deciding."])
        elif contains_trigger(user, linux_triggers):
            response = random.choice([
                "Basic Linux commands: ls, cd, pwd, mkdir, rm, cp, mv",
                "Tip: 'man command' shows the manual for any Linux command.",
                "'sudo' gives admin privileges. Use wisely!"
            ])
        # --- COMMANDS ---
        elif "flip a coin" in user or "/flip a coin" in user:
            response = random.choice(["Heads", "Tails"])
        elif "roll a dice" in user or "roll a die" in user or "/roll a dice" in user:
            response = f"You rolled a {random.randint(1,6)}"
        # --- Default fallback ---
        else:
            response = random.choice([
                "Interesting… tell me more!",
                "I’m listening, go on.",
                "I see, what else is happening?",
                "Could you explain that a bit more?",
                "That’s intriguing, tell me more details!"
            ])

    # --- SAVE MEMORY ---
    memory.append({"user": user_input, "assistant": response})
    save_memory()
    return response

# -------------------------------
# Idle Thread
# -------------------------------
IDLE_INTERVAL = 180  # 3 minutes
last_input_time = time.time()
idle_shown = False

def idle_loop():
    global last_input_time, idle_shown
    idle_messages = ["Standing by.", "Idle mode active.", "Awaiting input.", "Listening..."]
    while True:
        time.sleep(1)
        elapsed = time.time() - last_input_time
        if elapsed > IDLE_INTERVAL and not idle_shown:
            type_out("VEO-GPT: " + random.choice(idle_messages))
            idle_shown = True

idle_thread = threading.Thread(target=idle_loop, daemon=True)
idle_thread.start()

# -------------------------------
# Main Loop
# -------------------------------
while True:
    user_input = input("You: ").strip()
    last_input_time = time.time()
    idle_shown = False

    if user_input.lower() in ["exit", "/exit", "quit", "/quit", "bye"]:
        type_out("VEO-GPT: Goodbye! Talk soon 😊")
        break

    response = offline_brain(user_input)
    type_out("VEO-GPT: " + response)
