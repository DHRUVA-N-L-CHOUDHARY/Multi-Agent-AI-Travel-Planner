import streamlit as st
import requests
from datetime import datetime

# API URLs
API_BASE_URL = "http://localhost:8000"
API_URL_FLIGHTS = f"{API_BASE_URL}/search_flights/"
API_URL_HOTELS = f"{API_BASE_URL}/search_hotels/"

# Set page title
st.set_page_config(layout="wide")
st.title("AI-Powered Travel Planner")
st.write("Find flights, hotels, get personalized recommendations with AI! Create your perfect travel itinerary in seconds.")

# Device Width Detection using st.sidebar as workaround (Streamlit doesn’t have native screen size detection yet)
if "layout_mode" not in st.session_state:
    st.session_state.layout_mode = "Side-by-side"

layout_mode = st.radio("View Mode", ["Side-by-side", "Tabbed (Mobile)"], horizontal=True)

if layout_mode == "Side-by-side":
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("✈️ Flight Details")
        departure_airport = st.text_input("DEPARTURE AIRPORT (IATA CODE)", value="BLR", key="dep_airport")
        destination_airport = st.text_input("DESTINATION AIRPORT (IATA CODE)", value="HYD", key="dest_airport")
        departure_date = st.date_input("DEPARTURE DATE", value=datetime.strptime("2025-03-10", "%Y-%m-%d"), key="dep_date")
        return_date = st.date_input("RETURN DATE", value=datetime.strptime("2025-03-17", "%Y-%m-%d"), key="ret_date")

        if st.button("Search Flights"):
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
                st.write("**Available Flights:**")
                flights = flight_data.get("flights", [])
                if flights:
                    for flight in flights:
                        flight.pop("airline_logo", None)
                    st.dataframe(flights, use_container_width=True)
                else:
                    st.warning("No flights found.")

                st.write("**✈️ AI Recommendation:**")
                st.markdown(flight_data.get("ai_flight_recommendation", "No recommendation available."))

            except requests.exceptions.RequestException as e:
                st.error(f"Error searching flights: {str(e)}")

    with col2:
        st.subheader("🏨 Hotel Details")
        hotel_location = st.text_input("HOTEL LOCATION", value="Bangalore", key="hotel_loc")
        check_in_date = st.date_input("CHECK IN DATE", value=datetime.strptime("2025-03-10", "%Y-%m-%d"), key="in_date")
        check_out_date = st.date_input("CHECK OUT DATE", value=datetime.strptime("2025-03-17", "%Y-%m-%d"), key="out_date")

        if st.button("Search Hotels"):
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
                st.write("**Available Hotels:**")
                hotels = hotel_data.get("hotels", [])
                if hotels:
                # Display the table
                         st.dataframe(hotels, use_container_width=True)
                else:
                         st.warning("No hotels found.")
                st.write("**AI Recommendation:**")
                st.markdown(hotel_data.get("ai_hotel_recommendation", "No recommendation available."))

            except requests.exceptions.RequestException as e:
                st.error(f"Error searching hotels: {str(e)}")

else:
    tab = st.radio("Select a section", ["✈️ Flights", "🏨 Hotels"], horizontal=True)

    if tab == "✈️ Flights":
        st.subheader("✈️ Flight Details")
        departure_airport = st.text_input("DEPARTURE AIRPORT (IATA CODE)", value="BLR")
        destination_airport = st.text_input("DESTINATION AIRPORT (IATA CODE)", value="HYD")
        departure_date = st.date_input("DEPARTURE DATE", value=datetime.strptime("2025-03-10", "%Y-%m-%d"))
        return_date = st.date_input("RETURN DATE", value=datetime.strptime("2025-03-17", "%Y-%m-%d"))

        if st.button("Search Flights"):
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
                st.write("**Available Flights:**")
                flights = flight_data.get("flights", [])
                if flights:
                    for flight in flights:
                        flight.pop("airline_logo", None)
                    st.dataframe(flights, use_container_width=True)
                else:
                    st.warning("No flights found.")

                st.write("**✈️ AI Recommendation:**")
                st.markdown(flight_data.get("ai_flight_recommendation", "No recommendation available."))

            except requests.exceptions.RequestException as e:
                st.error(f"Error searching flights: {str(e)}")

    elif tab == "🏨 Hotels":
        st.subheader("🏨 Hotel Details")
        hotel_location = st.text_input("HOTEL LOCATION", value="Bangalore")
        check_in_date = st.date_input("CHECK IN DATE", value=datetime.strptime("2025-03-10", "%Y-%m-%d"))
        check_out_date = st.date_input("CHECK OUT DATE", value=datetime.strptime("2025-03-17", "%Y-%m-%d"))

        if st.button("Search Hotels"):
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
                st.write("**Available Hotels:**")
                hotels = hotel_data.get("hotels", [])
                if hotels:
                # Display the table
                         st.dataframe(hotels, use_container_width=True)
                else:
                         st.warning("No hotels found.")

                st.write("**AI Recommendation:**")
                st.markdown(hotel_data.get("ai_hotel_recommendation", "No recommendation available."))

            except requests.exceptions.RequestException as e:
                st.error(f"Error searching hotels: {str(e)}")