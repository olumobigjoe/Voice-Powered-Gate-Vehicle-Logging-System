# 🚗 Voice-Powered Gate Vehicle Logging System (Offline + AI)

A smart, offline-first vehicle entry/exit logging system that replaces manual gate logs with **voice input + AI extraction**.

---

## 📌 Overview

This system allows security guards to:
- 🎤 Record vehicle details using voice (15 seconds)
- 🧠 Transcribe speech into text
- 🤖 Extract structured vehicle data using a local LLM (Ollama)
- ✅ Confirm entries before saving
- 🚪 Track vehicle check-in and check-out

---

## ⚙️ Tech Stack

- Streamlit (UI)
- SpeechRecognition + pydub (voice processing)
- Ollama (llama3.2:1b) – local AI
- Pandas (data handling)
- Fully Offline (LLM runs locally)

---

## 🧩 Features

### 🎤 Voice Input
Say:
> "KJA 123 AB private red Toyota Corolla"

---

### 🤖 AI Extraction Output
```json
{
  "plate_number": "KJA123AB",
  "type": "Private",
  "color": "Red",
  "model": "Toyota Corolla"
}
