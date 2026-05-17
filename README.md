# KarobarAI

KarobarAI is an AI service orchestrator designed for Pakistan's informal economy. It connects users with local service providers like plumbers, electricians, AC technicians, and more in cities like Karachi and Islamabad.

## Features

- **Natural Language Understanding (NLU)**: Users can interact in English, Urdu, or Roman Urdu (e.g., "mera AC kharab hai G-13 mein kal chahiye budget kam hai"). It extracts intent using the Gemini API.
- **Smart Matching**: Filters and ranks providers based on user criteria (service, location, urgency, budget).
- **Booking Simulation**: Manages availability for providers.

## Project Structure

- `providers.json`: Mock dataset of 15 local service providers with fields capturing reliability, price, and availability.
- `nlu.py`: The Gemini API integration to parse user requests and determine intent.
- `agent.py`: The main entry point and agent logic for the orchestrator, featuring an interactive chat interface.
- `matcher.py`: Contains the logic to filter and rank providers based on user criteria.
- `booking.py`: Simulates the booking process, updating provider availability.

## Setup & Usage

1. Install dependencies:
   ```bash
   pip install google-genai
   ```
2. Set your Gemini API key:
   - On Windows: `set GEMINI_API_KEY=your_api_key_here`
   - On Linux/Mac: `export GEMINI_API_KEY=your_api_key_here`

3. **Run the CLI agent:**
   ```bash
   python agent.py
   ```

4. **Run the Flask API:**
   ```bash
   python app.py
   ```
   *Test the API using cURL or Postman:*
   ```bash
   curl -X POST http://localhost:5000/api/request \
   -H "Content-Type: application/json" \
   -d '{"message": "mera AC kharab hai G-13 mein kal chahiye budget kam hai", "complexity": "intermediate", "is_returning_user": true}'
   ```

## Future Enhancements
- Real-time availability tracking.
- Dynamic pricing models.

