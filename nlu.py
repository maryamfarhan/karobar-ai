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
        self.api_keys = []
        key = os.environ.get("GEMINI_API_KEY_1") or os.environ.get("GEMINI_API_KEY")
        if key:
            self.api_keys.append(key)
                
        self.current_key_idx = 0
        self.model_id = 'models/gemini-2.0-flash-lite'
        self.is_ready = HAS_GEMINI and len(self.api_keys) > 0
        
        if self.is_ready:
            self._init_client()

    def _init_client(self):
        if self.current_key_idx < len(self.api_keys):
            self.client = genai.Client(api_key=self.api_keys[self.current_key_idx])
            return True
        return False

    def _keyword_fallback(self, text):
        text_lower = text.lower()
        
        service = None
        if any(w in text_lower for w in ['ac', 'technician', 'thanda', 'air condition', 'kharab']):
            service = 'AC Technician'
        elif any(w in text_lower for w in ['plumber', 'nal', 'pipe', 'paani', 'water']):
            service = 'Plumber'
        elif any(w in text_lower for w in ['electrician', 'bijli', 'current', 'electric']):
            service = 'Electrician'
        elif any(w in text_lower for w in ['cleaner', 'safai', 'clean']):
            service = 'Cleaner'
        elif any(w in text_lower for w in ['carpenter', 'lakri', 'wood', 'furniture']):
            service = 'Carpenter'
        elif any(w in text_lower for w in ['painter', 'rang', 'paint', 'wall']):
            service = 'Painter'

        city = None
        if any(w in text_lower for w in ['islamabad', 'isb', 'isl', 'g-13', 'f-10', 'f-8', 'g-10', 'bahria', 'i-8', 'e-11']):
            city = 'Islamabad'
        elif any(w in text_lower for w in ['karachi', 'khi', 'dha', 'clifton', 'pechs', 'gulshan', 'saddar', 'malir', 'nazimabad']):
            city = 'Karachi'
        elif any(w in text_lower for w in ['lahore', 'lhr', 'johar', 'gulberg']):
            city = 'Lahore'

        area = None
        for a in ['G-13', 'F-10', 'F-8', 'G-10', 'I-8', 'E-11', 'DHA', 'Clifton', 'PECHS', 'Gulshan', 'Bahria', 'Saddar', 'Malir']:
            if a.lower() in text_lower:
                area = a
                break

        confidence = 0.9 if (service and city) else 0.5

        return {
            "service_type": service,
            "city": city,
            "area": area,
            "urgency": "high" if any(w in text_lower for w in ['abhi', 'jaldi', 'urgent', 'aaj', 'now', 'asap']) else "normal",
            "budget_sensitivity": "high" if any(w in text_lower for w in ['sasta', 'budget', 'kam', 'cheap', 'affordable']) else "normal",
            "confidence_score": confidence,
            "followup_question": None if confidence >= 0.7 else "Aap kaunsi service aur city mein chahiye?"
        }

    def parse_request(self, text):
        prompt = f"""
You are an intent extractor for KarobarAI, a service orchestrator in Pakistan.
The user might speak in English, Urdu, or Roman Urdu.
Extract the following information from the user's request:
- service_type: The type of service they need (e.g., "Plumber", "Electrician", "AC Technician", "Carpenter", "Cleaner", "Painter").
- city: The city they are in (e.g., "Karachi", "Islamabad", "Lahore"). If not mentioned, return null.
- area: The specific area or neighborhood (e.g., "G-13", "DHA", "Gulshan"). If not mentioned, return null.
- urgency: "high", "normal", or "low".
- budget_sensitivity: "high", "normal", or "low".
- confidence_score: A number between 0.0 and 1.0.
- followup_question: If confidence_score < 0.7, provide a question asking for missing info. Otherwise null.

Return ONLY a valid JSON object:
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
        if self.is_ready:
            try:
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=prompt
                )
                text_resp = response.text.strip()
                if text_resp.startswith('```json'):
                    text_resp = text_resp[7:]
                if text_resp.endswith('```'):
                    text_resp = text_resp[:-3]
                return json.loads(text_resp.strip())
            except Exception as e:
                print(f"Gemini error, using fallback: {e}")

        print("Using keyword-based fallback...")
        return self._keyword_fallback(text)

    def parse_audio_request(self, audio_path):
        if self.is_ready:
            try:
                audio_file = self.client.files.upload(file=audio_path)
                prompt = """
You are an intent extractor for KarobarAI Pakistan.
Extract service_type, city, area, urgency, budget_sensitivity, confidence_score, followup_question from the audio.
Return ONLY valid JSON with these exact fields.
"""
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=[audio_file, prompt]
                )
                text_resp = response.text.strip()
                if text_resp.startswith('```json'):
                    text_resp = text_resp[7:]
                if text_resp.endswith('```'):
                    text_resp = text_resp[:-3]
                return json.loads(text_resp.strip())
            except Exception as e:
                print(f"Audio error, using fallback: {e}")

        return {
            "service_type": None,
            "city": None,
            "area": None,
            "urgency": "normal",
            "budget_sensitivity": "normal",
            "confidence_score": 0.0,
            "followup_question": "Audio processing failed. Please type your request."
        }