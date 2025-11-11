import streamlit as st
from datetime import datetime, timedelta
import json
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from dotenv import load_dotenv

load_dotenv()
groq_key = st.secrets["GROQ_API_KEY"]
google_key = st.secrets["GOOGLE_API_KEY"]
openai_key = st.secrets["OPENAI_API_KEY"]
tavily_key = st.secrets["TAVILY_API_KEY"]


# Page config
st.set_page_config(
    page_title="AI Trip Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for animations and styling
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 15px;
        border: none;
        font-size: 16px;
    }

    .stButton>button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
        transform: scale(1.02);
        transition: all 0.3s ease;
    }

    @keyframes plane {
        0% { transform: translateX(-100px) rotate(-15deg); opacity: 0; }
        50% { opacity: 1; }
        100% { transform: translateX(100vw) rotate(-15deg); opacity: 0; }
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    .loading-container {
        text-align: center;
        padding: 40px;
    }

    .plane-animation {
        font-size: 48px;
        animation: plane 3s ease-in-out infinite;
    }

    .loading-text {
        font-size: 24px;
        font-weight: bold;
        color: #667eea;
        animation: pulse 2s ease-in-out infinite;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)


# Initialize LangGraph components
@st.cache_resource
def init_travel_agent():
    """Initialize the travel agent graph"""
    llm = ChatOpenAI(model="gpt-4o-mini", streaming=True)
    tavily_search = TavilySearch(max_results=7)

    class Travel_Agent(TypedDict):
        final_trip: str
        country: str
        interests: list[str]
        departure_date: str
        return_date: str
        travel_style: Literal["budget", "luxury", "adventure", "relaxation"]
        trip_type: Literal["solo", "friends", "family"]
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

    return graph.compile()


# Initialize session state
if 'trip_generated' not in st.session_state:
    st.session_state.trip_generated = False
if 'trip_result' not in st.session_state:
    st.session_state.trip_result = None

# Header
st.title("✈️ AI Trip Planner")
st.markdown("### Plan your perfect getaway with AI-powered recommendations")
st.markdown("---")

# Sidebar for inputs
with st.sidebar:
    st.header("🎯 Trip Preferences")

    # Country selection
    country = st.text_input(
        "Destination Country",
        value="Japan",
        help="Enter the country you want to visit"
    )

    # Interests
    st.subheader("What interests you?")
    interests = st.multiselect(
        "Select your interests",
        ["food", "culture", "nature", "nightlife", "adventure", "history", "shopping", "beaches", "mountains"],
        default=["food", "culture"]
    )

    # Dates
    st.subheader("📅 Travel Dates")
    col1, col2 = st.columns(2)
    with col1:
        departure_date = st.date_input(
            "Departure",
            value=datetime.now() + timedelta(days=30),
            min_value=datetime.now()
        )
    with col2:
        return_date = st.date_input(
            "Return",
            value=datetime.now() + timedelta(days=37),
            min_value=departure_date
        )

    # Travel style
    travel_style = st.selectbox(
        "Travel Style",
        ["budget", "luxury", "adventure", "relaxation"]
    )

    # Trip type
    trip_type = st.selectbox(
        "Traveling with",
        ["solo", "friends", "family"]
    )

    # Age group
    age_group = st.selectbox(
        "Age Group",
        ["child", "teen", "adult", "senior"]
    )

    # Accommodation
    accommodation_type = st.selectbox(
        "Accommodation Type",
        ["hotel", "hostel", "apartment", "bnb", "camping"]
    )

    st.markdown("---")
    generate_button = st.button("🚀 Generate My Trip", use_container_width=True)

# Main content area
if generate_button:
    if not interests:
        st.error("⚠️ Please select at least one interest!")
    else:
        # Show loading animation
        loading_placeholder = st.empty()
        progress_container = st.empty()

        with loading_placeholder.container():
            st.markdown("""
            <div class="loading-container">
                <div class="plane-animation">✈️</div>
                <div class="loading-text">Crafting your perfect itinerary...</div>
                <p style="color: #666; margin-top: 10px;">This may take a few moments</p>
            </div>
            """, unsafe_allow_html=True)

        # Progress messages
        progress_messages = [
            "🔍 Analyzing destinations...",
            "🏨 Finding the best accommodations...",
            "🍽️ Discovering local cuisine...",
            "🎭 Curating experiences...",
            "✨ Finalizing your itinerary..."
        ]

        try:
            # Initialize travel agent
            travel_agent = init_travel_agent()

            # Prepare input state
            input_state = {
                "country": country,
                "interests": interests,
                "departure_date": departure_date.strftime("%Y-%m-%d"),
                "return_date": return_date.strftime("%Y-%m-%d"),
                "travel_style": travel_style,
                "trip_type": trip_type,
                "age_group": age_group,
                "accommodation_type": accommodation_type,
                "final_trip": "",
                "search_results": ""
            }

            # Show progress
            with progress_container.container():
                progress_bar = st.progress(0)
                status_text = st.empty()

                for i, msg in enumerate(progress_messages):
                    status_text.info(msg)
                    progress_bar.progress((i + 1) / len(progress_messages))
                    
                    # Run the graph if we're at the start
                    if i == 0:
                        result = travel_agent.invoke(input_state)

            # Clear loading animations
            loading_placeholder.empty()
            progress_container.empty()

            # Store result
            st.session_state.trip_result = result.get('final_trip', str(result))
            st.session_state.trip_generated = True

            # Display success message
            st.success("🎉 Your trip has been generated!")

            # Display the trip
            st.markdown("## 🗺️ Your Personalized Itinerary")

            # Show trip details in an attractive format
            with st.container():
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🌍 Destination", country.title())
                with col2:
                    st.metric("📅 Duration", f"{(return_date - departure_date).days} days")
                with col3:
                    st.metric("💎 Style", travel_style.title())
                with col4:
                    st.metric("👥 Trip Type", trip_type.title())

            st.markdown("---")

            # Display the generated trip with better formatting
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
                        padding: 30px; 
                        border-radius: 15px; 
                        border-left: 5px solid #667eea;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                {st.session_state.trip_result}
            </div>
            """, unsafe_allow_html=True)

            # Download button
            trip_data = {
                "destination": country,
                "dates": {
                    "departure": departure_date.strftime("%Y-%m-%d"),
                    "return": return_date.strftime("%Y-%m-%d")
                },
                "preferences": {
                    "travel_style": travel_style,
                    "trip_type": trip_type,
                    "age_group": age_group,
                    "accommodation_type": accommodation_type,
                    "interests": interests
                },
                "itinerary": st.session_state.trip_result
            }
            trip_json = json.dumps(trip_data, indent=2)
            st.download_button(
                label="📥 Download Trip Details",
                data=trip_json,
                file_name=f"trip_{country.lower().replace(' ', '_')}_{departure_date.strftime('%Y%m%d')}.json",
                mime="application/json"
            )

        except Exception as e:
            loading_placeholder.empty()
            progress_container.empty()
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("💡 Make sure your API keys are properly set in your .env file")

# Show previous result if exists
elif st.session_state.trip_generated and st.session_state.trip_result:
    st.markdown("## 🗺️ Your Last Generated Trip")
    st.info("👈 Modify your preferences in the sidebar and generate a new trip!")

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
                padding: 30px; 
                border-radius: 15px; 
                border-left: 5px solid #667eea;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        {st.session_state.trip_result}
    </div>
    """, unsafe_allow_html=True)

    trip_json = json.dumps({"itinerary": st.session_state.trip_result}, indent=2)
    st.download_button(
        label="📥 Download Trip Details",
        data=trip_json,
        file_name="trip_details.json",
        mime="application/json"
    )

else:
    # Welcome screen
    st.markdown("""
    ### Welcome to AI Trip Planner! 🌍

    Let our AI assistant create a personalized travel itinerary just for you.

    #### How it works:
    1. 👈 Fill in your preferences in the sidebar
    2. 🚀 Click "Generate My Trip"
    3. ✨ Get your customized itinerary in moments

    #### Features:
    - 🎯 Personalized recommendations based on your interests
    - 🏨 Accommodation suggestions matching your style
    - 🍽️ Local cuisine and dining recommendations
    - 🎭 Activities and experiences tailored to your age group
    - 📅 Optimized daily schedules

    **Ready to start planning?** Configure your trip settings in the sidebar!
    """)

    # Add some emoji decorations
    st.markdown("---")
    cols = st.columns(5)
    emojis = ["🏖️", "🏔️", "🍕", "🎭", "🎨"]
    labels = ["Beaches", "Mountains", "Food", "Culture", "Arts"]

    for col, emoji, label in zip(cols, emojis, labels):
        with col:
            st.markdown(f"<div style='text-align: center; font-size: 48px;'>{emoji}</div>", unsafe_allow_html=True)

            st.markdown(f"<div style='text-align: center; color: #666;'>{label}</div>", unsafe_allow_html=True)
