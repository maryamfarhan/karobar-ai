# KarobarAI 🇵🇰
### AI Service Orchestrator for Pakistan's Informal Economy

KarobarAI is an agentic AI system that automates the end-to-end lifecycle of home service requests in Pakistan — from natural language input to provider matching, booking, follow-up, and dispute handling.

## Problem Statement
Pakistan's informal economy relies on WhatsApp, phone calls and referrals to find plumbers, electricians, AC technicians and other home service providers. This causes missed opportunities, poor matching, unpredictable pricing and lack of trust.

KarobarAI solves this by letting users simply say what they need in Urdu, Roman Urdu or English — and the system handles everything automatically.

## Demo
User types: "AC bilkul kaam nahi kar raha, kal subah G-13 mein chahiye, budget kam hai"
System understands, matches best provider, shows price breakdown, books, sends reminder, collects feedback.

## Architecture
User Input (Urdu/Roman Urdu/English)
↓
NLU Layer (Gemini API + Keyword Fallback)
↓
Provider Matching Engine (6-factor scoring)
↓
Dynamic Pricing Calculator
↓
Booking Simulation + Lifecycle
↓
Follow-up + Feedback + Rating Update

## Agent Workflow (Google Antigravity)
Antigravity orchestrates the entire pipeline:
- Intent understanding agent
- Provider matching agent  
- Pricing agent
- Booking and lifecycle agent
- Fallback and error recovery agent

## Files
- `nlu.py` — Multilingual intent extraction using Gemini API with keyword fallback
- `matcher.py` — 6-factor provider matching algorithm
- `booking.py` — Dynamic pricing, booking simulation, lifecycle management
- `agent.py` — Main orchestrator with chat interface
- `app.py` — Flask REST API
- `providers.json` — Mock dataset of 19 Pakistani service providers

## Matching Algorithm (6 Factors)
| Factor | Weight |
|--------|--------|
| Rating | 30% |
| On-time score | 25% |
| Cancellation rate | 20% |
| Experience years | 10% |
| Price vs budget | 10% |
| Availability | 5% |

## Dynamic Pricing
- Base rate from provider
- Urgency multiplier (1.3x for same day)
- Complexity multiplier (1.5x complex, 1.2x intermediate)
- Loyalty discount (5% for returning users)

## Multilingual Support
- English: "I need a plumber in DHA Karachi"
- Roman Urdu: "AC kharab hai G-13 mein chahiye"
- Urdu: Full Urdu text supported
- Fallback: Keyword detection when API quota exceeded

## Edge Cases Handled
- Provider cancels → auto-rebooks next best provider
- No provider available → clear error message
- Low confidence input → asks followup question
- All API keys exhausted → keyword fallback activates

## Baseline Comparison
| Feature | Simple App | KarobarAI |
|---------|-----------|-----------|
| Input | Form fields | Natural language |
| Matching | Distance only | 6-factor AI scoring |
| Pricing | Fixed | Dynamic with breakdown |
| Cancellation | Manual | Auto-rebook |
| Language | English only | Urdu/Roman Urdu/English |

## Tech Stack
- Google Antigravity (agent orchestration)
- Gemini API (NLU)
- Python/Flask (backend)
- Lovable (frontend UI)

## Setup
```bash
pip install -r requirements.txt
# Add GEMINI_API_KEY_1 to .env file
python app.py
```

## Privacy
All provider data is synthetic mock data. No real personal information is used.

## Limitations
- Mock provider dataset (19 providers)
- No real GPS tracking
- Gemini free tier quota limits

## Team
Built for AISeekho2026 Antigravity Hackathon
