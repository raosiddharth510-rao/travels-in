import streamlit as st
from pymongo import MongoClient
import pandas as pd
from bson import ObjectId

# -----------------------------
# MongoDB CONNECTION
# -----------------------------
MONGO_URI = st.secrets.get("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["travelland"]  # changed DB name to travelland
trips_collection = db["trips"]
bookings_collection = db["bookings"]

# -----------------------------
# Add Sample Data if Empty
# -----------------------------
def seed_sample_trips():
    """Insert some default trips if collection is empty."""
    if trips_collection.count_documents({}) == 0:
        sample_trips = [
            {
                "destination": "Paris",
                "price": 1200,
                "date": "2025-12-01",
                "description": "Experience art, romance, and culture in the City of Lights."
            },
            {
                "destination": "Tokyo",
                "price": 1500,
                "date": "2025-12-15",
                "description": "Discover modern Japan blended with ancient traditions."
            },
            {
                "destination": "Bali",
                "price": 950,
                "date": "2026-01-10",
                "description": "Relax on sandy beaches and explore tropical jungles."
            },
            {
                "destination": "New York",
                "price": 1100,
                "date": "2026-02-05",
                "description": "Enjoy the energy of the Big Apple with endless attractions."
            }
        ]
        trips_collection.insert_many(sample_trips)
        print("✅ Sample trips added to database!")

# Run only once at startup
seed_sample_trips()

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
st.set_page_config(page_title="🌍 TravelLand Booking App", layout="wide")

st.title("🌍 Welcome to TravelLand Booking System")

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
