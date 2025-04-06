import time
from typing import List, Dict, Any, Optional, Tuple
from fastapi import FastAPI, Query
from pydantic import BaseModel
import uvicorn
from difflib import get_close_matches
from geopy.distance import geodesic

# Initialize FastAPI app
app = FastAPI(
    title="Moustache Escapes Property Finder API",
    description="API for finding Moustache Escapes properties within 50km of a specified location",
    version="1.0.0"
)

# Data Models
class PropertyLocation(BaseModel):
    name: str
    latitude: float
    longitude: float

class PropertyResponse(BaseModel):
    property_name: str
    distance_km: float
    coordinates: Dict[str, float]

class PropertiesResponse(BaseModel):
    query: str
    matched_location: str
    properties_found: int
    properties: List[PropertyResponse]

# Load the property data with the exact coordinates provided
PROPERTIES = [
    {"name": "Moustache Udaipur Luxuria", "latitude": 24.57799888, "longitude": 73.68263271},
    {"name": "Moustache Udaipur", "latitude": 24.58145726, "longitude": 73.68223671},
    {"name": "Moustache Udaipur Verandah", "latitude": 24.58350565, "longitude": 73.68120777},
    {"name": "Moustache Jaipur", "latitude": 27.29124839, "longitude": 75.89630143},
    {"name": "Moustache Jaisalmer", "latitude": 27.20578572, "longitude": 70.85906998},
    {"name": "Moustache Jodhpur", "latitude": 26.30365556, "longitude": 73.03570908},
    {"name": "Moustache Agra", "latitude": 27.26156953, "longitude": 78.07524716},
    {"name": "Moustache Delhi", "latitude": 28.61257139, "longitude": 77.28423582},
    {"name": "Moustache Rishikesh Luxuria", "latitude": 30.13769036, "longitude": 78.32465767},
    {"name": "Moustache Rishikesh Riverside Resort", "latitude": 30.10216117, "longitude": 78.38458848},
    {"name": "Moustache Hostel Varanasi", "latitude": 25.2992622, "longitude": 82.99691388},
    {"name": "Moustache Goa Luxuria", "latitude": 15.6135195, "longitude": 73.75705228},
    {"name": "Moustache Koksar Luxuria", "latitude": 32.4357785, "longitude": 77.18518717},
    {"name": "Moustache Daman", "latitude": 20.41486263, "longitude": 72.83282455},
    {"name": "Panarpani Retreat", "latitude": 22.52805539, "longitude": 78.43116291},
    {"name": "Moustache Pushkar", "latitude": 26.48080513, "longitude": 74.5613783},
    {"name": "Moustache Khajuraho", "latitude": 24.84602104, "longitude": 79.93139381},
    {"name": "Moustache Manali", "latitude": 32.28818695, "longitude": 77.17702523},
    {"name": "Moustache Bhimtal Luxuria", "latitude": 29.36552248, "longitude": 79.53481747},
    {"name": "Moustache Srinagar", "latitude": 34.11547314, "longitude": 74.88701741},
    {"name": "Moustache Ranthambore Luxuria", "latitude": 26.05471373, "longitude": 76.42953726},
    {"name": "Moustache Coimbatore", "latitude": 11.02064612, "longitude": 76.96293531},
    {"name": "Moustache Shoja", "latitude": 31.56341267, "longitude": 77.36733331},
]

# Extract location information from property names
# This helps us build a dictionary for location lookups
locations = {}

for prop in PROPERTIES:
    # Extract location name from property name
    # For example, "Moustache Udaipur" -> "Udaipur"
    name_parts = prop["name"].split()
    if len(name_parts) >= 2:
        # Skip "Moustache" and get the location name
        location_name = name_parts[1].lower()
        
        # Special case for properties like "Panarpani Retreat"
        if name_parts[0] != "Moustache":
            location_name = name_parts[0].lower()
            
        # Store location coordinates
        if location_name not in locations:
            locations[location_name] = {
                "latitude": prop["latitude"], 
                "longitude": prop["longitude"]
            }

# Add common Indian cities for better location matching
INDIAN_CITIES = {
    "mumbai": {"latitude": 19.0760, "longitude": 72.8777},
    "delhi": {"latitude": 28.6139, "longitude": 77.2090},
    "bangalore": {"latitude": 12.9716, "longitude": 77.5946},
    "hyderabad": {"latitude": 17.3850, "longitude": 78.4867},
    "chennai": {"latitude": 13.0827, "longitude": 80.2707},
    "kolkata": {"latitude": 22.5726, "longitude": 88.3639},
    "ahmedabad": {"latitude": 23.0225, "longitude": 72.5714},
    "pune": {"latitude": 18.5204, "longitude": 73.8567},
    "lucknow": {"latitude": 26.8467, "longitude": 80.9462},
    "kochi": {"latitude": 9.9312, "longitude": 76.2673},
    "shimla": {"latitude": 31.1048, "longitude": 77.1734},
    "nainital": {"latitude": 29.3803, "longitude": 79.4636},
    "darjeeling": {"latitude": 27.0410, "longitude": 88.2663},
    "mussoorie": {"latitude": 30.4598, "longitude": 78.0644},
    "kodaikanal": {"latitude": 10.2381, "longitude": 77.4892},
    "goa": {"latitude": 15.2993, "longitude": 74.1240},
    "udaipur": {"latitude": 24.5854, "longitude": 73.7125},
    "jaipur": {"latitude": 26.9124, "longitude": 75.7873},
    "agra": {"latitude": 27.1767, "longitude": 78.0081},
    "varanasi": {"latitude": 25.3176, "longitude": 82.9739},
    "rishikesh": {"latitude": 30.0869, "longitude": 78.2676},
    "manali": {"latitude": 32.2396, "longitude": 77.1887},
    "mcleodganj": {"latitude": 32.2427, "longitude": 76.3234},
    "kasol": {"latitude": 32.0104, "longitude": 77.3149},
    "pushkar": {"latitude": 26.4899, "longitude": 74.5508},
    "jodhpur": {"latitude": 26.2389, "longitude": 73.0243},
    "jaisalmer": {"latitude": 26.9157, "longitude": 70.9083},
    "leh": {"latitude": 34.1526, "longitude": 77.5771},
    "srinagar": {"latitude": 34.0837, "longitude": 74.7973},
    "munnar": {"latitude": 10.0889, "longitude": 77.0595},
    "ooty": {"latitude": 11.4102, "longitude": 76.6950},
    "sissu": {"latitude": 32.4831, "longitude": 77.1328},  # Adding Sissu specifically from the example
    "koksar": {"latitude": 32.4083, "longitude": 77.2157},  # Adding Koksar from the example
}

# Update our locations dictionary with additional cities
for city, coordinates in INDIAN_CITIES.items():
    if city not in locations:
        locations[city] = coordinates

# States in India with approximate central coordinates
INDIAN_STATES = {
    "rajasthan": {"latitude": 27.0238, "longitude": 74.2179},
    "uttar pradesh": {"latitude": 27.5706, "longitude": 80.0982},
    "uttarakhand": {"latitude": 30.0668, "longitude": 79.0193},
    "himachal pradesh": {"latitude": 31.1048, "longitude": 77.1734},
    "maharashtra": {"latitude": 19.7515, "longitude": 75.7139},
    "karnataka": {"latitude": 15.3173, "longitude": 75.7139},
    "tamil nadu": {"latitude": 11.1271, "longitude": 78.6569},
    "kerala": {"latitude": 10.8505, "longitude": 76.2711},
    "goa": {"latitude": 15.2993, "longitude": 74.1240},
    "delhi": {"latitude": 28.7041, "longitude": 77.1025},
}

# Update locations with states
for state, coordinates in INDIAN_STATES.items():
    if state not in locations:
        locations[state] = coordinates

# Helper functions
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the distance between two geographical points using the Haversine formula.
    
    The Haversine formula determines the great-circle distance between two points
    on a sphere given their longitudes and latitudes. This is important for
    finding accurate distances between locations on Earth.
    
    Args:
        lat1: Latitude of the first point in decimal degrees
        lon1: Longitude of the first point in decimal degrees
        lat2: Latitude of the second point in decimal degrees
        lon2: Longitude of the second point in decimal degrees
        
    Returns:
        Distance between the points in kilometers
    """
    return geodesic((lat1, lon1), (lat2, lon2)).kilometers

def find_closest_match(location_query: str) -> Optional[str]:
    """
    Find the closest matching location for a potentially misspelled query.
    
    This function handles common spelling mistakes by finding the closest
    match in our database of locations. It uses the difflib library which
    compares sequences and finds close matches based on edit distance.
    
    Args:
        location_query: The user's location query which might contain typos
        
    Returns:
        The closest matching location name or None if no match is found
    """
    # Convert query to lowercase for case-insensitive matching
    query = location_query.lower()
    
    # Direct match
    if query in locations:
        return query
    
    # Check for close matches
    matches = get_close_matches(query, locations.keys(), n=1, cutoff=0.7)
    if matches:
        return matches[0]
    
    return None

def get_location_coordinates(location: str) -> Optional[Tuple[float, float]]:
    """
    Get coordinates (latitude and longitude) for a location.
    
    Args:
        location: The name of the location (should be pre-matched)
        
    Returns:
        A tuple of (latitude, longitude) or None if location not found
    """
    location = location.lower()
    
    if location in locations:
        return locations[location]["latitude"], locations[location]["longitude"]
    
    return None

def find_properties_near_location(lat: float, lon: float, max_distance_km: float = 50) -> List[PropertyResponse]:
    """
    Find all properties within the specified distance of a location.
    
    This function calculates the distance between a given point and all
    available properties, then returns those within the specified radius.
    
    Args:
        lat: Latitude of the target location
        lon: Longitude of the target location
        max_distance_km: Maximum distance in kilometers (default: 50km)
        
    Returns:
        List of nearby properties sorted by distance
    """
    nearby_properties = []
    
    for prop in PROPERTIES:
        # Calculate distance between query location and property
        distance = calculate_distance(lat, lon, prop["latitude"], prop["longitude"])
        
        # Check if property is within the maximum distance
        if distance <= max_distance_km:
            nearby_properties.append(
                PropertyResponse(
                    property_name=prop["name"],
                    distance_km=round(distance, 2),
                    coordinates={"latitude": prop["latitude"], "longitude": prop["longitude"]}
                )
            )
    
    # Sort properties by distance (closest first)
    nearby_properties.sort(key=lambda x: x.distance_km)
    return nearby_properties

# API Endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "Welcome to Moustache Escapes Property Finder API",
        "usage": "Send requests to /properties/nearby?location=YOUR_LOCATION to find nearby properties"
    }

@app.get("/properties/nearby", response_model=PropertiesResponse)
async def find_nearby_properties(location: str = Query(..., description="Location query (city, state, or area)")):
    """
    Find properties within 50km of the specified location.
    
    This endpoint accepts a location query and returns all Moustache Escapes properties
    within a 50km radius, sorted by distance. It handles potential spelling mistakes
    in the input query.
    
    Args:
        location: The location query (city, state, or area)
        
    Returns:
        A PropertiesResponse object containing matched location and nearby properties
    """
    # Start timing the response
    start_time = time.time()
    
    # Handle potential spelling mistakes
    matched_location = find_closest_match(location)
    if not matched_location:
        # No matching location found
        return PropertiesResponse(
            query=location,
            matched_location="No matching location found",
            properties_found=0,
            properties=[]
        )
    
    # Get coordinates for the matched location
    coordinates = get_location_coordinates(matched_location)
    if not coordinates:
        # This should not happen if find_closest_match worked correctly
        return PropertiesResponse(
            query=location,
            matched_location=matched_location,
            properties_found=0,
            properties=[]
        )
    
    lat, lon = coordinates
    
    # Find nearby properties
    nearby_properties = find_properties_near_location(lat, lon)
    
    # Ensure response time is within limits
    process_time = time.time() - start_time
    if process_time > 1.8:  # Warning threshold
        print(f"Warning: Response time approaching limit: {process_time:.2f}s")
    
    return PropertiesResponse(
        query=location,
        matched_location=matched_location,
        properties_found=len(nearby_properties),
        properties=nearby_properties
    )

# Run the API server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)