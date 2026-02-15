# VEO-GPTx

![VEO-GPTx Logo](./assets/logo.png)

VEO-GPTx is a personalized AI assistant designed to run directly in a Linux terminal, leveraging the OpenAI API for real-time interaction. It emphasizes **simplicity, speed, and flexibility**, making it ideal for developers, system administrators, and tech enthusiasts who want AI support without leaving the command line.  

---

## **Fallback System (Offline Mode)**

The fallback mechanism allows VEO-GPTx to **continue functioning even if the OpenAI API is unreachable**. Instead of stopping, it uses:

- Local tools and scripts  
- Preloaded prompts  
- Simple Python-based utilities  

This ensures the assistant remains **responsive and useful offline**. Once internet connectivity is restored, it automatically resumes full AI capabilities.  

---

## **Setup Instructions**

### **1. Clone the Repository**

```bash
git clone https://github.com/graven144p/VEO-GPTx
cd VEO-GPTx

2. Install Python (3.11+)
Download and install the latest Python from:
https://www.python.org/downloads/source/

Verify installation:

python3 --version

3. Install Dependencies
pip install -r requirements.txt
pip install openai

4. Configure OpenAI API Key
import openai
openai.api_key = "YOUR_OPENAI_API_KEY"

5. Run VEO-GPTx
~/python3/bin/python3 /home/user/VEO-GPTx.py

Usage Example
After running VEO-GPTx in your terminal, you can interact with it like this:

> hello
VEO-GPTx: Hi there! How can I assist you today?


├─ README.md
├─ requirements.txt
