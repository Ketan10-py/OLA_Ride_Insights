import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
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
    file_path = "OLA_DataSet_July.csv.csv"  
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
    else:
        st.error("⚠️ Data file not found! Make sure 'OLA_DataSet_July.csv' is in repo root.")
        return pd.DataFrame()

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

    # Ensure lowercase for consistency
    df.columns = df.columns.str.lower()
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
        "1. All Successful Bookings": """
            SELECT * FROM Bookings WHERE ride_status = 'Success';
        """,
        "2. Average Ride Distance per Vehicle": """
            SELECT vehicle_type, AVG(trip_distance) AS avg_distance 
            FROM Bookings GROUP BY vehicle_type;
        """,
        "3. Cancelled Rides by Customers": """
            SELECT COUNT(*) AS cancelled_by_customers
            FROM Bookings WHERE ride_status = 'Cancelled by Customer';
        """,
        "4. Top 5 Customers by Ride Count": """
            SELECT customer_id, COUNT(*) AS total_rides
            FROM Bookings 
            GROUP BY customer_id
            ORDER BY total_rides DESC LIMIT 5;
        """,
        "5. Rides Cancelled by Drivers (Personal/Car Issues)": """
            SELECT COUNT(*) AS cancelled_by_drivers
            FROM Bookings
            WHERE ride_status = 'Cancelled by Driver'
              AND cancel_reason IN ('Personal', 'Car Issue');
        """,
        "6. Max & Min Driver Ratings (Prime Sedan)": """
            SELECT MAX(driver_rating) AS max_rating,
                   MIN(driver_rating) AS min_rating
            FROM Bookings WHERE vehicle_type = 'Prime Sedan';
        """,
        "7. UPI Payments": """
            SELECT * FROM Bookings WHERE payment_method = 'UPI';
        """,
        "8. Average Customer Rating per Vehicle": """
            SELECT vehicle_type, AVG(customer_rating) AS avg_customer_rating
            FROM Bookings GROUP BY vehicle_type;
        """,
        "9. Total Booking Value (Successful Rides)": """
            SELECT SUM(booking_value) AS total_successful_value
            FROM Bookings WHERE ride_status = 'Success';
        """,
        "10. Incomplete Rides with Reason": """
            SELECT booking_id, customer_id, driver_id, cancel_reason
            FROM Bookings WHERE ride_status = 'Incomplete';
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

    # ---------------------------
    # AUTO CHARTS
    # ---------------------------
    fig = None
    if choice in ["2. Average Ride Distance per Vehicle", "8. Average Customer Rating per Vehicle"]:
        fig = px.bar(result, x=result.columns[0], y=result.columns[1], text_auto=True,
                     color=result.columns[0], color_discrete_sequence=[OLA_GREEN, OLA_YELLOW, "#FF7043"])
    elif choice == "4. Top 5 Customers by Ride Count":
        fig = px.bar(result, x="customer_id", y="total_rides", text_auto=True,
                     color="customer_id", color_discrete_sequence=[OLA_YELLOW])
    elif choice == "3. Cancelled Rides by Customers":
        st.metric("❌ Cancelled by Customers", result.iloc[0, 0])
    elif choice == "5. Rides Cancelled by Drivers (Personal/Car Issues)":
        st.metric("🚫 Cancelled by Drivers", result.iloc[0, 0])
    elif choice == "9. Total Booking Value (Successful Rides)":
        st.metric("💰 Total Successful Ride Value", f"₹ {result.iloc[0, 0]:,.2f}")

    if fig is not None:
        fig.update_layout(
            plot_bgcolor=OLA_BLACK,
            paper_bgcolor=OLA_BLACK,
            font=dict(color="white")
        )
        st.plotly_chart(fig, use_container_width=True)

else:
    st.stop()



