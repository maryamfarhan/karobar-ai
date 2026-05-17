from flask import Flask, request, jsonify
from nlu import NLUProcessor
from matcher import ProviderMatcher
from booking import BookingSystem

app = Flask(__name__)

# Initialize system components
nlu_processor = NLUProcessor()
matcher = ProviderMatcher("providers.json")
booking_system = BookingSystem(matcher)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "KarobarAI API is running."})

@app.route('/api/request', methods=['POST'])
def handle_request():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Missing 'message' field in JSON body"}), 400

    user_message = data['message']
    
    # Optional context fields that could be passed from the frontend
    complexity = data.get('complexity', 'basic')
    is_returning_user = data.get('is_returning_user', False)
    
    # 1. Natural Language Understanding
    parsed = nlu_processor.parse_request(user_message)
    
    if not parsed or parsed.get('confidence_score', 0) < 0.7:
        return jsonify({
            "status": "needs_clarification",
            "followup_question": parsed.get('followup_question', "Could you please provide more details?")
        }), 200

    service_type = parsed.get('service_type')
    city = parsed.get('city')
    area = parsed.get('area')
    urgency = parsed.get('urgency', 'normal')
    budget_sensitivity = parsed.get('budget_sensitivity', 'normal')
    
    max_price = None
    if budget_sensitivity == 'high':
        max_price = 800
        
    # 2. Matching logic
    matches = matcher.find_providers(
        service=service_type, 
        city=city, 
        area=area, 
        max_price=max_price
    )
    
    # Filter to only show available providers
    available_matches = [m for m in matches if m['available']]
    
    # 3. Prepare response with Dynamic Pricing breakdown
    results = []
    for match in available_matches:
        price_info = booking_system.calculate_price(
            match['price_per_hour'], 
            urgency, 
            complexity, 
            is_returning_user
        )
        
        # Attach pricing details
        provider_result = match.copy()
        provider_result['pricing_breakdown'] = price_info
        results.append(provider_result)
        
    return jsonify({
        "status": "success",
        "parsed_intent": parsed,
        "providers_found": len(results),
        "results": results
    }), 200

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
