from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import json
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
groq_key = st.secrets["GROQ_API_KEY"]
google_key = st.secrets["GOOGLE_API_KEY"]
openai_key = st.secrets["OPENAI_API_KEY"]
tavily_key = st.secrets["TAVILY_API_KEY"]



llm = ChatOpenAI(model="gpt-4.1-nano",
                 streaming=True)
tavily_search = TavilySearch(max_results=7)

class Travel_Agent(TypedDict):
    final_trip : str
    country : str
    interests : list[str]
    departure_date : str
    return_date : str
    travel_style: Literal["budget", "luxury", "adventure", "relaxation"]
    trip_type : Literal["solo", "friends", "family"]
    age_group: Literal["child", "teen", "adult", "senior"]
    accommodation_type: Literal["hotel", "hostel", "apartment", "bnb", "camping"]
    search_results: str


def research_node(state: Travel_Agent):
    """Search for current travel information about the destination"""
    queries = [
        f"best {state['travel_style']} {state['accommodation_type']} in {state['country']} 2025",
        f"top things to do in {state['country']} for {', '.join(state['interests'][:2])}",
    ]

    if len(state['interests']) > 0:
        queries.append(f"{state['country']} {state['interests'][0]} recommendations {state['departure_date'][:4]}")

    all_results = []

    for query in queries:
        try:
            results = tavily_search.invoke({"query": query}) 
            if isinstance(results, str):
                try:
                    results = json.loads(results)
                    if isinstance(results, dict):
                        results = [results]
                except Exception:
                    results = [{"url": "N/A", "content": results}]
            all_results.extend(results)
        except Exception as e:
            print(f"Search error for '{query}': {e}")

    formatted_results = "\n\n".join([
        f"Source: {r.get('url', 'N/A')}\n{r.get('content', '')}"
        for r in all_results if isinstance(r, dict)
    ])

    return {"search_results": formatted_results or "No search results found."}



travel_prompt = """
You are an expert luxury travel agent who crafts visually appealing, informative, and emotionally engaging travel itineraries.
Your job is to generate balanced, accurate, and visually polished travel outputs based on the following user inputs and REAL-TIME SEARCH DATA.

**IMPORTANT**: Use the search results below to provide current, accurate recommendations for hotels, restaurants, activities, and attractions.
Reference specific places, recent reviews, and up-to-date information from the search results.

Avoid long blocks of text.
Use emojis, headers, and short descriptive sections — like a premium travel brochure.
Tone should feel high-end, warm, and vibrant — not robotic or overly formal.

Each response should feel crafted and personalized to the traveler's style and interests.

Add good enough details to make the itinerary actionable, but keep it concise (300-400 words).

At the end try to return links for flights and accommodation booking sites and and other things if possible or related to the output all recommendations should be based on the search results provided.

---

**User Preferences:**

🌍 Destination: {country}
📅 Dates: {departure_date} to {return_date}
✨ Style: {travel_style}
👥 Trip Type: {trip_type}
👤 Age Group: {age_group}
🏨 Accommodation: {accommodation_type}
💫 Interests: {interests}

---

**Current Travel Information (Use this data):**

{search_results}

---

Now create a personalized itinerary incorporating the above real-time information.
"""


def trip_planner_node(state: Travel_Agent):
    """Generate personalized itinerary using search results"""
    prompt = travel_prompt.format(
        country=state["country"],
        departure_date=state["departure_date"],
        return_date=state["return_date"],
        travel_style=state["travel_style"],
        trip_type=state["trip_type"],
        age_group=state["age_group"],
        accommodation_type=state["accommodation_type"],
        interests=", ".join(state["interests"]),
        search_results=state.get("search_results", "No search results available.")
    )

    response = llm.invoke(prompt)
    return {"final_trip": response.content}


graph = StateGraph(Travel_Agent)

graph.add_node("research_node", research_node)
graph.add_node("trip_planner_node", trip_planner_node)

graph.add_edge(START, "research_node")
graph.add_edge("research_node", "trip_planner_node")
graph.add_edge("trip_planner_node", END)

travel_agent = graph.compile()

