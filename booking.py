import time
import random

class BookingSystem:
    def __init__(self, matcher):
        self.matcher = matcher
        self.active_bookings = []

    def calculate_price(self, base_rate, urgency, complexity, is_returning_user):
        urgency_multiplier = 1.3 if urgency == 'high' else 1.0
        
        complexity_multiplier = 1.0
        if complexity == 'complex':
            complexity_multiplier = 1.5
        elif complexity == 'intermediate':
            complexity_multiplier = 1.2
            
        loyalty_discount = 0.95 if is_returning_user else 1.0
        
        final_price = base_rate * urgency_multiplier * complexity_multiplier * loyalty_discount
        
        return {
            'base_rate': base_rate,
            'urgency_multiplier': urgency_multiplier,
            'complexity_multiplier': complexity_multiplier,
            'loyalty_discount': loyalty_discount,
            'final_price': round(final_price, 2)
        }

    def book_provider(self, provider_id, criteria):
        """
        Simulate booking a provider and start the service lifecycle.
        criteria should contain: service, city, area, max_price, urgency, complexity, is_returning_user
        """
        provider = self.matcher.get_provider_by_id(provider_id)
        if not provider or not provider['available']:
            print(f"Booking failed: Provider not found or unavailable.")
            return False

        # Calculate price breakdown
        price_info = self.calculate_price(
            provider['price_per_hour'], 
            criteria.get('urgency', 'normal'), 
            criteria.get('complexity', 'basic'), 
            criteria.get('is_returning_user', False)
        )
        
        # Book the provider
        provider['available'] = False
        success = self.matcher.update_provider(provider)
        
        if success:
            print(f"\n--- Booking Confirmed ---")
            print(f"Provider: {provider['name']} ({provider['service']})")
            print(f"Final Price: Rs {price_info['final_price']}/hr")
            print("-------------------------\n")
            
            # Start lifecycle simulation
            return self._run_lifecycle(provider, criteria)
        else:
            print("Booking failed due to a system error.")
            return False

    def _run_lifecycle(self, provider, criteria):
        print(f"Starting service lifecycle simulation for {provider['name']}...")
        time.sleep(1)
        
        # 1. Cancellation check
        cancel_chance = provider.get('cancellation_rate', 0.0)
        if random.random() < cancel_chance:
            print(f"\n🚨 ALERT: {provider['name']} has cancelled the booking!")
            provider['available'] = True
            self.matcher.update_provider(provider)
            time.sleep(1)
            return self._handle_cancellation(criteria, cancelled_provider_id=provider['id'])

        # 2. Reminder
        print("⏰ [1 hour before]: Sending reminder to provider and user...")
        time.sleep(1)
        
        # 3. En-route update
        print(f"🚗 [En-route]: {provider['name']} is on their way to the location.")
        time.sleep(1)
        
        # 4. Job Completion
        print(f"✅ [Completed]: {provider['name']} has completed the job.")
        time.sleep(1)
        
        # 5. Feedback
        feedback_score = random.choice([4, 5, 5, 5, 4, 3]) # Simulating mostly positive feedback
        print(f"⭐ [Feedback]: User rated the service {feedback_score}/5.")
        
        # Update provider rating (simple moving average approximation)
        old_rating = provider['rating']
        provider['rating'] = round((old_rating * 10 + feedback_score) / 11, 2)
        provider['available'] = True
        self.matcher.update_provider(provider)
        print(f"📈 Provider rating updated to {provider['rating']}.")
        return True

    def _handle_cancellation(self, criteria, cancelled_provider_id):
        print("🔄 Finding next best available provider...")
        matches = self.matcher.find_providers(
            service=criteria['service'],
            city=criteria['city'],
            area=criteria['area'],
            max_price=criteria['max_price']
        )
        
        # Filter out the cancelled one and unavailable ones
        valid_matches = [m for m in matches if m['id'] != cancelled_provider_id and m['available']]
        
        if not valid_matches:
            print("❌ Rebooking failed: No other providers available.")
            return False
            
        next_best = valid_matches[0]
        print(f"✅ Found replacement: {next_best['name']} (Score: {next_best['match_score']}/100)")
        return self.book_provider(next_best['id'], criteria)
