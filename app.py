import streamlit as st
import pandas as pd
import joblib
from geopy.distance import geodesic
import requests

# Load the trained model
model = joblib.load('nyc_taxi_model.pkl')


# Create a function to calculate distances
def calculate_distance(coord1, coord2):
    return geodesic(coord1, coord2).kilometers

# Create a function to get coordinates from place names using the new geocoding service
def get_coordinates(place_name):
    # Define the API endpoint for forward geocoding with the specified changes
    api_endpoint = f'https://geocode.maps.co/search?q={"+".join(place_name.split())}+NY+US'
    
    # Make the API request
    response = requests.get(api_endpoint)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response to extract coordinates
        data = response.json()
        
        # Check if there are results in the response
        if data and isinstance(data, list) and len(data) > 0:
            # Pick the first result
            first_result = data[0]
            
            # Extract coordinates from the first result
            lat = float(first_result.get('lat', 0))
            lon = float(first_result.get('lon', 0))
            
            return lat, lon  # Coordinates
            
    # If the request was not successful or no valid coordinates found, return None
    return None
  
# Create the Streamlit app
st.set_page_config(
    page_title="NYC Taxi Fare Prediction",
    page_icon="🚖",
    layout="wide",
    initial_sidebar_state="auto",
)

# Custom CSS styling
st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        background-color: #f5f5f5;
    }
    .stButton > button:first-child {
        background-color: #336699;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
    }
    .stButton > button:first-child:hover {
        background-color: #204975;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Create the Streamlit app
st.title('NYC Taxi Fare Calculator')
st.markdown(
    "Predict the fare amount for a NYC taxi ride based on user inputs.")


st.sidebar.header('Inputs')

pickup_location = st.sidebar.text_input('Enter Pickup Location', 'Times Square, New York')
dropoff_location = st.sidebar.text_input('Enter Dropoff Location', 'Central Park, New York')


passenger_count = st.sidebar.number_input('Enter Passenger Count', min_value=1, max_value=10, value=1)

date = st.sidebar.date_input('Enter Date', pd.to_datetime('2023-08-08'))
time = st.sidebar.time_input('Enter Time', pd.to_datetime('12:00'))

# Combine date and time into a single DateTime object
date_time = pd.to_datetime(str(date) + ' ' + str(time))

pickup_coords = get_coordinates(pickup_location)
dropoff_coords = get_coordinates(dropoff_location)

if pickup_coords and dropoff_coords:
    st.write(f'Pickup Coordinates: {pickup_coords}')
    st.write(f'Dropoff Coordinates: {dropoff_coords}')
    
    # Calculate distance using geopy
    trip_distance = geodesic(pickup_coords, dropoff_coords).kilometers
    st.write(f'Trip Distance: {trip_distance:.2f} km')
    
    # Additional calculations for distances to famous places
    jfk_coords = (40.6413, -73.7781)
    lga_coords = (40.7769, -73.8740)
    ewr_coords = (40.6895, -74.1745)
    met_coords = (40.7794, -73.9632)
    wtc_coords = (40.7128, -74.0135)
    
    jfk_distance = calculate_distance(dropoff_coords, jfk_coords)
    lga_distance = calculate_distance(dropoff_coords, lga_coords)
    ewr_distance = calculate_distance(dropoff_coords, ewr_coords)
    met_distance = calculate_distance(dropoff_coords, met_coords)
    wtc_distance = calculate_distance(dropoff_coords, wtc_coords)

    # Explanation for including the distances to famous places
    st.write("## Why These Distances?")
    st.markdown(
    """
    We've included the distances to the following famous places in New York City because these locations often have higher surcharges due to their popularity and significance. 
    Including them as features helps our model better capture fare predictions for trips to these destinations.
    """
    )

    st.write(f'Distance to JFK Airport: {jfk_distance:.2f} km')
    st.write(f'Distance to LGA Airport: {lga_distance:.2f} km')
    st.write(f'Distance to EWR Airport: {ewr_distance:.2f} km')
    st.write(f'Distance to Metropolitan Museum: {met_distance:.2f} km')
    st.write(f'Distance to World Trade Center: {wtc_distance:.2f} km')
    
    # Extract features from date and time
    year = date_time.year
    month = date_time.month
    day = date_time.day
    day_of_week = date_time.weekday()
    week_of_year = date_time.strftime("%U")
    week_of_year= int(week_of_year)
    hour = date_time.hour
    
    # Prepare input features for prediction
    input_data = pd.DataFrame({
        'pickup_longitude': [pickup_coords[1]],
        'pickup_latitude': [pickup_coords[0]],
        'dropoff_longitude': [dropoff_coords[1]],
        'dropoff_latitude': [dropoff_coords[0]],
        'passenger_count': [passenger_count],
        'trip_distance': [trip_distance],
        'year': [year],
        'month': [month],
        'day': [day],
        'day_of_week': [day_of_week],
        'week_of_year': [week_of_year],
        'hour': [hour],
        'jfk_drop_distance': [jfk_distance],
        'lga_drop_distance': [lga_distance],
        'ewr_drop_distance': [ewr_distance],
        'met_drop_distance': [met_distance],
        'wtc_drop_distance': [wtc_distance]
    })


    # Submit button
    st.sidebar.markdown("<button type='submit'>Predict Fare</button>", unsafe_allow_html=True)

    # Make predictions using the loaded model
    prediction = model.predict(input_data)
    
    st.markdown(
        "<p style='font-size:24px; font-weight:bold; text-align:center; color:green;'>"
        f"Predicted Fare Amount: ${prediction[0]:.2f}"
        "</p>",
        unsafe_allow_html=True
    )
else:
    st.markdown(
        "<p style='font-size:24px; font-weight:bold; text-align:center; color:red;'>"
        "Invalid location names. Please provide valid names."
        "</p>",
        unsafe_allow_html=True
    )
    
hex_code_kaggle="#20beff"
# Hyperlink to Kaggle analysis
st.markdown(
    "<p style='font-size:15px; font-weight:bold; text-align:center; color: {hex_code_kaggle}; font-style: italic;'>"
    "<a href='https://www.kaggle.com/code/sridharstreaks/new-york-taxi-fare-prediction-score-3-1899' target='_blank' rel='noopener noreferrer'>View full Analysis in Kaggle</a>"
    "</p>",
    unsafe_allow_html=True
)

hex_code_github="A2A1A1"
# Hyperlink to Github repo
st.markdown(
    "<p style='font-size:15px; font-weight:bold; text-align:center; color: {hex_code_github}; font-style: italic:'>"
    "<a href='https://github.com/sridharstreaks/NYC_TaxiFare_Prediction' target='_blank' rel='noopener noreferrer'>View Github repo</a>"
    "</p>",
    unsafe_allow_html=True
)


# Footer
st.sidebar.markdown(
    """
    ---\n
    🚖 This app is for educational purposes only. Always verify actual fare amounts with taxi services.
    Also the geolocation convertor used here is a paid service and i'm using a free tier incase of the app not working properly,
    create a issue on the provided Github Repo.
    """
)
