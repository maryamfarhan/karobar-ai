import json
from matcher import ProviderMatcher
from booking import BookingSystem
from nlu import NLUProcessor

class KarobarAIAgent:
    def __init__(self, data_file="providers.json"):
        self.data_file = data_file
        self.matcher = ProviderMatcher(data_file)
        self.booking_system = BookingSystem(self.matcher)
        self.nlu = NLUProcessor()
        print("KarobarAI Agent Initialized")

    def find_service(self, service_type, city, area=None, max_price=None):
        """
        Find a service provider based on criteria.
        """
        print(f"Searching for {service_type} in {city}...")
        matches = self.matcher.find_providers(
            service=service_type, 
            city=city, 
            area=area, 
            max_price=max_price
        )
        return matches

    def book_service(self, provider_id, criteria):
        """
        Book a specific service provider with criteria.
        """
        return self.booking_system.book_provider(provider_id, criteria)

    def chat(self):
        print("\nWelcome to KarobarAI! How can I help you today?")
        print("(Type 'exit' to quit)\n")
        
        followup_count = 0
        
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                break
                
            parsed = self.nlu.parse_request(user_input)
            
            if not parsed or parsed.get('confidence_score', 0) < 0.7:
                followup_count += 1
                if followup_count >= 2:
                    print("KarobarAI: I'm still having trouble understanding. Please choose from our available services:")
                    services = sorted(list(set([p['service'] for p in self.matcher.providers])))
                    for i, s in enumerate(services):
                        print(f"  {i+1}. {s}")
                    print("Please tell me which service you need and your city.")
                    followup_count = 0
                else:
                    followup = parsed.get('followup_question') if parsed else "Could you please provide more details?"
                    print(f"KarobarAI: {followup}")
                continue
            
            followup_count = 0
                
            service_type = parsed.get('service_type')
            city = parsed.get('city')
            area = parsed.get('area')
            urgency = parsed.get('urgency', 'normal')
            budget_sensitivity = parsed.get('budget_sensitivity', 'normal')
            
            # Map budget sensitivity to max price
            max_price = None
            if budget_sensitivity == 'high':
                max_price = 800
                
            print(f"KarobarAI: Got it! Looking for a {service_type} in {city}{f', {area}' if area else ''}...")
            
            matches = self.find_service(service_type, city, area, max_price)
            # Filter available providers for the booking flow
            available_matches = [m for m in matches if m['available']]
            
            if available_matches:
                best_match = available_matches[0]
                
                # Ask for additional booking details
                complexity = input("Is the job 'basic', 'intermediate', or 'complex'? (default basic): ").lower()
                if complexity not in ['basic', 'intermediate', 'complex']:
                    complexity = 'basic'
                    
                returning = input("Are you a returning user? (y/n): ").lower()
                is_returning_user = returning in ['y', 'yes', 'haan', 'ji']
                
                # Get price breakdown
                price_preview = self.booking_system.calculate_price(
                    best_match['price_per_hour'], urgency, complexity, is_returning_user
                )
                
                print(f"\nKarobarAI: Found best available match: {best_match['name']}")
                print(f"  - Overall Score: {best_match['match_score']}/100")
                print(f"  - Provider Details: Rating: {best_match['rating']}, Base Price: Rs {best_match['price_per_hour']}/hr, Experience: {best_match['experience_years']} years")
                print(f"  - Estimated Price Breakdown:")
                print(f"    * Base Rate: Rs {price_preview['base_rate']}/hr")
                print(f"    * Urgency Multiplier ({urgency}): x{price_preview['urgency_multiplier']}")
                print(f"    * Complexity Multiplier ({complexity}): x{price_preview['complexity_multiplier']}")
                if is_returning_user:
                    print(f"    * Loyalty Discount: 5% off")
                print(f"    => Final Estimated Price: Rs {price_preview['final_price']}/hr\n")
                
                book_now = input("Do you want to book this provider? (yes/no): ")
                if book_now.lower() in ['yes', 'y', 'haan', 'ji']:
                    criteria = {
                        'service': service_type,
                        'city': city,
                        'area': area,
                        'max_price': max_price,
                        'urgency': urgency,
                        'complexity': complexity,
                        'is_returning_user': is_returning_user
                    }
                    self.book_service(best_match['id'], criteria)
                else:
                    print("KarobarAI: Okay, no problem.")
            else:
                print("KarobarAI: Sorry, no available providers found matching your criteria right now.")

if __name__ == "__main__":
    agent = KarobarAIAgent()
    agent.chat()

