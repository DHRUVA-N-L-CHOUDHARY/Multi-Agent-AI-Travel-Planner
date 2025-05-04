import streamlit as st
import requests
import re
from datetime import datetime

def clean_raw_markdown_string(raw_text: str) -> str:

    raw_text = re.sub(r"^```markdown\n|```$", "", raw_text.strip(), flags=re.DOTALL)

    clean_text = raw_text.encode('utf-8').decode('unicode_escape')

    return clean_text.strip()


def fix_unicode_issues(text: str) -> str:
    return text.encode('latin1').decode('utf-8', 'ignore')


# API URLs
API_BASE_URL = "https://multi-agent-ai-travel-planner.onrender.com:8000"
API_URL_FLIGHTS = f"{API_BASE_URL}/search_flights/"
API_URL_HOTELS = f"{API_BASE_URL}/search_hotels/"
API_URL_ITINERARY = f"{API_BASE_URL}/generate_itinerary/"

st.set_page_config(layout="wide")
st.title("✈️🏨 AI-Powered Travel Planner")
st.markdown("Find flights, hotels, and generate a smart itinerary – all in one place!")

# Tabs
tabs = st.tabs(["✈️ Search Flights", "🏨 Search Hotels", "🗺️ Generate Itinerary"])

# --- Flights Tab ---
with tabs[0]:
    st.subheader("✈️ Flight Details")
    departure_airport = st.text_input("DEPARTURE AIRPORT (IATA CODE)", value="BLR", key="dep_airport")
    destination_airport = st.text_input("DESTINATION AIRPORT (IATA CODE)", value="HYD", key="dest_airport")
    departure_date = st.date_input("DEPARTURE DATE", value=datetime.strptime("2025-03-10", "%Y-%m-%d"), key="dep_date")
    return_date = st.date_input("RETURN DATE", value=datetime.strptime("2025-03-17", "%Y-%m-%d"), key="ret_date")

    if st.button("🔍 Search Flights"):
        flight_request = {
            "origin": departure_airport,
            "destination": destination_airport,
            "outbound_date": departure_date.strftime("%Y-%m-%d"),
            "return_date": return_date.strftime("%Y-%m-%d"),
            "type": "1"
        }

        try:
            response = requests.post(API_URL_FLIGHTS, json=flight_request)
            response.raise_for_status()
            flight_data = response.json()

            st.subheader("Flight Results")
            flights = flight_data.get("flights", [])
            if flights:
                for flight in flights:
                    flight.pop("airline_logo", None)
                st.dataframe(flights, use_container_width=True)
            else:
                st.warning("No flights found.")

            raw_text = flight_data.get("ai_flight_recommendation", "No recommendation available.")
            parsed_md = clean_raw_markdown_string(raw_text)
            fixed_md = fix_unicode_issues(parsed_md)
            highlighted_md = f"""
            <div style="border: 3px solid #FF6347; padding: 20px; background-color: #FFF0F5; border-radius: 10px; color: black;">
            <h2 style="color: #FF6347;">🏨 AI Recommendation:</h2>
            <p style="font-size: 16px; color: black;">
            {fixed_md}
             </p>
            </div>
            """
            st.markdown(highlighted_md, unsafe_allow_html=True)

        except requests.exceptions.RequestException as e:
            st.error(f"Error searching flights: {str(e)}")

# --- Hotels Tab ---
with tabs[1]:
    st.subheader("🏨 Hotel Details")
    hotel_location = st.text_input("HOTEL LOCATION", value="Bangalore", key="hotel_loc")
    check_in_date = st.date_input("CHECK IN DATE", value=datetime.strptime("2025-03-10", "%Y-%m-%d"), key="in_date")
    check_out_date = st.date_input("CHECK OUT DATE", value=datetime.strptime("2025-03-17", "%Y-%m-%d"), key="out_date")

    if st.button("🔍 Search Hotels"):
        hotel_request = {
            "location": hotel_location,
            "check_in_date": check_in_date.strftime("%Y-%m-%d"),
            "check_out_date": check_out_date.strftime("%Y-%m-%d")
        }

        try:
            response = requests.post(API_URL_HOTELS, json=hotel_request)
            response.raise_for_status()
            hotel_data = response.json()

            st.subheader("Hotel Results")
            hotels = hotel_data.get("hotels", [])
            if hotels:
                st.dataframe(hotels, use_container_width=True)
            else:
                st.warning("No hotels found.")

            raw_text = hotel_data.get("ai_hotel_recommendation", "No recommendation available.")
            parsed_md = clean_raw_markdown_string(raw_text)
            fixed_md = fix_unicode_issues(parsed_md)
            highlighted_md = f"""
            <div style="border: 3px solid #FF6347; padding: 20px; background-color: #FFF0F5; border-radius: 10px; color: black;">
            <h2 style="color: #FF6347;">🏨 AI Recommendation:</h2>
            <p style="font-size: 16px; color: black;">
            {fixed_md}
             </p>
            </div>
            """
            st.markdown(highlighted_md, unsafe_allow_html=True)

        except requests.exceptions.RequestException as e:
            st.error(f"Error searching hotels: {str(e)}")

# --- Generate Itinerary Tab ---
with tabs[2]:
    st.subheader("🗺️ Generate Itinerary")
    destination = st.text_input("Destination", value="Hyderabad", key="itinerary_dest")

    itinerary_flights = st.text_area("Paste your selected flight details (JSON format)", height=100)
    itinerary_hotels = st.text_area("Paste your selected hotel details (JSON format)", height=100)

    itinerary_checkin = st.date_input("Check-in Date", value=datetime.strptime("2025-03-10", "%Y-%m-%d"))
    itinerary_checkout = st.date_input("Check-out Date", value=datetime.strptime("2025-03-17", "%Y-%m-%d"))

    if st.button("🧠 Generate Itinerary"):
        try:
            request_body = {
                "destination": destination,
                "flights": itinerary_flights,   # use json.loads() instead for production!
                "hotels": itinerary_hotels,
                "check_in_date": itinerary_checkin.strftime("%Y-%m-%d"),
                "check_out_date": itinerary_checkout.strftime("%Y-%m-%d")
            }

            response = requests.post(API_URL_ITINERARY, json=request_body)
            response.raise_for_status()
            itinerary_data = response.json()
            raw_text = itinerary_data.get("itinerary", "No itinerary generated.")
            parsed_md = clean_raw_markdown_string(raw_text)
            fixed_md = fix_unicode_issues(parsed_md)
            highlighted_md = f"""
            <div style="border: 3px solid #FF6347; padding: 20px; background-color: #FFF0F5; border-radius: 10px; color: black;">
            <h2 style="color: #FF6347;">📝 AI Generated Itinerary</h2>
            <p style="font-size: 16px; color: black;">
            {fixed_md}
             </p>
            </div>
            """
            st.markdown(highlighted_md, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Failed to generate itinerary: {e}")
