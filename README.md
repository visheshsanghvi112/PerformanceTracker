# PerformanceTracker
# 💬 Telegram Performance Tracker Bot

A smart sales & purchase logging bot for field staff. Accepts messages in natural or structured format and logs them into Google Sheets. Powered by Google Gemini AI.

---

## 📸 Scan to Try the Bot

![Performance Tracker Bot QR](897f4f5c-1f41-4eb4-b430-6ee07ee1030b.png)

[@PerformanceTracker786Bot](https://t.me/PerformanceTracker786Bot)

---

## 🚀 Features

- Log sales and purchase updates
- Accepts structured and unstructured (messy) messages
- Auto-detects:
  - ✅ Client name
  - ✅ Location
  - ✅ Order quantity
  - ✅ Amount (INR)
  - ✅ Remarks
  - ✅ Timestamp
- Gemini 2.5 Flash model for natural language parsing
- Stores all data in a live Google Sheet

---

## 🧰 Requirements

Ensure you have Python 3.9+ installed.

Install `pip` if needed:

```bash
python -m ensurepip --upgrade
git clone https://github.com/yourusername/performance-tracker-bot.git
cd performance-tracker-bot
pip install -r requirements.txt
