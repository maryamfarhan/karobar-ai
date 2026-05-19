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
            print("Warning: google-genai is not installed.")
            
        self.api_keys = []
        for i in range(1, 4):
            key = os.environ.get(f"GEMINI_API_KEY_{i}")
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

    def _rotate_key(self):
        self.current_key_idx += 1
        if self.current_key_idx < len(self.api_keys):
            print(f"Switching to GEMINI_API_KEY_{self.current_key_idx + 1}")
            return self._init_client()
        return False

    def _keyword_fallback(self, text):
        text_lower = text.lower()
        
        service = None
        if any(w in text_lower for w in ['ac', 'technician', 'thanda', 'air condition']):
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
        if any(w in text_lower for w in ['islamabad', 'g-13', 'f-10', 'f-8', 'g-10', 'bahria']):
            city = 'Islamabad'
        elif any(w in text_lower for w in ['karachi', 'dha', 'clifton', 'pechs', 'gulshan', 'saddar', 'malir']):
            city = 'Karachi'
        elif any(w in text_lower for w in ['lahore', 'johar', 'gulberg']):
            city = 'Lahore'

        area = None
        for a in ['G-13', 'F-10', 'F-8', 'G-10', 'DHA', 'Clifton', 'PECHS', 'Gulshan', 'Bahria']:
            if a.lower() in text_lower:
                area = a
                break

        confidence = 0.9 if (service and city) else 0.5

        return {
            "service_type": service,
            "city": city,
            "area": area,
            "urgency": "high" if any(w in text_lower for w in ['abhi', 'jaldi', 'urgent', 'aaj']) else "normal",
            "budget_sensitivity": "high" if any(w in text_lower for w in ['sasta', 'budget', 'kam', 'cheap']) else "normal",
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
        while self.is_ready and self.current_key_idx < len(self.api_keys):
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
                err_str = str(e).lower()
                if 'quota' in err_str or '429' in err_str or 'exhausted' in err_str or 'limit' in err_str:
                    print(f"Quota/Limit hit on key index {self.current_key_idx}. Rotating...")
                    if not self._rotate_key():
                        break
                else:
                    print(f"Error parsing request with Gemini: {e}")
                    break

        print("Using keyword-based fallback...")
        return self._keyword_fallback(text)

    def parse_audio_request(self, audio_path):
        while self.is_ready and self.current_key_idx < len(self.api_keys):
            try:
                audio_file = self.client.files.upload(file=audio_path)
                prompt = """
You are an intent extractor for KarobarAI Pakistan.
Extract service_type, city, area, urgency, budget_sensitivity, confidence_score, followup_question from the audio.
Return ONLY valid JSON.
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
                err_str = str(e).lower()
                if 'quota' in err_str or '429' in err_str:
                    print(f"Quota/Limit hit on key index {self.current_key_idx}. Rotating...")
                    if not self._rotate_key():
                        break
                else:
                    print(f"Error processing audio: {e}")
                    break

        return {
            "service_type": None,
            "city": None,
            "area": None,
            "urgency": "normal",
            "budget_sensitivity": "normal",
            "confidence_score": 0.0,
            "followup_question": "Audio processing failed. Please type your request."
        }