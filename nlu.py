import os
import json
from dotenv import load_dotenv

load_dotenv()

try:
    from google import genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

class NLUProcessor:
    def __init__(self):
        if not HAS_GEMINI:
            print("Warning: google-genai is not installed. Please install it using 'pip install google-genai'.")
            
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY environment variable is not set. NLU features will not work.")
            
        if HAS_GEMINI and api_key:
            self.client = genai.Client(api_key=api_key)
            self.model_id = 'models/gemini-2.0-flash'
            self.is_ready = True
        else:
            self.is_ready = False

    def parse_request(self, text):
        if not self.is_ready:
            return {
                "service_type": None,
                "city": None,
                "area": None,
                "urgency": "normal",
                "budget_sensitivity": "normal",
                "confidence_score": 0.0,
                "followup_question": "NLU is not configured. Please ensure google-genai is installed and GEMINI_API_KEY is set."
            }

        prompt = f"""
You are an intent extractor for KarobarAI, a service orchestrator in Pakistan.
The user might speak in English, Urdu, or Roman Urdu.
Extract the following information from the user's request:
- service_type: The type of service they need (e.g., "Plumber", "Electrician", "AC Technician", "Carpenter", "Cleaner", "Painter"). Try to map their request to one of these if possible. If not clear, return null.
- city: The city they are in (e.g., "Karachi", "Islamabad", "Lahore"). If not mentioned, return null.
- area: The specific area or neighborhood (e.g., "G-13", "DHA", "Gulshan"). If not mentioned, return null.
- urgency: "high", "normal", or "low". (e.g. "kal chahiye" -> normal/high, "abhi" -> high). If not mentioned, return "normal".
- budget_sensitivity: "high", "normal", or "low". (e.g. "budget kam hai" -> high). If not mentioned, return "normal".
- confidence_score: A number between 0.0 and 1.0 indicating how confident you are in your extraction. If crucial information like service_type or city is missing, lower the confidence score.
- followup_question: If confidence_score < 0.7, provide a natural sounding question (in the same language as the user's input) asking for the missing information. Otherwise, return null.

Return ONLY a valid JSON object matching this structure:
{{
    "service_type": "string or null",
    "city": "string or null",
    "area": "string or null",
    "urgency": "string",
    "budget_sensitivity": "string",
    "confidence_score": 0.0,
    "followup_question": "string or null"
}}

User request: "{text}"
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            # Find JSON block in the response
            text_resp = response.text.strip()
            if text_resp.startswith('```json'):
                text_resp = text_resp[7:]
            if text_resp.endswith('```'):
                text_resp = text_resp[:-3]
            return json.loads(text_resp.strip())
        except Exception as e:
            print(f"Error parsing request with Gemini: {e}")
            return {
                "service_type": None,
                "city": None,
                "area": None,
                "urgency": "normal",
                "budget_sensitivity": "normal",
                "confidence_score": 0.0,
                "followup_question": "Sorry, I had trouble processing that request."
            }

    def parse_audio_request(self, audio_path):
        if not self.is_ready:
            return {
                "service_type": None,
                "city": None,
                "area": None,
                "urgency": "normal",
                "budget_sensitivity": "normal",
                "confidence_score": 0.0,
                "followup_question": "NLU is not configured. Please ensure google-genai is installed and GEMINI_API_KEY is set."
            }

        prompt = """
You are an intent extractor for KarobarAI, a service orchestrator in Pakistan.
The user's spoken request is provided in the attached audio file (they might speak in English, Urdu, or Roman Urdu).
Extract the following information from the user's request:
- service_type: The type of service they need (e.g., "Plumber", "Electrician", "AC Technician", "Carpenter", "Cleaner", "Painter"). Try to map their request to one of these if possible. If not clear, return null.
- city: The city they are in (e.g., "Karachi", "Islamabad", "Lahore"). If not mentioned, return null.
- area: The specific area or neighborhood (e.g., "G-13", "DHA", "Gulshan"). If not mentioned, return null.
- urgency: "high", "normal", or "low". (e.g. "kal chahiye" -> normal/high, "abhi" -> high). If not mentioned, return "normal".
- budget_sensitivity: "high", "normal", or "low". (e.g. "budget kam hai" -> high). If not mentioned, return "normal".
- confidence_score: A number between 0.0 and 1.0 indicating how confident you are in your extraction. If crucial information like service_type or city is missing, lower the confidence score.
- followup_question: If confidence_score < 0.7, provide a natural sounding question (in the same language as the user's input) asking for the missing information. Otherwise, return null.

Return ONLY a valid JSON object matching this structure:
{
    "service_type": "string or null",
    "city": "string or null",
    "area": "string or null",
    "urgency": "string",
    "budget_sensitivity": "string",
    "confidence_score": 0.0,
    "followup_question": "string or null"
}
"""
        try:
            # Upload the audio file to Gemini
            uploaded_file = self.client.files.upload(file=audio_path)
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[uploaded_file, prompt]
            )
            
            # Clean up the uploaded file
            self.client.files.delete(name=uploaded_file.name)
            
            # Find JSON block in the response
            text_resp = response.text.strip()
            if text_resp.startswith('```json'):
                text_resp = text_resp[7:]
            if text_resp.endswith('```'):
                text_resp = text_resp[:-3]
            return json.loads(text_resp.strip())
        except Exception as e:
            print(f"Error parsing audio request with Gemini: {e}")
            return {
                "service_type": None,
                "city": None,
                "area": None,
                "urgency": "normal",
                "budget_sensitivity": "normal",
                "confidence_score": 0.0,
                "followup_question": "Sorry, I had trouble processing that audio request."
            }
