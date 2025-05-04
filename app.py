import os
import uvicorn
import asyncio
import logging
import streamlit as st
import requests
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from serpapi import GoogleSearch
from crewai import Agent, Task, Crew, Process, LLM
from functools import lru_cache
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from datetime import datetime

load_dotenv()

# Load API Keys
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
SERP_API_KEY = os.getenv("SERPER_API_KEY")

# Initialize Logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def initialize_llm():
    """Initialize and cache the LLM instance to avoid repeated initializations."""
    return LLM(
        model="gemini/gemini-2.0-flash",
        provider="google",
        api_key=GEMINI_API_KEY
    )


class FlightClassInfo:
    def __init__(self, departure_airport, arrival_airport, duration, airplane, airline, airline_logo, travel_class, flight_number, legroom, extensions):
        self.departure_airport = departure_airport
        self.arrival_airport = arrival_airport
        self.duration = duration
        self.airplane = airplane
        self.airline = airline
        self.airline_logo = airline_logo
        self.travel_class = travel_class
        self.flight_number = flight_number
        self.legroom = legroom
        self.extensions = extensions

class HotelClassInfo:
    def __init__(self, name, description, rate_per_night, hotel_class, overall_rating, amenities, address=None):
        self.name = name
        self.description = description
        self.rate_per_night = rate_per_night
        self.hotel_class = hotel_class
        self.overall_rating = overall_rating
        self.amenities = amenities
        self.address = address  # optional

class FlightRequest(BaseModel):
    origin: str
    destination: str
    outbound_date: str
    return_date: str
    type: str

class HotelRequest(BaseModel):
    location: str
    check_in_date: str
    check_out_date: str

class ItineraryRequest(BaseModel):
    destination: str
    check_in_date: str
    check_out_date: str
    flights: str
    hotels: str

class FlightInfo(BaseModel):
    airline: str
    price: str
    duration: str
    stops: str
    departure: str
    arrival: str
    travel_class: str
    return_date: str
    airline_logo: str

class HotelInfo(BaseModel):
    name: str
    price: str
    rating: float
    location: str
    link: str

class AIResponse(BaseModel):
    flights: List[FlightInfo] = []
    hotels: List[HotelInfo] = []
    ai_flight_recommendation: str = ""
    ai_hotel_recommendation: str = ""
    itinerary: str = ""


app = FastAPI(title="Travel Planning API", version="1.0.1")


def parse_hotel_info_list(hotel_data_list: List[dict], location: str = "Unknown") -> List[HotelInfo]:
    parsed_hotels = []
    for hotel_data in hotel_data_list:
        if not isinstance(hotel_data, dict):
            logger.warning(f"Skipping non-dict hotel_data: {hotel_data}")
            continue
        parsed_hotels.append(
            HotelInfo(
                name=hotel_data.get("name", "No name"),
                link=hotel_data.get("link") or hotel_data.get("serpapi_property_details_link", ""),
                location=location,
                price=str(hotel_data.get("rate_per_night", {}).get("extracted_lowest", "0")),
                rating=hotel_data.get("overall_rating") or 0.0
            )
        )
    return parsed_hotels

def parse_flight_object(data: Dict, return_date: Optional[str] = "") -> FlightInfo:
    flights = data.get("flights", [])
    layovers = data.get("layovers", [])

    # Airline and logo from the first flight (can be extended for multi-leg)
    airline = flights[0]["airline"] if flights else "N/A"
    airline_logo = flights[0]["airline_logo"] if flights else ""

    # Price and duration
    price = f"${data.get('price', 'N/A')}"
    total_flight_duration = sum(flight.get("duration", 0) for flight in flights)

    # Stops information
    stops = f"{len(layovers)} stop(s)" if layovers else "Non-stop"

    # Departure and Arrival
    if flights:
        departure_airport = flights[0]["departure_airport"]
        arrival_airport = flights[-1]["arrival_airport"]
        departure = f"{departure_airport['id']} - {departure_airport['name']}"
        arrival = f"{arrival_airport['id']} - {arrival_airport['name']}"
    else:
        departure = "N/A"
        arrival = "N/A"

    # Travel class
    travel_class = flights[0].get("travel_class", "N/A") if flights else "N/A"

    # Return date (only if type is not one-way)
    flight_type = data.get("type", "oneway").lower()
    return_date_val = return_date if flight_type != "oneway" else "N/A"

    return FlightInfo(
        airline=airline,
        price=price,
        duration=f"{total_flight_duration} minutes",
        stops=stops,
        departure=departure,
        arrival=arrival,
        travel_class=travel_class,
        return_date=return_date_val,
        airline_logo=airline_logo
    )

def parse_all_flights(response: Dict, return_date: Optional[str] = "") -> List[FlightInfo]:
    best_flights = [parse_flight_object(flight, return_date) for flight in response.get("best_flights", [])]
    other_flights = [parse_flight_object(flight, return_date) for flight in response.get("other_flights", [])]
    all_flights = best_flights + other_flights
    return all_flights


async def run_search(params):
    """Generic function to run SerpAPI searches asynchronously."""
    try:
        return await asyncio.to_thread(lambda: GoogleSearch(params).get_dict())
    except Exception as e:
        logger.exception(f"SerpAPI search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search API error: {str(e)}")

async def search_flights(flight_request: FlightRequest):
    """Fetch real-time flight details from Google Flights using SerpAPI."""
    logger.info(f"Searching flights: {flight_request.origin} to {flight_request.destination}")

    params = {
        "api_key": SERP_API_KEY,
        "engine": "google_flights",
        "type": flight_request.type,
        "hl": "en",
        "gl": "in",
        "departure_id": flight_request.origin.strip().upper(),
        "arrival_id": flight_request.destination.strip().upper(),
        "outbound_date": flight_request.outbound_date,
        "return_date": flight_request.return_date,
        "currency": "USD",

    }
    logger.info(params)
    search_results = await run_search(params)
    flights = search_results
    return flights

async def search_hotels(hotel_request: HotelRequest):
    """Fetch hotel information from SerpAPI."""
    logger.info(f"Searching hotels for: {hotel_request.location}")

    params = {
        "api_key": SERP_API_KEY,
        "engine": "google_hotels",
        "q": hotel_request.location,
        "hl": "en",
        "gl": "in",
        "check_in_date": hotel_request.check_in_date,
        "check_out_date": hotel_request.check_out_date,
        "currency": "USD",
        "sort_by": 3,
        "rating": 8
    }

    search_results = await run_search(params)
    hotels = search_results.get("properties")
    return hotels

async def get_ai_recommendation(data_type, formatted_data):
    logger.info(f"Getting {data_type} analysis from AI")
    logger.info(formatted_data)
    llm_model = initialize_llm()

    # Configure agent based on data type
    if data_type == "flights":
        role = "AI Flight Analyst"
        goal = "Analyze flight options and recommend the best one considering price, duration, stops, and overall convenience."
        backstory = f"AI expert that provides in-depth analysis comparing flight options based on multiple factors."
        description = """
        Recommend the best flight from the available options, based on the details provided below:

        **Reasoning for Recommendation:**
        - **Price:** Provide a detailed explanation about why this flight offers the best value compared to others.
        - **Duration:** Explain why this flight has the best duration in comparison to others.
        - **Stops:** Discuss why this flight has minimal or optimal stops.
        - **Travel Class:** Describe why this flight provides the best comfort and amenities.

        Use the provided flight data as the basis for your recommendation. Be sure to justify your choice using clear reasoning for each attribute. Do not repeat the flight details in your response.
        """
    elif data_type == "hotels":
        role = "AI Hotel Analyst"
        goal = "Analyze hotel options and recommend the best one considering price, rating, location, and amenities."
        backstory = f"AI expert that provides in-depth analysis comparing hotel options based on multiple factors."
        description = """
        Based on the following analysis, generate a detailed recommendation for the best hotel. Your response should include clear reasoning based on price, rating, location, and amenities.

        **AI Hotel Recommendation**
        We recommend the best hotel based on the following analysis:

        **Reasoning for Recommendation**:
        - **Price:** The recommended hotel is the best option for the price compared to others, offering the best value for the amenities and services provided.
        - **Rating:** With a higher rating compared to the alternatives, it ensures a better overall guest experience. Explain why this makes it the best choice.
        - **Location:** The hotel is in a prime location, close to important attractions, making it convenient for travelers.
        - **Amenities:** The hotel offers amenities like Wi-Fi, pool, fitness center, free breakfast, etc. Discuss how these amenities enhance the experience, making it suitable for different types of travelers.

        **Reasoning Requirements**:
        - Ensure that each section clearly explains why this hotel is the best option based on the factors of price, rating, location, and amenities.
        - Compare it against the other options and explain why this one stands out.
        - Provide concise, well-structured reasoning to make the recommendation clear to the traveler.
        - Your recommendation should help a traveler make an informed decision based on multiple factors, not just one.
        """
    else:
        raise ValueError("Invalid data type for AI recommendation")

    # Create the agent and task
    analyze_agent = Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        llm=llm_model,
        verbose=False
    )

    analyze_task = Task(
        description=f"{description}\n\nData to analyze:\n{formatted_data}",
        agent=analyze_agent,
        expected_output=f"A structured recommendation explaining the best {data_type} choice based on the analysis of provided details."
    )

    # Define CrewAI Workflow for the agent
    analyst_crew = Crew(
        agents=[analyze_agent],
        tasks=[analyze_task],
        process=Process.sequential,
        verbose=False
    )

    # Execute CrewAI Process
    crew_results = await asyncio.to_thread(analyst_crew.kickoff)
    return str(crew_results)

async def generate_itinerary(destination, flights_text, hotels_text, check_in_date, check_out_date):
    """Generate a detailed travel itinerary based on flight and hotel information."""
    try:
        # Convert the string dates to datetime objects
        check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
        check_out = datetime.strptime(check_out_date, "%Y-%m-%d")

        # Calculate the difference in days
        days = (check_out - check_in).days

        llm_model = initialize_llm()

        analyze_agent = Agent(
            role="AI Travel Planner",
            goal="Create a detailed itinerary for the user based on flight and hotel information",
            backstory="AI travel expert generating a day-by-day itinerary including flight details, hotel stays, and must-visit locations in the destination.",
            llm=llm_model,
            verbose=False
        )

        analyze_task = Task(
            description=f"""
            Based on the following details, create a {days}-day itinerary for the user:

            **Flight Details**:
            {flights_text}

            **Hotel Details**:
            {hotels_text}

            **Destination**: {destination}

            **Travel Dates**: {check_in_date} to {check_out_date} ({days} days)

            The itinerary should include:
            - Flight arrival and departure information
            - Hotel check-in and check-out details
            - Day-by-day breakdown of activities
            - Must-visit attractions and estimated visit times
            - Restaurant recommendations for meals
            - Tips for local transportation

            **Format Requirements**:
            - Use markdown formatting with clear headings (# for main headings, ## for days, ### for sections)
            - Include emojis for different types of activities ( for landmarks, 🍽️ for restaurants, etc.)
            - Use bullet points for listing activities
            - Include estimated timings for each activity
            - Format the itinerary to be visually appealing and easy to read
            """,
            agent=analyze_agent,
            expected_output="A well-structured, visually appealing itinerary in markdown format, including flight, hotel, and day-wise breakdown with emojis, headers, and bullet points."
        )

        itinerary_planner_crew = Crew(
            agents=[analyze_agent],
            tasks=[analyze_task],
            process=Process.sequential,
            verbose=False
        )

        crew_results = await asyncio.to_thread(itinerary_planner_crew.kickoff)
        return str(crew_results)

    except Exception as e:
        return f"An error occurred: {e}"

@app.post("/search_flights/", response_model=AIResponse)
async def get_flight_recommendations(flight_request: FlightRequest):
    flights = await search_flights(flight_request)
    logger.info(flights)
    flights_text = parse_all_flights(flights, flight_request.return_date)
    ai_recommendation = await get_ai_recommendation("flights", flights_text)
    return AIResponse(flights=flights_text, ai_flight_recommendation=ai_recommendation)

@app.post("/search_hotels/", response_model=AIResponse)
async def get_hotel_recommendations(hotel_request: HotelRequest):
    hotels = await search_hotels(hotel_request)
    logger.info(hotels)
    hotels_text = parse_hotel_info_list(hotels, hotel_request.location)
    ai_recommendation = await get_ai_recommendation("hotels", hotels_text)
    return AIResponse(hotels=hotels_text, ai_hotel_recommendation=ai_recommendation)

@app.post("/generate_itinerary/", response_model=AIResponse)
async def get_itinerary(itinerary_request: ItineraryRequest):
    itinerary = await generate_itinerary(
        itinerary_request.destination,
        itinerary_request.flights,
        itinerary_request.hotels,
        itinerary_request.check_in_date,
        itinerary_request.check_out_date
    )
    return AIResponse(itinerary=itinerary)

# Run FastAPI Server
if __name__ == "__main__":
    logger.info("Starting Travel Planning API server")
    uvicorn.run(app, host="0.0.0.0", port=8000)


# API URLs
API_BASE_URL = "http://localhost:8000"
API_URL_FLIGHTS = f"{API_BASE_URL}/search_flights/"
API_URL_HOTELS = f"{API_BASE_URL}/search_hotels/"
API_URL_COMPLETE = f"{API_BASE_URL}/complete_search/"
API_URL_ITINERARY = f"{API_BASE_URL}/generate_itinerary/"