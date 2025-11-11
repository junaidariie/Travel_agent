from fastapi import  FastAPI, HTTPException
from Travel_Agent import travel_agent
from pydantic import BaseModel
from typing import Literal
from fastapi.responses import StreamingResponse

app = FastAPI(title="Travel Agent")

class Input_schema(BaseModel):
    country             : str
    interests           : list[str]
    departure_date      : str
    return_date         : str
    travel_style        : Literal["budget", "luxury", "adventure", "relaxation"]
    trip_type           : Literal["solo", "friends", "family"]
    age_group           : Literal["child", "teen", "adult", "senior"]
    accommodation_type  : Literal["hotel", "hostel", "apartment", "bnb", "camping"]

class Output_schema(BaseModel):
    final_result    : str


@app.get("/")
def Home() -> dict:
    return {"Status" : "The Travel Agent API is Live."}

@app.post("/response", response_model=Output_schema)
async def response(input_data: Input_schema):
    try:
        user_query = input_data.dict()

        result = travel_agent.invoke(user_query)

        return {"final_result": result.get("final_trip", "")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))







