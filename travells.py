import streamlit as st
from pymongo import MongoClient
import pandas as pd
from bson import ObjectId

# -----------------------------
# MongoDB CONNECTION
# -----------------------------
MONGO_URI = st.secrets.get("MONGO_URI", "mongodb://localhost:27017")  # Use Atlas URI in deployment
client = MongoClient(MONGO_URI)
db = client["travelDB"]
trips_collection = db["trips"]
bookings_collection = db["bookings"]

# -----------------------------
# Helper Functions
# -----------------------------
def get_trips(destination=None):
    query = {}
    if destination:
        query["destination"] = {"$regex": destination, "$options": "i"}
    return list(trips_collection.find(query))

def add_booking(name, email, trip_id):
    trip = trips_collection.find_one({"_id": ObjectId(trip_id)})
    if not trip:
        return False
    booking = {
        "name": name,
        "email": email,
        "trip_id": str(trip_id),
        "destination": trip["destination"],
        "price": trip["price"],
        "date": trip["date"]
    }
    bookings_collection.insert_one(booking)
    return True

def get_all_bookings():
    return list(bookings_collection.find())

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="🌍 Travel Booking App", layout="wide")

st.title("🌍 Travel Booking System")

menu = st.sidebar.radio("Menu", ["Search Trips", "Book a Trip", "Admin - View Bookings"])

# -----------------------------
# SEARCH TRIPS
# -----------------------------
if menu == "Search Trips":
    st.subheader("🔍 Search Available Trips")
    destination = st.text_input("Enter destination name")
    if st.button("Search"):
        trips = get_trips(destination)
        if trips:
            df = pd.DataFrame(trips)
            df["_id"] = df["_id"].astype(str)
            df = df[["_id", "destination", "price", "date", "description"]]
            st.dataframe(df)
        else:
            st.warning("No trips found!")

# -----------------------------
# BOOK A TRIP
# -----------------------------
elif menu == "Book a Trip":
    st.subheader("✈️ Book Your Trip")

    trips = get_trips()
    if not trips:
        st.warning("No trips available!")
    else:
        trip_options = {f"{t['destination']} - ${t['price']} ({t['date']})": str(t["_id"]) for t in trips}
        selected_trip = st.selectbox("Select a Trip", list(trip_options.keys()))

        name = st.text_input("Full Name")
        email = st.text_input("Email Address")

        if st.button("Confirm Booking"):
            if not name or not email or not selected_trip:
                st.error("Please fill out all fields before booking.")
            else:
                success = add_booking(name, email, trip_options[selected_trip])
                if success:
                    st.success("✅ Booking confirmed! Enjoy your trip! 🎉")
                else:
                    st.error("⚠️ Trip not found, please try again.")

# -----------------------------
# ADMIN - VIEW BOOKINGS
# -----------------------------
elif menu == "Admin - View Bookings":
    st.subheader("🧾 All Bookings")

    bookings = get_all_bookings()
    if bookings:
        df = pd.DataFrame(bookings)
        df["_id"] = df["_id"].astype(str)
        df = df[["name", "email", "destination", "price", "date", "trip_id"]]
        st.dataframe(df)
    else:
        st.info("No bookings found yet.")
travell