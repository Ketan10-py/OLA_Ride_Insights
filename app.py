import streamlit as st
import pandas as pd
import sqlite3
import os

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="OLA Rides Dashboard", layout="wide")

# OLA THEME COLORS
OLA_YELLOW = "#FFD600"
OLA_BLACK = "#212121"
OLA_GREEN = "#00B050"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {OLA_BLACK};
        color: white;
        font-family: 'Arial', sans-serif;
    }}
    .metric-card {{
        background-color: #2C2C2C;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.5);
        margin: 10px;
    }}
    .metric-card h3 {{
        color: {OLA_YELLOW};
        margin: 0;
    }}
    .metric-card p {{
        font-size: 22px;
        font-weight: bold;
        margin: 0;
        color: {OLA_GREEN};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# LOAD DATA
# ---------------------------
@st.cache_data
def load_data():
    # Update with your actual file path
    file_path = r"C:\Users\bajpa\OneDrive\Desktop\OLA Ride\OLA_DataSet_July.csv.csv"

    if not os.path.exists(file_path):
        st.error("⚠️ Data file not found! Please check the file path.")
        return pd.DataFrame()

    df = pd.read_csv(file_path)

    # 🔹 Standardize column names to match SQL queries
    df = df.rename(columns={
        "Ride Status": "Booking_status",
        "Trip Distance": "distance",
        "Driver Rating": "driver_rating",
        "Customer Rating": "customer_rating",
        "Payment Type": "payment_method",
        "Ride Fare": "booking_value",
        "Cancel Reason": "cancel_reason",
        "Booking ID": "booking_id",
        "Customer ID": "customer_id",
        "Driver ID": "driver_id",
        "Vehicle": "vehicle_type"
    })

    return df

df = load_data()

if not df.empty:
    # ---------------------------
    # CREATE SQLITE IN-MEMORY DB
    # ---------------------------
    conn = sqlite3.connect(":memory:")
    df.to_sql("Bookings", conn, index=False, if_exists="replace")

    # ---------------------------
    # SQL QUERIES
    # ---------------------------
    queries = {
        "1. All Successful Bookings": """SELECT * FROM Bookings WHERE Booking_status = 'Success';""",
        "2. Average Ride Distance per Vehicle": """SELECT vehicle_type, AVG(Ride_Distance) AS avg_distance FROM Bookings GROUP BY vehicle_type;""",
        "3. Cancelled Rides by Customers": """
        SELECT COUNT(*) AS cancelled_by_customers
        FROM Bookings WHERE Booking_status = 'Cancelled by Customer';
    """,
    "4. Top 5 Customers by Ride Count": """
        SELECT Customer_ID AS customer_id, COUNT(*) AS total_rides
        FROM Bookings 
        GROUP BY customer_id
        ORDER BY total_rides DESC LIMIT 5;
    """,
    "5. Rides Cancelled by Drivers (Personal/Car Issues)": """
        SELECT COUNT(*) AS Canceled_Rides_by_Drivers
        FROM Bookings
        WHERE Booking_status = 'Canceled by Driver'
          AND Incomplete_Rides_Reason IN ('Customer Demand', 'Vehicle Breakdown');
    """,
    "6. Max & Min Driver Ratings (Prime Sedan)": """
        SELECT MAX(driver_ratings) AS max_rating,
               MIN(driver_ratings) AS min_rating
        FROM Bookings WHERE vehicle_type = 'Prime Sedan';
    """,
    "7. UPI Payments": """
        SELECT * FROM Bookings WHERE payment_method = 'UPI';
    """,
    "8. Average Customer Rating per Vehicle": """
        SELECT Vehicle_Type, AVG(Customer_Rating) AS avg_customer_rating
        FROM Bookings GROUP BY Vehicle_Type;
    """,
    "9. Total Booking Value (Successful Rides)": """
        SELECT SUM(Booking_Value) AS total_successful_value
        FROM Bookings WHERE Booking_status = 'Success';
    """,
    "10. Incomplete Rides with Reason": """
        SELECT booking_id, customer_id, Incomplete_Rides_Reason
        FROM Bookings WHERE Booking_status = 'Canceled by Driver';
    """
    }

    # ---------------------------
    # HEADER WITH LOGO
    # ---------------------------
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        st.image("Ola-Cabs-Logo.png", width=200)
    with col2:
        st.title("OLA Rides Dashboard 🚖")
        st.markdown("### Ride Analytics · Revenue · Customer Insights")

    st.markdown("---")

    # ---------------------------
    # QUERY SELECTION
    # ---------------------------
    choice = st.selectbox("🔎 Select Query", list(queries.keys()))
    sql = queries[choice]

    result = pd.read_sql(sql, conn)
    st.dataframe(result, use_container_width=True)



