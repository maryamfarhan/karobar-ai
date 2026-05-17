import json

class ProviderMatcher:
    def __init__(self, data_file):
        self.data_file = data_file
        self.providers = self._load_providers()

    def _load_providers(self):
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Could not find {self.data_file}")
            return []

    def get_provider_by_id(self, provider_id):
        for provider in self.providers:
            if provider['id'] == provider_id:
                return provider
        return None

    def update_provider(self, updated_provider):
        for i, provider in enumerate(self.providers):
            if provider['id'] == updated_provider['id']:
                self.providers[i] = updated_provider
                self._save_providers()
                return True
        return False

    def _save_providers(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.providers, f, indent=2)

    def find_providers(self, service, city, area=None, max_price=None, require_available=False):
        matches = []
        for p in self.providers:
            # Filter by basic requirements
            if p['service'].lower() != service.lower():
                continue
            if p['city'].lower() != city.lower():
                continue
            
            # Optional filters
            if area and p['area'].lower() != area.lower():
                continue
            if require_available and not p['available']:
                continue
                
            # Score Components
            s_rating = (p['rating'] / 5.0) * 0.30
            s_on_time = p['on_time_score'] * 0.25
            s_cancel = (1.0 - p['cancellation_rate']) * 0.20
            
            # Experience (cap at 15 years for max score)
            s_exp = min(p['experience_years'] / 15.0, 1.0) * 0.10
            
            # Price Score relative to budget
            if max_price:
                if p['price_per_hour'] <= max_price:
                    s_price = (1.0 - 0.5 * (p['price_per_hour'] / max_price)) * 0.10
                else:
                    s_price = max(0, 1.0 - (p['price_per_hour'] / max_price)) * 0.10
            else:
                # If no max price, normalize to a reasonable max (e.g. 2000)
                s_price = max(0, 1.0 - (p['price_per_hour'] / 2000.0)) * 0.10
                
            # Availability score
            s_avail = (1.0 if p['available'] else 0.0) * 0.05
            
            total_score = s_rating + s_on_time + s_cancel + s_exp + s_price + s_avail
            
            match = p.copy()
            match['match_score'] = round(total_score * 100, 2)
            match['score_breakdown'] = {
                'rating_score': round(s_rating * 100, 2),
                'on_time_score': round(s_on_time * 100, 2),
                'cancellation_score': round(s_cancel * 100, 2),
                'experience_score': round(s_exp * 100, 2),
                'price_score': round(s_price * 100, 2),
                'availability_score': round(s_avail * 100, 2)
            }
            matches.append(match)
            
        # Sort matches by match_score (descending)
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return matches
