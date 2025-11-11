## AI Trip Planner (Travel Agent)

A small FastAPI + Streamlit project that generates personalized travel itineraries using an LLM-driven agent and real-time search results.

This repository contains:

- `app.py` — FastAPI backend that exposes a `/response` endpoint and wires into the travel agent graph.
- `Travel_Agent.py` — The agent implementation: research node (real-time search) + trip planner node (LLM prompt generation).
- `main.py` — Streamlit frontend for user input and displaying the generated itinerary.

### Quick overview

The backend (`app.py`) accepts a POST request with user preferences and returns a generated trip itinerary produced by the stateful travel agent implemented in `Travel_Agent.py`.

The frontend (`main.py`) is a Streamlit app that collects user input (destination, dates, interests, style, etc.), calls the backend, and displays the result.

## Requirements

See `requirements.txt` for the primary dependencies and notes about optional/custom packages.

## Environment & Secrets

Create a `.env` file in the project root with the following variables (example):

```
OPENAI_API_KEY=sk-...
# If the project uses an external search provider key, add that too, e.g.:
# TAVILY_API_KEY=your_tavily_key
```

The code uses `python-dotenv` to load environment variables.

## Installation (recommended)

Open PowerShell and run the following commands:

```powershell
# create & activate a virtual environment (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If you run into a package that isn't on PyPI (see `requirements.txt` comments), check the project's docs or the package source or install the package from the provider's recommended location.

## Running the backend (FastAPI)

Start the API server (run from the project root):

```powershell
# Run FastAPI via uvicorn
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at http://127.0.0.1:8000 and you can open the interactive docs at http://127.0.0.1:8000/docs

## Running the frontend (Streamlit)

In another terminal (with the virtualenv activated):

```powershell
streamlit run main.py
```

Open the Streamlit UI in your browser (typically `http://localhost:8501`). The front-end will POST to `http://127.0.0.1:8000/response` by default.

## API: /response

POST `/response` accepts a JSON body matching `Input_schema` in `app.py` and returns a JSON object with the generated itinerary (`final_result`).

Input fields (summary):

- `country`: string
- `interests`: list of strings (e.g., ["food","culture"]) 
- `departure_date`, `return_date`: YYYY-MM-DD
- `travel_style`: one of ["budget","luxury","adventure","relaxation"]
- `trip_type`: ["solo","friends","family"]
- `age_group`: ["child","teen","adult","senior"]
- `accommodation_type`: ["hotel","hostel","apartment","bnb","camping"]

Example payload:

```json
{
  "country": "usa",
  "interests": ["food","culture"],
  "departure_date": "2025-12-10",
  "return_date": "2025-12-17",
  "travel_style": "luxury",
  "trip_type": "solo",
  "age_group": "adult",
  "accommodation_type": "hotel"
}
```

Response: `{ "final_result": "<the generated itinerary text>" }`

## Notes on LLM / Search integrations

`Travel_Agent.py` references the following components:

- `ChatOpenAI` (LLM) — the code expects an LLM wrapper that reads `OPENAI_API_KEY`.
- `TavilySearch` — used for real-time search. If this is a custom or private provider, ensure you have the proper package and credentials.

If either `langchain_openai` or `langchain_tavily` are not installed from PyPI, please consult the provider's installation instructions or replace them with equivalents (for example, `openai` + custom search integration).

## Troubleshooting

- Cannot connect to API from Streamlit: ensure the FastAPI server is running and reachable at `127.0.0.1:8000`.
- Key/credentials errors: check `.env` is present and the environment variables are correctly set before starting the server.
- Package not found: inspect `requirements.txt` and install any provider-specific packages per their documentation.

## Tests / Validation

There are no automated tests added in this repository yet. A good next step is to add a small test that POSTs a sample payload to `/response` and asserts a 200 response and non-empty `final_result`.

## Next steps / Improvements

- Add unit tests for the API inputs and agent behavior.
- Add Dockerfile / docker-compose for easier deployment.
- Add CI to run linting and tests automatically.
- Add clearer handling for missing provider libraries and descriptive runtime errors when a provider is not installed.

## License

This project doesn't include an explicit license file. Add a `LICENSE` file to make licensing intentions explicit.

---

If you want, I can also add a small unittest that sends a sample payload to `/response` and checks the response format.
