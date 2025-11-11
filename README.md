# ✈️ Travel Agent — AI-Powered Itinerary Planner (LangGraph + Streamlit + FastAPI)

**Live App:** https://travelagent-yugzam4z6zmjnpzzbusiar.streamlit.app/  
**Repository:** https://github.com/junaidariie/Travel_agent/

This project builds personalized, visually appealing travel itineraries using real-time search, natural language generation, and a LangGraph workflow. It behaves like a premium travel consultant — crafting brochures with emojis, headers, and up-to-date recommendations.

A FastAPI backend is also included and ready for deployment. The only reason it’s not publicly hosted is because the author doesn’t have access to a Claude service that part of the backend was intended to use — otherwise, the API is fully deployable with OpenAI + Tavily.

---

## 🌟 Key Features

- Realtime travel research (hotels, restaurants, attractions, reviews)
- LangGraph pipeline for:
  - Research step (destination + travel style + interests)
  - Itinerary generation (300–400 word polished brochure)
- Streamlit UI for interactive usage
- FastAPI backend (deployable)
- Personalized results based on:
  - Country, Dates, Interests
  - Age group, Trip type, Travel style, Accommodation

---

## 🧰 Tech Stack

- Python 3.10+
- LangGraph
- LangChain
- OpenAI (gpt-4.1-nano)
- Tavily Search
- Streamlit
- FastAPI + Uvicorn

---

## 📌 How It Works

1. User gives destination, dates, interests, and preferences.
2. The system performs real-time research using Tavily.
3. The itinerary is crafted using OpenAI with a premium brochure-like style.
4. Streamlit displays it beautifully with emojis, sections, and booking suggestions.

---

## 📦 Project Structure

```
Travel_agent/
├─ Streamlit App                # Frontend UI
├─ FastAPI Backend              # Deployable API
├─ LangGraph Workflow           # Nodes + State
├─ .env                         # API keys
└─ requirements.txt
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository
```
git clone https://github.com/junaidariie/Travel_agent.git
cd Travel_agent
```

### 2️⃣ Create & activate a virtual environment
```
python -m venv .venv
# Windows:  .venv\Scripts\activate
# mac/Linux: source .venv/bin/activate
```

### 3️⃣ Install dependencies
```
pip install -r requirements.txt
```

### 4️⃣ Add your environment variables in `.env`
```
OPENAI_API_KEY=sk-xxxx
TAVILY_API_KEY=tvly-xxxx
```

---

## ▶️ Run Streamlit App
```
streamlit run streamlit_app.py
```

---

## 🚀 FastAPI Backend (Deployable)

The backend exposes an endpoint that generates itineraries programmatically.

Run locally:
```
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Deployable on:
✅ Render  
✅ Railway  
✅ Fly.io  
✅ GCP  
✅ Azure  
✅ VPS

> Backend is ready — not deployed only due to missing Claude access at the moment.

---

## ✅ Highlights

- Handles messy search results safely
- Structured TypedDict state
- Produces modern, clean, non-generic itineraries
- Easy to extend with flight APIs, hotel pricing, etc.

---

## 📜 License
MIT License

---

## 🙌 Credits

- LangChain & LangGraph
- OpenAI
- Tavily
- Streamlit
- FastAPI
