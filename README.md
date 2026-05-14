# Hive Industrial Sentinel (HIS) 🐝🛡️

**Autonomous & Governed Industrial AI Agent**

The **Hive Industrial Sentinel** is a high-integrity AI solution designed to monitor critical infrastructures such as smart-grid power transformers. It addresses the challenge of combining the reasoning capabilities of Large Language Models (LLMs) with the strict safety requirements of industrial environments.

This project was developed for the **Transforming Enterprise Through AI Hackathon**, with a special focus on the **Agent Security & AI Governance** track.

---

## 🚀 Innovation & Architecture

Industrial teams require real-time diagnostics, but autonomous agents cannot "hallucinate" or recommend unsafe actions in physical systems. HIS implements a **Three-Layer Architecture**:

1. **Intelligence Layer (Gemini 2.5):**  
   Uses the **CLEAN** prompt framework to provide engineering diagnostics based on real-time data and technical manuals.

2. **Connectivity Layer (MCP-Ready):**  
   Employs a modular tooling standard compatible with the **Model Context Protocol (MCP)** to retrieve telemetry and query technical documentation.

3. **Governance Layer (Lobster Trap):**  
   A security proxy inspired by the *Lobster Trap* pattern that inspects every prompt and response, enforcing safety policies and logging audits.

---

## 🛠️ Technology Stack

- **LLM:** Google Gemini 2.5 Flash & Pro (via OpenAI-compatible endpoint)
- **Security:** Lobster Trap (Ingress/Egress policy layer)
- **Connectivity:** Python MCP Tooling
- **Interface:** Industrial Dashboard built with Streamlit
- **Data:** Simulated Telemetry (Voltage, Load, Oil Temperature)

---

## ⚙️ Installation & Setup

### 1. Clone and Configure the Environment
```powershell
git clone https://github.com/your-username/hive-industrial-sentinel
cd hive-industrial-sentinel
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```