import os
import tempfile
from flask import Flask, request, jsonify, send_from_directory
from nlu import NLUProcessor
from matcher import ProviderMatcher
from booking import BookingSystem

app = Flask(__name__)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

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
    if not parsed:
        parsed = {}
        
    service_type = parsed.get('service_type')
    # If no service type was detected by NLU, use keyword fallback directly
    if not service_type:
        fallback_parsed = nlu_processor._keyword_fallback(user_message)
        service_type = fallback_parsed.get('service_type')
        if service_type:
            parsed['service_type'] = service_type
            
    # If still no service type, then we really need clarification
    if not service_type:
        return jsonify({
            "status": "needs_clarification",
            "followup_question": "Aap ko kaunsi service chahiye? (Plumber, Electrician, AC Repair, etc.)"
        }), 200

    # Fallback to context/defaults for location
    city = parsed.get('city') or data.get('city') or 'Islamabad'
    if not city or city == 'null' or city == '':
        city = 'Islamabad'
        
    area = parsed.get('area') or data.get('area') or 'G-13'
    if not area or area == 'null' or area == '':
        area = 'G-13'
        
    urgency = parsed.get('urgency') or data.get('urgency') or 'normal'
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
        "parsed_intent": {
            "service_type": service_type,
            "city": city,
            "area": area,
            "urgency": urgency,
            "budget_sensitivity": budget_sensitivity
        },
        "providers_found": len(results),
        "results": results
    }), 200

@app.route('/api/voice', methods=['POST'])
def handle_voice_request():
    if 'audio' not in request.files:
        return jsonify({"error": "No 'audio' file found in request"}), 400
        
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({"error": "Empty file submitted"}), 400
        
    # Optional context fields
    complexity = request.form.get('complexity', 'basic')
    is_returning_user = request.form.get('is_returning_user', 'false').lower() == 'true'
    
    # Save temporarily
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
            audio_file.save(temp_audio.name)
            temp_path = temp_audio.name
            
        # 1. Natural Language Understanding from Audio
        parsed = nlu_processor.parse_audio_request(temp_path)
        
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
        
        available_matches = [m for m in matches if m['available']]
        
        # 3. Dynamic Pricing breakdown
        results = []
        for match in available_matches:
            price_info = booking_system.calculate_price(
                match['price_per_hour'], 
                urgency, 
                complexity, 
                is_returning_user
            )
            
            provider_result = match.copy()
            provider_result['pricing_breakdown'] = price_info
            results.append(provider_result)
            
        return jsonify({
            "status": "success",
            "parsed_intent": parsed,
            "providers_found": len(results),
            "results": results
        }), 200
        
    finally:
        # Clean up local file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
