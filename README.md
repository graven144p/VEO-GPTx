# VEO-GPTx
VEO-GPTx is a personalized AI assistant designed to run directly in a Linux terminal, leveraging the OpenAI API for real-time interaction. It emphasizes simplicity, speed, and flexibility, making it ideal for developers, system administrators, and tech enthusiasts who want AI support without leaving the command line.

Fallback System (Offline Mode):
The fallback mechanism allows VEO-GPTx to continue functioning even if the OpenAI API is unreachable. Instead of stopping, it uses:



Local tools and scripts

Preloaded prompts

Simple Python-based utilities

This ensures the assistant remains responsive and useful offline. Once internet connectivity is restored, it automatically resumes full AI capabilities.

Setup Instructions




Clone the Repository

git clone https://github.com/graven144p/VEO-GPTx
cd VEO-GPTx





Install Python (3.11+)
Download and install the latest Python from:
https://www.python.org/downloads/source/

Verify installation:

python3 --version




Install Dependencies

pip install -r requirements.txt
pip install openai




Configure OpenAI API Key
In your Python code or environment, set your API key:

import openai
openai.api_key = "YOUR_OPENAI_API_KEY"


Run VEO-GPTx

~/python3/bin/python3 /home/user/VEO-GPTx.py


