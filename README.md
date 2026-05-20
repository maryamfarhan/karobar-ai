# KarobarAI 🇵🇰
**AI Service Orchestrator for Pakistan's Informal Economy**

KarobarAI is an AI-powered platform designed to modernize Pakistan’s informal home services market by enabling users to find and book trusted local service providers through natural language interaction.

Instead of relying on WhatsApp messages, phone calls, or personal referrals, users can simply describe their issue in English, Urdu, or Roman Urdu, and the system automatically handles provider matching, pricing, booking, tracking, and support workflows.

KarobarAI brings the simplicity of ride-hailing platforms such as Careem and Bykea to the home services sector.

## Live Production Deployment
Experience the fully responsive mobile PWA prototype live on your phone or browser:
**[https://karobar-ai-alpha.vercel.app/](https://karobar-ai-alpha.vercel.app/)**

---

## Problem Statement
Pakistan's informal economy relies on WhatsApp, phone calls, and referrals to find plumbers, electricians, AC technicians, and other home service providers. This causes missed opportunities, poor matching, unpredictable pricing, and a lack of trust.

KarobarAI solves this by letting users simply say what they need in Urdu, Roman Urdu, or English — and the system handles everything automatically.

---

## Demo
*   **User inputs**: *"AC bilkul kaam nahi kar raha, kal subah G-13 mein chahiye, budget kam hai"*
*   **System action**: Parses and extracts intent, matches the best local provider, displays pricing breakdown, confirms booking, schedules en-route transit updates, and collects feedback.

---

## Architecture
```
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
```

---

## Agent Workflow (Google Antigravity)
Antigravity orchestrates the entire pipeline:
1.  **Intent understanding agent**
2.  **Provider matching agent**
3.  **Pricing agent**
4.  **Booking and lifecycle agent**
5.  **Fallback and error recovery agent**

---

## Core File Modules
*   `nlu.py` — Multilingual intent extraction using Gemini API with keyword fallback
*   `matcher.py` — 6-factor provider matching algorithm (rating, punctuality, cancel rates, experience, pricing, availability)
*   `booking.py` — Dynamic pricing, booking simulation, lifecycle management
*   `agent.py` — Main orchestrator with chat interface
*   `app.py` — Flask REST API
*   `index.html` — Fully responsive Mobile PWA Client UI with custom SVG assets (e.g., custom Paint Roller)
*   `providers.json` — Mock database of 20 Pakistani service providers across Karachi, Islamabad, and Lahore (including Clifton Karachi Carpenter Javed Iqbal)

---

## Key Features Built & Deployed

### 1. Native PWA Mobile Experience
*   **Animated Splash Screen**: Emulates production apps on startup with an elegant green gradient and animated loading bar.
*   **Sticky Bottom Navigation**: Smooth navigation between Home, Bookings, Track, Support (Disputes), and Profile views.
*   **Circular Submit Button (`➔`)**: Integrated inside the search bar next to the microphone for immediate tap queries.

### 2. checkout Checkout & Payment Sheet
*   **Checkout Bottom Modal**: Allows users to dynamically select between Cash on Delivery (COD), EasyPaisa / JazzCash, or Karobar Wallet balances before confirming.

### 3. Automated Dispute Resolution & Live Support (Support Tab)
*   **Interactive Chatbot Assistant**: Launched inside the dedicated Support tab (`💬`) for any active or completed booking.
*   **Price Disputes**: Automates excess pricing claims by issuing direct EasyPaisa wallet refunds.
*   **No-Show Claims**: Verifies provider coordinates, cancels booking, adds Rs 200 compensation voucher to user wallet, and registers strikes.
*   **Quality Warranty**: Pauses provider settlement and schedules a free inspection visit under a 7-day quality warranty.

### 4. Autonomous Cancellation Re-routing
*   **Simulate Cancellation Button**: Trigger provider cancellations mid-transit on the GPS tracking screen.
*   The orchestrator autonomously queries the database, maps candidate ustaads, confirms a replacement candidate at the original rate, and resumes route animation without human intervention.

---

## Matching Algorithm (6 Factors)

| Factor | Weight | Description |
| :--- | :--- | :--- |
| **Rating** | 30% | Based on cumulative provider customer feedback ratings |
| **On-time score** | 25% | Punctuality history score |
| **Cancellation rate** | 20% | Penalty metric for historical order cancellations |
| **Experience years** | 10% | Verified years of active service experience |
| **Price vs budget** | 10% | Financial alignment score relative to estimated cost |
| **Availability** | 5% | Real-time service schedule availability |

---

## Dynamic Pricing Model
*   **Base Rate**: Dynamic rate sourced from provider's database.
*   **Urgency Multiplier**: 1.3x markup for same-day high urgency bookings.
*   **Complexity Multiplier**: 1.5x for complex jobs, 1.2x for intermediate tasks.
*   **Loyalty Discount**: 5% discount applied automatically for returning customers.

---

## Multilingual Support
*   **English**: *"I need a plumber in DHA Karachi"*
*   **Roman Urdu**: *"AC kharab hai G-13 mein chahiye"*
*   **Urdu**: Full Noto Sans Urdu speech and text queries supported.
*   **Fallback**: Localized keyword parser activates seamlessly when Gemini API quota limits are exceeded.

---

## Edge Cases Handled
*   **Provider cancels**: Automated rebooking engine automatically finds, assigns, and transitions to the next best provider at the original rate mid-route with zero user intervention.
*   **No provider available**: Renders friendly alternative recommendations and helpful error messages.
*   **Low confidence input**: Proactively prompts follow-up questions to gather necessary neighborhood or service details.
*   **All API keys exhausted**: Automated transition to deterministic keyword parser.

---

## Platform Baseline Comparison

| Feature | Simple App | KarobarAI |
| :--- | :--- | :--- |
| **Input** | Standard Form fields | Natural language / Speech assistant |
| **Matching** | Neighborhood distance only | Advanced 6-factor AI weighted scoring |
| **Pricing** | Fixed hourly flat fees | Real-time dynamic pricing breakdown |
| **Cancellation** | Manual cancel & re-search | Fully autonomous auto-rebooking |
| **Language** | English only | Urdu / Roman Urdu / English |

---

## Technology Stack
*   **Google Antigravity**: Agent orchestration
*   **Gemini API**: Multilingual Natural Language Understanding (NLU)
*   **Python / Flask**: Restful APIs & Backend orchestrator
*   **Vanilla CSS**: Premium Mobile-First PWA interface

---

## Setup & Local Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Keys
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY_1=your_api_key_here
```

### 3. Start Flask Web Server
```bash
python app.py
```

---

## Privacy
All provider data is synthetic mock data. No real personal information is used.

---

## Limitations
*   Mock provider dataset (20 providers)
*   No real GPS tracking
*   Gemini free tier quota limits

---

## Team
Built for the **AISeekho2026 Antigravity Hackathon**:
*   **Maryam Farhan**
*   **Shafaq Jamil**
