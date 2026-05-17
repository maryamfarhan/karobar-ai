from nlu import NLUProcessor
import json

def test():
    print("Initializing NLU Processor...")
    nlu = NLUProcessor()
    
    if not nlu.is_ready:
        print("\nWarning: NLU Processor is not ready. Make sure GEMINI_API_KEY is set in .env")
    
    test_input = "AC bilkul kaam nahi kar raha, kal subah G-13 mein chahiye, budget kam hai"
    print(f"\nTesting input: '{test_input}'")
    
    result = nlu.parse_request(test_input)
    print("\nParsed Result:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test()
