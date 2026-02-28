# VEO-x

![VEO-x Logo](https://i.postimg.cc/jdgcshH3/logo.webp)


![VEO-Tx ](https://i.postimg.cc/CLDgCKFd/Untitled.png)




VEO-x is a personalized AI assistant designed to run directly in a Linux terminal, leveraging the ollama API for real-time interaction. It emphasizes **simplicity, speed, and flexibility**, making it ideal for developers, system administrators, and tech enthusiasts who want AI support without leaving the command line.  

---

## **Fallback System (Offline Mode)**

The fallback mechanism allows VEO-x to **continue functioning even if the ollama API is unreachable**. Instead of stopping, it uses:

- Local tools and scripts  
- Preloaded prompts  
- Simple Python-based utilities  

This ensures the assistant remains **responsive and useful offline**. Once internet connectivity is restored, it automatically resumes full AI capabilities.  

---

## **Setup Instructions**

### **1. Clone the Repository**

```bash
git clone https://github.com/graven144p/VEO-x
cd VEO-x

2. Install Python (3.11+)
Download and install the latest Python from:
https://www.python.org/downloads/source/

Verify installation:

python3 --version

3. Install Dependencies
curl -fsSL https://ollama.com/install.sh | sh


ollama pull gemma:2b





5. Run VEO-x
~/python3/bin/python3 /home/user/VEO-x.py

Usage Example
After running VEO-x in your terminal, you can interact with it like this:

> hello
VEO-x: Hi there! How can I assist you today?






