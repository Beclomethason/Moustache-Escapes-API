Moustache Escapes Property Finder API
Project Overview
The Moustache Escapes Property Finder API is a backend service designed for the tele-calling team at Moustache Escapes. This API helps agents quickly find available properties within a 50km radius of locations mentioned by customers during calls.
Key Features

Fast property lookup within 50km of any specified location in India
Intelligent handling of spelling mistakes in location names
Response time under 2 seconds for real-time usage during customer calls
Clean, RESTful API with clear JSON responses
Comprehensive location database covering Indian cities and states

Technical Details
This API is built with:

Python 3.7+
FastAPI framework
GeoPy for geographic calculations
Pydantic for data validation

Getting Started
Follow these steps to set up and run the Moustache Escapes Property Finder API on your local machine.
Prerequisites

Python 3.7 or higher
Git
Basic command line knowledge

Installation
1. Clone the repository
bashCopygit clone https://github.com/your-username/moustache-escapes-api.git
cd moustache-escapes-api
2. Set up a virtual environment
bashCopy# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
3. Install dependencies
bashCopypip install -r requirements.txt  
Running the API
Start the server with the following command:
bashCopypython main.py
The API will be available at http://localhost:8000.
API Documentation
Once the server is running, you can access the interactive API documentation at:
Copyhttp://localhost:8000/docs
Endpoints
GET /

Returns basic API information
Example: http://localhost:8000/

GET /properties/nearby

Returns properties within 50km of the specified location
Parameters:

location (required): City, state, or area name in India


Example: http://localhost:8000/properties/nearby?location=Jaipur

Response Format
The API returns data in the following format:
```
jsonCopy{
  "query": "original query string",
  "matched_location": "location matched after spelling correction",
  "properties_found": 3,
  "properties": [
    {
      "property_name": "Moustache Jaipur",
      "distance_km": 0.25,
      "coordinates": {
        "latitude": 27.29124839,
        "longitude": 75.89630143
      }
    },
    // Additional properties...
  ]
}
```
Example Usage
Here are some examples of how to use the API:
Finding properties near a city:
CopyGET /properties/nearby?location=Delhi
Finding properties with misspelled locations:
CopyGET /properties/nearby?location=Delih
The API will correct "Delih" to "Delhi" and return nearby properties.
Finding properties near a location without a direct property:
CopyGET /properties/nearby?location=Sissu
This will find the nearest property to Sissu (Moustache Koksar Luxuria).
Testing
You can test the API using:

Web Browser: Navigate to http://localhost:8000/docs and use the interactive Swagger UI
cURL: Run curl "http://localhost:8000/properties/nearby?location=Jaipur"
Postman: Create a GET request to http://localhost:8000/properties/nearby?location=Jaipur

Deployment
For production deployment, consider:

Using a production ASGI server (like Gunicorn with Uvicorn workers)
Setting up proper logging
Adding SSL/TLS for secure connections
Implementing caching for frequent queries

File Structure
```
Copymoustache-escapes-api/
├── main.py            # Main application file
├── requirements.txt   # Project dependencies
└── README.md          # This documentation
```
Future Enhancements
Potential improvements:

Database integration for property storage
Caching mechanism for frequent queries
Integration with property availability system
Admin panel for managing property data
Expanded coverage for international locations

Contributing

Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add some amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request
