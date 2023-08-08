import streamlit as st
import pandas as pd
import joblib
from opencage.geocoder import OpenCageGeocode
from geopy.distance import geodesic

# Load the trained model
model = joblib.load('nyc_taxi_model.pkl')

# Initialize OpenCageData geocoder
geocoder = OpenCageGeocode("f07647291ffc4d259ce67ab13ca530b5")  # Replace with your OpenCageData API key

# Create a function to calculate distances
def calculate_distance(coord1, coord2):
    return geodesic(coord1, coord2).kilometers

# Create a function to get coordinates from place names using OpenCageData
def get_coordinates(place_name):
    result = geocoder.geocode(place_name)
    if result and len(result):
        lat = result[0]['geometry']['lat']
        lon = result[0]['geometry']['lng']
        return lat, lon
    return None

# Create the Streamlit app
st.title('NYC Taxi Fare Prediction')

st.sidebar.header('User Inputs')

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
    
    # Make predictions using the loaded model
    prediction = model.predict(input_data)
    
    st.write(f'Predicted Fare Amount: ${prediction[0]:.2f}')
else:
    st.write('Invalid location names. Please provide valid names.')
