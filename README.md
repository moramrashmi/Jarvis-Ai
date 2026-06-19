# 🤖 JARVIS - Intelligent Local AI Agent

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-1.1-lightgrey?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow?logo=javascript&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![Groq](https://img.shields.io/badge/Groq_API-LLaMA_3.1-orange?logo=groq&logoColor=white)](https://console.groq.com/docs/overview)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

> A **secure, privacy-first AI agent framework** with voice control, intelligent planning, and web automation. Runs locally with zero cloud exposure for your sensitive operations.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔐 **Secure Architecture** | Backend gateway with token authentication & server-side Groq integration |
| 🎤 **Voice Control** | Natural speech recognition & synthesis for hands-free operation |
| 🧠 **Intelligent Brain** | Planning, intent inference, and tool governance with confidence scoring |
| 🌐 **Web Automation** | Screen capture, web scraping, and system command execution |
| 🔒 **Privacy First** | API keys & tokens stored server-side only (never exposed to frontend) |
| 💻 **Localhost-Only** | Runs on 127.0.0.1 with restricted CORS for maximum isolation |
| 🎯 **Agentic Loop** | Iterative planning-execution-analysis workflow |

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     BROWSER (Frontend)                      │
│                   jarvis-v2.html                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ • Voice Input (SpeechRecognition API)                │  │
│  │ • Agentic Brain (Planning + Intent Inference)        │  │
│  │ • Tool Governance & Confidence Scoring               │  │
│  │ • Voice Output (SpeechSynthesis API)                 │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────┬─────────────────────────────────────────────┘
                 │ HTTP/HTTPS (Localhost:5000)
                 ↓
┌─────────────────────────────────────────────────────────────┐
│              GATEWAY SERVER (Secure Proxy)                  │
│              jarvis_server.py (Port 5050)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ • Token Authentication                               │  │
│  │ • Groq API Proxy (/api/chat)                         │  │
│  │ • Vision Analysis Proxy (/api/vision-analyze)        │  │
│  │ • Config Handshake (/api/config)                     │  │
│  │ • Engine Token Management                            │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────┬──────────────────────────────────────────────┬──┘
             │                                              │
       HTTP  │                                              │ HTTP
      :5000  │                                              │ :5050
             ↓                                              ↓
    ┌──────────────────────┐          ┌──────────────────────┐
    │  Groq Cloud LLM      │          │ LOCAL ENGINE         │
    │  API (Secure Key)    │          │ jarvis_engine.py     │
    │                      │          │                      │
    │ • LLaMA 3.1-8B       │          │ • System Control     │
    │ • Server-side auth   │          │ • Screen Capture     │
    └──────────────────────┘          │ • Script Execution   │
                                       │ • Web Scraping       │
                                       │ • Token Auth         │
                                       └──────────────────────┘
```

---

## 🛠️ Tech Stack

### **Backend**
- **Flask 1.1** - Lightweight REST API framework
- **Flask-CORS** - Cross-origin resource sharing management
- **Python 3.11** - Core runtime environment

### **Frontend**
- **Vanilla JavaScript (ES6+)** - Zero-dependency, fast UI
- **Web Speech API** - Voice recognition & synthesis
- **File System Access API** - Local file operations
- **Fetch API** - HTTP client for backend communication

### **AI/LLM**
- **Groq API** - Fast LLaMA 3.1-8B inference (300+ tokens/sec)
- **Vision Capabilities** - Screenshot analysis via Groq's multimodal models

### **Libraries**
- **Requests** - HTTP client for web scraping & Groq proxying
- **Pillow** - Screenshot capture & image processing
- **BeautifulSoup4** - HTML parsing & web scraping
- **python-dotenv** - Environment variable management

### **Security**
- **Token-based Auth** - X-Jarvis-Token header validation
- **Localhost-only Binding** - 127.0.0.1:5050 & :5000 (no external exposure)
- **CORS Whitelisting** - Restricted to ["null", "http://localhost", "http://127.0.0.1"]
- **Command Filtering** - Safe shell execution with dangerous pattern blocking
- **URL Validation** - SSRF protection with private IP range blocking

---

## 🚀 How It Works

### **1. Voice Input → Intent Parsing**
```
User speaks → SpeechRecognition captures audio → Frontend sends to Groq
             ↓
        Groq LLM analyzes intent & parses commands
```

### **2. Planning Phase**
```
Intent received → Brain generates execution plan → Confidence scoring applied
             ↓
      Tool governance checks threshold → Proceed or ask for confirmation
```

### **3. Tool Execution**
```
Selected tools called with auth token → Engine validates request → Execute safely
             ↓
      Results analyzed → Response generated → Voice synthesis output to user
```

### **4. Memory & Learning**
```
Each interaction stored in episodic memory → Intent patterns learned
             ↓
      Confidence scores adjust over time → Better planning accuracy
```

---

## 📦 Quick Start

### **Prerequisites**
- Python 3.11+
- Groq API key (free at [console.groq.com](https://console.groq.com))
- Modern browser with Web Speech API support

### **Installation**

```bash
# 1. Clone repository
git clone https://github.com/SukumarJujjuvarapu/Jarvis.git
cd Jarvis

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.template .env
# Edit .env and add your GROQ_API_KEY
```

### **Running JARVIS**

```bash
# Terminal 1: Start the execution engine
python jarvis_engine.py
# Output: Listening on 127.0.0.1:5050

# Terminal 2: Start the gateway server
python jarvis_server.py
# Output: Open http://localhost:5000 in your browser
```

Then open **http://localhost:5000** in your browser and start talking! 🎤

---

## 🔐 Security Features

✅ **Zero API Key Exposure** - Groq key stored server-side only  
✅ **Token Authentication** - All engine calls require X-Jarvis-Token header  
✅ **Localhost Isolation** - Services run on 127.0.0.1 (no external network exposure)  
✅ **CORS Whitelist** - Only localhost origins can communicate with server  
✅ **Command Filtering** - Dangerous shell patterns blocked (rm -rf, format, etc.)  
✅ **URL Validation** - Web scraping blocked for private IP ranges (SSRF protection)  
✅ **Temp File Cleanup** - Script executions use random UUIDs with proper cleanup  
✅ **Safe Rendering** - XSS protection via textContent (no innerHTML eval)  

---

## 📊 Performance

| Operation | Speed | Note |
|-----------|-------|------|
| Intent Parsing | ~500ms | Groq LLaMA 3.1 inference |
| Tool Execution | ~100-500ms | Varies by operation complexity |
| Screen Capture | ~50ms | Pillow-based PIL capture |
| Web Scraping | ~1-3s | Network latency dependent |
| Voice Synthesis | Real-time | Native Web Speech API |

---

## 🎯 Roadmap

- [ ] **Long-term Memory** - SQLite/persistent JSON storage for user preferences
- [ ] **Enhanced Planner** - Subtask breakdown & retry logic
- [ ] **Permissions UI** - Tool approval levels (auto-safe, confirm, blocked)
- [ ] **Streaming Responses** - Real-time token streaming for long operations
- [ ] **Browser Automation** - Puppeteer-based web navigation
- [ ] **Session Compression** - Memory cleanup & state optimization
- [ ] **Project Workspace** - Multi-file coding task support
- [ ] **Observability Panel** - Internal debug info & metrics dashboard

---

## 👨‍💻 About Me & My Work

**Sukumar Jujjuvarapu** - AI/ML Engineer & Full-Stack Developer

### **Vision**
Building intelligent systems that augment human capability through natural voice interaction and autonomous task execution—with privacy and security as foundational principles.

### **Expertise**
- 🤖 **AI/ML**: LLM integration, agentic systems, intent classification
- 🔐 **Security**: Token auth, CORS policies, secure API design
- 🌐 **Full-Stack**: Python/Flask backend, vanilla JS frontend, API architecture
- 📡 **Cloud Integration**: Groq API, distributed service design, proxy patterns

### **This Project Represents**
JARVIS showcases a **production-grade agentic AI framework** combining:
- **Architectural Excellence**: Three-tier design with secure gateway pattern
- **Security Best Practices**: Token auth, localhost binding, CORS whitelisting, SSRF protection
- **Intelligent Design**: Planning-based execution, confidence scoring, episodic memory
- **User Experience**: Natural voice interaction with visual feedback

### **Philosophy**
*"Intelligence without security is reckless. Security without usability is pointless. JARVIS achieves both."*

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- [Groq](https://groq.com/) - Ultra-fast LLM inference
- [Flask](https://flask.palletsprojects.com/) - Lightweight web framework
- [Web APIs](https://developer.mozilla.org/en-US/docs/Web/API) - Modern browser capabilities

---

## 📞 Contact & Links

- **GitHub**: [github.com/SukumarJujjuvarapu](https://github.com/SukumarJujjuvarapu)
- **Repository**: [Jarvis](https://github.com/SukumarJujjuvarapu/Jarvis)

**Built with ❤️ for secure, intelligent AI automation**
