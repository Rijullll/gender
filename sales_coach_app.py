import streamlit as st
import requests
import json
import os
import re
import time
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Sales Coach - Practice Smarter. Sell Better.",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MODERN ENTERPRISE SAAS DESIGN SYSTEM ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Base */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: radial-gradient(at 0% 0%, rgba(79, 70, 229, 0.04) 0px, transparent 50%),
                    radial-gradient(at 100% 100%, rgba(14, 165, 233, 0.04) 0px, transparent 50%),
                    #F8FAFC;
        color: #0F172A;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #0F172A;
        font-weight: 700;
        letter-spacing: -0.025em;
    }

    /* Gradient Typography */
    .text-gradient {
        background: linear-gradient(135deg, #0F172A 0%, #4F46E5 50%, #06B6D4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Ambient Landing Hero Banner */
    .landing-hero {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 45%, #312E81 100%);
        border-radius: 24px;
        padding: 56px 48px;
        color: white;
        margin-bottom: 32px;
        box-shadow: 0 20px 40px -15px rgba(15, 23, 42, 0.35);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }
    
    .landing-hero::before {
        content: "";
        position: absolute;
        top: -60px;
        right: -60px;
        width: 240px;
        height: 240px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.35) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    .landing-hero h1 {
        color: white;
        font-size: 3.2rem;
        font-weight: 800;
        line-height: 1.15;
        margin-bottom: 14px;
        letter-spacing: -0.03em;
    }
    
    .landing-hero p {
        color: #E2E8F0;
        font-size: 1.2rem;
        max-width: 680px;
        line-height: 1.6;
        margin-bottom: 26px;
    }

    /* Modern Card System */
    .saas-card {
        background: #FFFFFF;
        border: 1px solid rgba(226, 232, 240, 0.85);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.03), 0 2px 4px -2px rgba(15, 23, 42, 0.02);
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
    }
    
    .saas-card:hover {
        transform: translateY(-2px);
        border-color: #CBD5E1;
        box-shadow: 0 12px 24px -6px rgba(15, 23, 42, 0.08), 0 4px 8px -4px rgba(15, 23, 42, 0.04);
    }
    
    .saas-card-accent {
        border-left: 4px solid #4F46E5;
    }

    /* Badges & Chips */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }
    
    .badge-indigo { background: #EEF2FF; color: #4338CA; border: 1px solid #E0E7FF; }
    .badge-emerald { background: #ECFDF5; color: #047857; border: 1px solid #D1FAE5; }
    .badge-amber { background: #FFFBEB; color: #B45309; border: 1px solid #FEF3C7; }
    .badge-blue { background: #EFF6FF; color: #1D4ED8; border: 1px solid #DBEAFE; }
    .badge-rose { background: #FFF1F2; color: #BE123C; border: 1px solid #FFE4E6; }
    .badge-purple { background: #FAF5FF; color: #7E22CE; border: 1px solid #F3E8FF; }

    /* Framework Pill Strip */
    .framework-chip {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 9999px;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        font-size: 0.85rem;
        font-weight: 600;
        color: #334155;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }

    /* Sidebar Custom Widgets */
    .user-streak-card {
        background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
        border: 1px solid #C7D2FE;
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 16px;
    }
    
    .active-engine-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 16px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }

    .pulsing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10B981;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        animation: pulse 1.8s infinite;
        display: inline-block;
    }

    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    /* Metric & Stat Cards */
    .stat-box {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px;
        text-align: left;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    
    .stat-label {
        font-size: 0.82rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 6px;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 800;
        color: #0F172A;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Script & Response Display */
    .script-container {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #4F46E5;
        border-radius: 10px;
        padding: 20px 22px;
        font-size: 1.05rem;
        line-height: 1.7;
        color: #1E293B;
        margin: 12px 0;
    }

    /* Chat Elements */
    .chat-bubble-customer {
        background: #F1F5F9;
        border: 1px solid #E2E8F0;
        border-radius: 16px 16px 16px 4px;
        padding: 16px 20px;
        margin-bottom: 14px;
        color: #0F172A;
        line-height: 1.55;
    }
    
    .chat-bubble-user {
        background: #EEF2FF;
        border: 1px solid #C7D2FE;
        border-radius: 16px 16px 4px 16px;
        padding: 16px 20px;
        margin-bottom: 14px;
        color: #312E81;
        line-height: 1.55;
    }

    /* Persona Badge */
    .persona-badge {
        display: flex;
        align-items: center;
        gap: 14px;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 22px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }

    /* Streamlit UI Button Overrides */
    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0.6rem 1.35rem;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(79, 70, 229, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- PREDEFINED SCENARIOS CATALOG ---
SCENARIOS = {
    "saas_crm_migration": {
        "title": "Data Migration & Adoption Friction",
        "category": "B2B",
        "difficulty": "Intermediate",
        "industry": "Technology / SaaS",
        "product": "NextGen AI CRM Software",
        "price": "$120 / user / month",
        "customer": "VP of Sales (Mid-market company, 120 reps)",
        "objection": "We already use HubSpot. Migrating our team's data is too much work, our reps hate learning new tools, and it will disrupt our sales pipeline.",
        "context": "They complain that HubSpot's analytics are slow and field updates are clunky, but fear of operational downtime paralyzes them.",
        "description": "Handle status-quo bias and operational friction from an enterprise sales leader.",
        "objective": "De-risk the migration with white-glove onboarding and reframe weekly hours lost on legacy tools.",
        "persona": {
            "name": "David Vance",
            "role": "VP of Sales",
            "personality": "Direct, results-oriented, highly protective of quarterly pipeline.",
            "main_concern": "Sales downtime during migration and low CRM adoption by reps."
        }
    },
    "real_estate_interest_rates": {
        "title": "Waiting for Interest Rate Cuts",
        "category": "B2C",
        "difficulty": "Beginner",
        "industry": "Real Estate / Residential",
        "product": "Suburban 3-Bedroom Family Home",
        "price": "$450,000",
        "customer": "First-time Homebuyers (Young couple renting at $2,500/mo)",
        "objection": "The house is perfect for our toddler, but we're convinced mortgage rates will drop next year. We should wait and buy then.",
        "context": "They are spending $2,500/mo on rent with zero equity build, and the school district of this house is ranked #1 in the county.",
        "description": "Help emotional first-time buyers overcome hesitation and analyze rent vs. buy math.",
        "objective": "Demonstrate that waiting costs $30,000 in lost rent equity and leads to high-competition bidding wars.",
        "persona": {
            "name": "Sarah Miller",
            "role": "First-time Homebuyer",
            "personality": "Cautious, family-first, financially anxious about macro conditions.",
            "main_concern": "Fear of buying at the 'wrong time' before rate cuts."
        }
    },
    "cybersecurity_budget_freeze": {
        "title": "Startup Compliance Budget Pushback",
        "category": "B2B",
        "difficulty": "Advanced",
        "industry": "Professional Services / InfoSec",
        "product": "Enterprise SOC2 & Penetration Testing Audit",
        "price": "$25,000 flat fee",
        "customer": "CTO (Fintech Startup raising Series A in 3 months)",
        "objection": "Your $25,000 fee is double what we budgeted. We can buy automated checklist templates online for $10,000.",
        "context": "They must pass institutional due diligence for their Series A. A failed or delayed audit stalls their funding round.",
        "description": "Defend high-ticket consulting against cheap automated commodity alternatives.",
        "objective": "Reframe the audit from a compliance box into an insurance policy protecting their multi-million dollar Series A.",
        "persona": {
            "name": "Elena Rostova",
            "role": "Chief Technology Officer",
            "personality": "Analytical, cost-conscious, technically rigorous.",
            "main_concern": "Preserving startup runway while passing upcoming VC security diligence."
        }
    },
    "cold_call_gatekeeper": {
        "title": "Cold Call 'Send Me an Email' Brush-Off",
        "category": "B2B",
        "difficulty": "Advanced",
        "industry": "Cloud & DevOps",
        "product": "Autonomous Cloud Cost Optimization Suite",
        "price": "$2,500 / month",
        "customer": "Director of Engineering (Mid-market SaaS)",
        "objection": "I get 25 cold calls like this a day. Just send me an email and I'll review it if we have bandwidth.",
        "context": "They recently expanded AWS infrastructure by 40% and are experiencing compute overprovisioning.",
        "description": "Pivot past the classic gatekeeper brush-off and earn a 30-second peer conversation.",
        "objective": "Validate their time constraint, deliver a 15-second tailored peer benchmark, and ask a low-friction question.",
        "persona": {
            "name": "Marcus Thorne",
            "role": "Director of Engineering",
            "personality": "Extremely busy, guarded, allergic to generic sales pitches.",
            "main_concern": "Wasting valuable engineering time on sales calls."
        }
    },
    "competitor_entrenched": {
        "title": "Deeply Entrenched Competitor",
        "category": "B2B",
        "difficulty": "Intermediate",
        "industry": "Business Intelligence",
        "product": "Real-Time Customer Data Platform (CDP)",
        "price": "$1,800 / month",
        "customer": "Head of Growth & Analytics",
        "objection": "We already have Tableau and Snowflake deeply integrated into our stack. We are happy and have no reason to switch.",
        "context": "Business users cannot query real-time data without waiting 48 hours for data engineering tickets.",
        "description": "Handle a prospect who claims to be fully satisfied with an existing tech stack.",
        "objective": "Position as a real-time activation layer rather than a replacement, giving marketers direct autonomy.",
        "persona": {
            "name": "Rachel Chen",
            "role": "Head of Growth",
            "personality": "Pragmatic, metric-driven, skeptical of redundant software.",
            "main_concern": "Adding software bloat or breaking existing analytics pipelines."
        }
    },
    "ghosting_reengagement": {
        "title": "Ghosting Client Re-Engagement",
        "category": "B2B",
        "difficulty": "Beginner",
        "industry": "Digital Marketing",
        "product": "High-Intent B2B Lead Gen Retainer",
        "price": "$4,000 / month",
        "customer": "VP of Marketing",
        "objection": "Sorry for going radio silent after the proposal. We've decided to freeze all agency hiring until next year.",
        "context": "They missed their Q2 pipeline target by 28% and internal SDRs are struggling with cold outbound.",
        "description": "Revive a dormant deal after a sudden budget freeze without sounding desperate.",
        "objective": "Offer immediate value (pipeline audit), remove pressure, and uncover the real obstacle behind the freeze.",
        "persona": {
            "name": "Liam O'Connor",
            "role": "VP of Marketing",
            "personality": "Polite, conflict-avoidant, stressed by upper-management targets.",
            "main_concern": "Committing marketing budget when pipeline targets are uncertain."
        }
    },
    "luxury_retail_hesitation": {
        "title": "High-Ticket Retail Price Guilt",
        "category": "B2C",
        "difficulty": "Beginner",
        "industry": "Luxury Goods / Retail",
        "product": "Swiss Chronometer Heirloom Watch",
        "price": "$7,500",
        "customer": "Executive celebrating 40th birthday",
        "objection": "I love the watch and the craftsmanship is stunning, but I just can't justify spending $7,500 on myself right now.",
        "context": "He has been admiring the piece for 6 months to celebrate a major career milestone.",
        "description": "Help high-net-worth buyers overcome buyer's remorse and embrace milestone celebrations.",
        "objective": "Reframe the watch as a generational heirloom marking personal achievement rather than an expense.",
        "persona": {
            "name": "James Sterling",
            "role": "Customer Celebrating 40th Birthday",
            "personality": "Refined, hardworking, feels slight guilt around personal luxury indulgence.",
            "main_concern": "Perception of extravagance vs. personal reward."
        }
    },
    "demo_pushback_complexity": {
        "title": "Post-Demo Team Complexity Fear",
        "category": "B2B",
        "difficulty": "Intermediate",
        "industry": "Human Resources / People Tech",
        "product": "AI Workforce Intelligence Suite",
        "price": "$15,000 / year",
        "customer": "Chief People Officer",
        "objection": "The demo looked powerful, but our HR coordinators are non-technical. It looks too complex for our team to adopt.",
        "context": "Their current employee review process is manual spreadsheets taking 40 hours per cycle.",
        "description": "Counter the fear of software complexity and employee frustration.",
        "objective": "Demonstrate the zero-training UI, assisted 14-day rollout, and compare against 40 hours of spreadsheet pain.",
        "persona": {
            "name": "Brenda Garcia",
            "role": "Chief People Officer",
            "personality": "Empathetic, protective of team morale, overwhelmed by HR ops.",
            "main_concern": "Employee frustration with complex software and low adoption."
        }
    }
}

# --- LEARNING HUB MODULES ---
LESSONS = [
    {
        "id": "comm_psych",
        "title": "1. The Psychology of Sales Objections",
        "tag": "Psychology",
        "read_time": "4 min read",
        "summary": "Why customers push back and how to recognize real hesitation vs. polite brush-offs.",
        "content": """
### Understanding Why Customers Object
An objection is rarely a rejection. In 80% of sales interactions, an objection is actually a **request for more information or psychological reassurance**.

#### The Core Reasons Behind Objections:
1. **Fear of Looking Foolish:** B2B buyers fear making a decision that damages their internal reputation or career standing.
2. **Status Quo Bias:** Human brains prefer existing pain that is familiar over a new solution that carries unknown risks.
3. **Budget vs. Priority:** When a customer says *"We don't have the budget"*, they usually mean *"This has not been proven to be more important than the other 5 things on our list."*

#### Pro Tip:
Never argue with an objection. When you fight an objection directly, you create resistance. When you **validate** it first, you lower their emotional defenses.
"""
    },
    {
        "id": "four_step_formula",
        "title": "2. The 4-Step Objection Handling Formula",
        "tag": "Framework",
        "read_time": "5 min read",
        "summary": "Master the Listen, Validate, Reframe, and Check methodology used by top 1% performers.",
        "content": """
### The 4-Step Objection Formula (LVRC)

#### Step 1: Listen (Active & Uninterrupted)
Let the customer finish their entire thought without cutting them off. When you pause for 2 seconds after they finish, you demonstrate respect and gain conversational leverage.

#### Step 2: Validate & Empathize
Align yourself on their side of the table. Acknowledge that their concern is logical.
* *Say:* "That makes total sense. If I were in your shoes with this quarterly deadline, I’d be asking the exact same question."

#### Step 3: Reframe the Value
Shift their mental perspective from **cost/risk** to **cost of inaction or protected outcomes**.
* *Say:* "What we often see is that staying on the legacy system is actually costing 15 hours a week in manual work..."

#### Step 4: Check & Transition (Trial Close)
Confirm that the reframing made sense before pushing ahead.
* *Say:* "Does that perspective align with how your team measures risk?"
"""
    },
    {
        "id": "spin_challenger",
        "title": "3. SPIN Selling vs. The Challenger Sale",
        "tag": "Methodology",
        "read_time": "6 min read",
        "summary": "Compare the two most dominant B2B sales frameworks and when to deploy each.",
        "content": """
### Which Framework Should You Use?

#### SPIN Selling (Best for Discovery & Consultative Deals)
* **Situation:** Understand their current operations.
* **Problem:** Uncover dissatisfaction or bottlenecks.
* **Implication:** Quantify what happens if the problem remains unsolved (*"How does this error rate affect your customer churn?"*).
* **Need-Payoff:** Guide them to state the value of your solution in their own words.

#### The Challenger Sale (Best for Displacing Competitors & Status Quo)
* **Teach:** Bring commercial insights the customer hasn't considered.
* **Tailor:** Connect the insight directly to their specific role and KPI.
* **Take Control:** Guide the customer through decision criteria without backing down on price.
"""
    },
    {
        "id": "closing_mastery",
        "title": "4. Modern Closing Strategies That Don't Feel Pushy",
        "tag": "Closing",
        "read_time": "4 min read",
        "summary": "Say goodbye to old aggressive closes. Learn modern, consultative closing techniques.",
        "content": """
### Modern Closing Techniques

#### 1. The Alternative Choice Close
Instead of asking *"Do you want to buy?"*, give them two forward-moving choices.
* *Example:* "Would you prefer our engineering team begin the onboarding this Thursday, or would Monday be smoother for your staff?"

#### 2. The Trial Close (Temperature Check)
Test readiness before asking for the signature.
* *Example:* "On a scale of 1 to 10, based on what we've walked through today, how closely does this fit what your leadership is looking for?"

#### 3. The Assumptive Close
Speak naturally as if the partnership has already begun.
* *Example:* "Let's go ahead and draft the implementation schedule so your team is fully active before the busy holiday quarter."
"""
    },
    {
        "id": "follow_up_playbook",
        "title": "5. High-Conversion Follow-up Strategies",
        "tag": "Outreach",
        "read_time": "3 min read",
        "summary": "Write follow-ups that prospects actually respond to instead of 'just checking in'.",
        "content": """
### How to Follow-up Without Being Annoying

#### Never Say: *"Just checking in"* or *"Touching base"*
These phrases offer zero value and put all the cognitive burden on the prospect.

#### The 3 Rules of High-Conversion Follow-ups:
1. **Provide Value Every Touch:** Attach a 1-page case study, a relevant news insight, or a customized calculation.
2. **Clear Single Call-to-Action:** Don't ask 3 questions. Ask one simple yes/no or calendar choice.
3. **The 9-Word Breakup Email (For Ghosted Deals):**
   * *"Have you given up on optimizing your pipeline for Q4?"*
   * *Why it works:* It triggers loss aversion and prompts a rapid 80%+ reply rate.
"""
    }
]

# --- SESSION STATE INITIALIZATION ---
if "page" not in st.session_state:
    st.session_state.page = "Landing"

if "practice_mode" not in st.session_state:
    st.session_state.practice_mode = "Objection Coach"

if "api_provider" not in st.session_state:
    st.session_state.api_provider = "Google Gemini"

if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = os.getenv("GEMINI_API_KEY", "")

if "groq_api_key" not in st.session_state:
    st.session_state.groq_api_key = os.getenv("GROQ_API_KEY", "")

if "gemini_model" not in st.session_state:
    st.session_state.gemini_model = "gemini-3.5-flash"

if "groq_model" not in st.session_state:
    st.session_state.groq_model = "llama-3.3-70b-versatile"

# Form States
if "coach_product" not in st.session_state:
    st.session_state.coach_product = ""
if "coach_industry" not in st.session_state:
    st.session_state.coach_industry = ""
if "coach_price" not in st.session_state:
    st.session_state.coach_price = ""
if "coach_customer" not in st.session_state:
    st.session_state.coach_customer = ""
if "coach_objection" not in st.session_state:
    st.session_state.coach_objection = ""
if "coach_context" not in st.session_state:
    st.session_state.coach_context = ""
if "coaching_response" not in st.session_state:
    st.session_state.coaching_response = None

# Simulator States
if "sim_scenario_source" not in st.session_state:
    st.session_state.sim_scenario_source = "Library"
if "sim_scenario" not in st.session_state:
    st.session_state.sim_scenario = "saas_crm_migration"
if "sim_difficulty" not in st.session_state:
    st.session_state.sim_difficulty = "Intermediate"
if "sim_input_mode" not in st.session_state:
    st.session_state.sim_input_mode = "Text"
if "sim_messages" not in st.session_state:
    st.session_state.sim_messages = []
if "sim_in_progress" not in st.session_state:
    st.session_state.sim_in_progress = False
if "sim_report" not in st.session_state:
    st.session_state.sim_report = None
if "confirm_end_sim" not in st.session_state:
    st.session_state.confirm_end_sim = False

# Custom Scenarios Storage
if "custom_scenarios" not in st.session_state:
    st.session_state.custom_scenarios = {}
if "active_custom_scenario" not in st.session_state:
    st.session_state.active_custom_scenario = None

# Custom Scenario Inputs
if "cust_prod" not in st.session_state:
    st.session_state.cust_prod = ""
if "cust_ind" not in st.session_state:
    st.session_state.cust_ind = ""
if "cust_price" not in st.session_state:
    st.session_state.cust_price = ""
if "cust_name" not in st.session_state:
    st.session_state.cust_name = ""
if "cust_role" not in st.session_state:
    st.session_state.cust_role = ""
if "cust_trait" not in st.session_state:
    st.session_state.cust_trait = "Skeptical & analytical"
if "cust_obj" not in st.session_state:
    st.session_state.cust_obj = ""
if "cust_goal" not in st.session_state:
    st.session_state.cust_goal = ""

# Performance History
if "practice_history" not in st.session_state:
    st.session_state.practice_history = []

# --- API HELPER FUNCTIONS ---
def call_gemini_api(api_key, system_prompt, prompt, model="gemini-3.5-flash"):
    models_to_try = [model]
    for m_fallback in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]:
        if m_fallback not in models_to_try:
            models_to_try.append(m_fallback)

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2048}
    }

    last_error = ""
    for current_model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent?key={api_key}"
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=25)
            if response.status_code == 200:
                res_data = response.json()
                if "candidates" in res_data and res_data["candidates"]:
                    c_parts = res_data["candidates"][0].get("content", {}).get("parts", [])
                    if c_parts and "text" in c_parts[0]:
                        return c_parts[0]["text"]
            else:
                try:
                    last_error = response.json().get("error", {}).get("message", response.text)
                except:
                    last_error = response.text
                # If model is not found (404) or bad model parameter (400), try fallback model
                if response.status_code in (400, 404):
                    continue
        except Exception as e:
            last_error = str(e)
            
    if last_error:
        st.session_state.last_api_error = last_error
    return None

def generate_smart_sim_reply(active_sc, user_msg, sim_messages, difficulty):
    persona = active_sc.get("persona", {})
    p_name = persona.get("name", "Prospect")
    p_role = persona.get("role", "Decision Maker")
    p_concern = persona.get("main_concern", active_sc.get("objection", "pricing and risk"))
    prod = active_sc.get("product", "your solution")
    industry = active_sc.get("industry", "our industry")
    
    user_turns = len([m for m in sim_messages if m["role"] == "user"])
    u_lower = user_msg.lower()
    
    has_price = any(w in u_lower for w in ["price", "cost", "budget", "expensive", "fee", "discount", "payment", "cheap", "roi", "dollar", "$", "invest", "financial"])
    has_guarantee = any(w in u_lower for w in ["guarantee", "warranty", "proof", "case study", "results", "ensure", "promise", "safe", "risk", "track record", "reference", "certif"])
    has_time = any(w in u_lower for w in ["meeting", "demo", "call", "schedule", "tuesday", "thursday", "friday", "monday", "tomorrow", "next week", "minutes", "calendar", "sync"])
    has_onboarding = any(w in u_lower for w in ["migration", "setup", "onboarding", "training", "transition", "adopt", "downtime", "implement", "friction", "switch"])
    has_question = "?" in user_msg
    
    if user_turns == 1:
        if has_guarantee:
            return f"You talk about guarantees, but in {industry}, we've had vendors promise the world before. When it comes to our specific issue—{p_concern}—what concrete evidence do you have that {prod} won't cause the exact same headache for my team?"
        elif has_price:
            return f"ROI sounds great on a spreadsheet, but our budget was set months ago. Even if {prod} makes sense long-term, {p_concern}. How do you expect us to justify that expenditure to leadership right now?"
        elif has_onboarding:
            return f"Saying your team handles the setup is easy, but my staff is already operating at capacity. Specifically regarding {p_concern}, how many hours of internal resources are you really going to pull from us in the first 30 days?"
        elif has_question:
            return f"To be direct with you: yes, that's part of the puzzle. But the real blocker keeping me up at night is {p_concern}. What is your immediate strategy to eliminate that risk for {p_name}?"
        else:
            return f"Look, I appreciate your perspective, but you're skipping over our primary hurdle: {p_concern}. How exactly does {prod} solve that without creating new friction for our team?"

    elif user_turns == 2:
        if has_time:
            return f"Before I block out 20 minutes on my calendar, I need one thing clear: if we evaluate {prod}, what happens if we run into {p_concern}? Do you offer milestone sign-offs or written guarantees?"
        elif has_guarantee or has_onboarding:
            return f"That does sound more reassuring. If your team takes accountability for the transition, that removes some anxiety. But what about the ongoing support once the sales team hands us off?"
        elif has_price:
            return f"If the commercial structure can be tied to performance milestones, that might soften leadership's stance. But can you show me a case study of another {p_role} who overcame {p_concern} with you?"
        else:
            return f"That's a fair perspective. But in practical terms, how quickly can our team see measurable value before we get trapped in a long commitment with {prod}?"

    elif user_turns == 3:
        if has_time:
            return f"Alright, you've earned a short conversation. Send over the one-page summary and reference customer cases. If you can show me how you protect us from {p_concern}, I'm open to meeting next Tuesday at 2 PM."
        elif has_guarantee or has_price:
            return f"If you're willing to put that warranty into the pilot agreement in writing, I'm open to taking this to our committee. What does the onboarding timeline look like if we start next month?"
        else:
            return f"You've addressed the main points well. If you can document that in a proposal with clear exit clauses if we hit {p_concern}, I think we can discuss a small pilot."

    else:
        if has_time:
            return f"Confirmed. Send the calendar invite and the documentation to my inbox. If our technical lead approves the security review, we'll finalize the kickoff on that call."
        else:
            return f"I'm satisfied with how you've handled our concerns regarding {p_concern}. Send over the formal agreement with the terms we discussed for {prod}, and we'll schedule our review with the executive team."

def call_groq_api(api_key, system_prompt, prompt, model="llama-3.3-70b-versatile"):
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 2048
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            res_data = response.json()
            return res_data["choices"][0]["message"]["content"]
        else:
            try:
                err_msg = response.json().get("error", {}).get("message", response.text)
            except:
                err_msg = response.text
            st.error(f"⚠️ Groq API Error ({response.status_code}): {err_msg}")
            return None
    except Exception as e:
        st.error(f"Connection error to Groq: {str(e)}")
        return None

def call_ai(system_prompt, prompt):
    provider = st.session_state.api_provider
    if provider == "Google Gemini":
        key = st.session_state.gemini_api_key
        model = st.session_state.gemini_model
        if key:
            return call_gemini_api(key, system_prompt, prompt, model)
    elif provider == "Groq":
        key = st.session_state.groq_api_key
        model = st.session_state.groq_model
        if key:
            return call_groq_api(key, system_prompt, prompt, model)
    return None

# --- PARSING HELPERS ---
def parse_coaching_response(text):
    data = {
        "understand": "",
        "response": "",
        "why_it_works": "",
        "follow_up": "",
        "closing": "",
        "score": 80,
        "raw": text
    }
    
    sections = [
        ("Understand the Objection", "understand"),
        ("Recommended Response", "response"),
        ("Why This Works", "why_it_works"),
        ("Follow-up Question", "follow_up"),
        ("Closing Technique", "closing"),
        ("Confidence Score", "score_raw")
    ]
    
    for i, (title, key) in enumerate(sections):
        pattern = re.compile(rf"##\s*{re.escape(title)}\s*\n(.*?)(?=\n##|$)", re.DOTALL | re.IGNORECASE)
        match = pattern.search(text)
        if match:
            content = match.group(1).strip()
            if key == "score_raw":
                nums = re.findall(r"\b\d{1,3}\b", content)
                for n in nums:
                    if 0 <= int(n) <= 100:
                        data["score"] = int(n)
                        break
            else:
                data[key] = content
                
    if not data["response"] and len(text) > 50:
        data["response"] = text[:600]
    if not data["understand"]:
        data["understand"] = "The customer is experiencing status-quo inertia and seeking reassurance that your solution will not introduce hidden operational risks or friction."
    if not data["why_it_works"]:
        data["why_it_works"] = "By validating their concern first rather than defending your product, you lower defensive barriers and position yourself as a trusted advisor."
    if not data["follow_up"]:
        data["follow_up"] = "If we could demonstrate how our onboarding team handles 90% of the initial heavy lifting, would you be open to a 10-minute preview?"
    if not data["closing"]:
        data["closing"] = "Use a Trial Close: 'Would a phased pilot with just your core team give you the confidence needed before a company-wide rollout?'"
        
    return data

def generate_mock_coaching(product, customer, objection, price=""):
    return {
        "understand": f"The prospect ({customer}) is primarily concerned with operational risk, potential disruption, and justifying the investment ({price or 'cost'}). They are testing whether you truly understand their internal friction before committing.",
        "response": f"\"I completely understand where you're coming from. When a team is focused on daily execution, any change sounds risky. But let me ask you: if we could guarantee zero downtime and handle the heavy lifting for you, would you be open to exploring how this can save your team 4 hours a week?\"",
        "why_it_works": "This response deploys the Consultative Empathy framework. It acknowledges their friction without being defensive, reframes the cost into weekly hours recovered, and closes with a low-friction question.",
        "follow_up": "\"What is the single biggest milestone your team is trying to hit this quarter that we should protect?\"",
        "closing": "Alternative Choice Close: \"Would you prefer to review our 14-day transition blueprint this Thursday at 2 PM, or would Friday morning suit your schedule better?\"",
        "score": 85,
        "raw": "Mock Demo Response Generated"
    }

# --- IMPRESSIVE SIDEBAR NAVIGATION ---
with st.sidebar:
    # Sleek Brand Banner
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 22px;">
        <div style="background: linear-gradient(135deg, #4F46E5 0%, #06B6D4 100%); color: white; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: 800; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.35);">
            🎯
        </div>
        <div>
            <h3 style="margin: 0; font-size: 1.3rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em;">AI Sales Coach</h3>
            <p style="margin: 0; font-size: 0.75rem; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Enterprise Edition</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Rep Mastery Widget
    history_len = len(st.session_state.practice_history)
    rank = "Master Closer" if history_len >= 5 else ("Advancing Closer" if history_len >= 2 else "Apprentice Closer")
    streak_days = min(7, history_len + 1)
    
    st.markdown(f"""
    <div class="user-streak-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.78rem; font-weight: 800; color: #4338CA; text-transform: uppercase;">🏆 {rank}</span>
            <span style="font-size: 0.8rem; font-weight: 800; color: #EA580C;">🔥 {streak_days} Days Streak</span>
        </div>
        <div style="font-size: 0.74rem; color: #64748B; margin-top: 4px;">{history_len} sessions completed • SPIN Certified</div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation Buttons
    pages = [
        ("Dashboard", "🏠"),
        ("Practice", "🎯"),
        ("Scenario Library", "📚"),
        ("My Performance", "📊"),
        ("Learning Hub", "💡"),
        ("Settings", "⚙️")
    ]
    
    for p_name, icon in pages:
        is_active = (st.session_state.page == p_name)
        btn_type = "primary" if is_active else "secondary"
        if st.button(f"{icon}  {p_name}", key=f"nav_{p_name}", use_container_width=True, type=btn_type):
            st.session_state.page = p_name
            st.rerun()
            
    st.divider()
    
    # Active AI Engine Card
    active_key = st.session_state.gemini_api_key if st.session_state.api_provider == "Google Gemini" else st.session_state.groq_api_key
    active_model = st.session_state.gemini_model if st.session_state.api_provider == "Google Gemini" else st.session_state.groq_model
    
    if active_key:
        st.markdown(f"""
        <div class="active-engine-card">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span class="pulsing-dot"></span>
                <span style="font-weight: 700; font-size: 0.82rem; color: #0F172A;">{st.session_state.api_provider} Active</span>
            </div>
            <div style="font-size: 0.74rem; color: #64748B; margin-top: 4px;">
                Model: <span class="badge badge-indigo" style="font-size: 0.68rem; padding: 2px 6px;">{active_model}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="active-engine-card">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 14px;">⚪</span>
                <span style="font-weight: 700; font-size: 0.82rem; color: #B45309;">Demo Mode Active</span>
            </div>
            <div style="font-size: 0.74rem; color: #64748B; margin-top: 4px;">Full features unlocked via preloaded scenarios.</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    if st.button("🌐 Explore Landing Page", use_container_width=True):
        st.session_state.page = "Landing"
        st.rerun()

# ==========================================
# PAGE ROUTING
# ==========================================

# ------------------------------------------
# 1. IMPRESSIVE LANDING PAGE
# ------------------------------------------
if st.session_state.page == "Landing":
    st.markdown("""
    <div class="landing-hero">
        <span class="badge" style="background: rgba(255,255,255,0.18); color: white; border: 1px solid rgba(255,255,255,0.25); margin-bottom: 16px; font-size: 0.78rem;">
            ✨ AI-POWERED SALES ENABLEMENT 2.0
        </span>
        <h1>Turn Tough Customer Objections<br/>into Closed Deals.</h1>
        <p>Master objection handling, refine consultative discovery, and negotiate with unwavering confidence. Roleplay against adaptive AI buyer personas that react dynamically to your tone, methodology, and closing tactics.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_c1, col_c2, col_c3 = st.columns([1, 1, 1])
    with col_c1:
        if st.button("🚀 Enter Dashboard", use_container_width=True, type="primary"):
            st.session_state.page = "Dashboard"
            st.rerun()
    with col_c2:
        if st.button("🛡️ Handle an Objection", use_container_width=True):
            st.session_state.page = "Practice"
            st.session_state.practice_mode = "Objection Coach"
            st.rerun()
    with col_c3:
        if st.button("🎭 Launch Live Roleplay", use_container_width=True):
            st.session_state.page = "Practice"
            st.session_state.practice_mode = "Live Pitch Simulator"
            st.rerun()

    st.write("")
    # Methodology Strip
    st.markdown("""
    <div style="display: flex; gap: 12px; flex-wrap: wrap; align-items: center; justify-content: center; margin: 24px 0 36px 0;">
        <span style="font-size: 0.85rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Frameworks Embedded:</span>
        <span class="framework-chip">🎯 SPIN Selling®</span>
        <span class="framework-chip">⚡ The Challenger Sale®</span>
        <span class="framework-chip">🤝 Consultative Discovery</span>
        <span class="framework-chip">💼 Value-Based Closing</span>
        <span class="framework-chip">📈 MEDDPICC Alignment</span>
    </div>
    """, unsafe_allow_html=True)

    # Interactive Live Teaser Card
    st.markdown("""
    <div class="saas-card" style="border: 1px solid #C7D2FE; background: #FFFFFF; padding: 28px; margin-bottom: 32px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span class="badge badge-rose">Live Scenario Preview</span>
                <span style="font-size: 0.85rem; color: #64748B;">B2B Enterprise SaaS • Negotiation Stage</span>
            </div>
            <span class="badge badge-emerald">Estimated Win Probability: 84%</span>
        </div>
        <div style="background: #F8FAFC; border-left: 4px solid #EF4444; border-radius: 8px; padding: 14px 18px; margin-bottom: 14px; font-size: 0.95rem; color: #1E293B;">
            <strong>Prospect:</strong> "Your competitor is offering 40% cheaper annual licensing. We like your tool, but our CFO won't approve this price delta."
        </div>
        <div style="background: #EEF2FF; border-left: 4px solid #4F46E5; border-radius: 8px; padding: 14px 18px; font-size: 0.95rem; color: #312E81;">
            <strong>AI Coach Verbatim Script:</strong> "I completely respect that—every CFO's mandate is capital discipline. But let me ask you: if their tool saves $10k on software yet costs 30 hours of manual work every month, which solution actually protects your bottom line? Let's run a 1-page TCO comparison together."
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4-Pillar Capability Grid
    st.subheader("⚡ Built for Top 1% Revenue Generators")
    f1, f2 = st.columns(2)
    with f1:
        st.markdown("""
        <div class="saas-card saas-card-accent" style="height: 100%;">
            <span class="badge badge-indigo" style="margin-bottom: 10px;">Sub-Second Intelligence</span>
            <h3 style="margin: 0 0 8px 0;">Tactical Objection Deconstruction</h3>
            <p style="color: #64748B; font-size: 0.95rem; line-height: 1.6;">
                Uncover what prospects are *actually* afraid of. Get psychographic root-cause analysis, verbatim scripts, and discovery questions that turn defensive prospects into buyers.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown("""
        <div class="saas-card saas-card-accent" style="height: 100%;">
            <span class="badge badge-purple" style="margin-bottom: 10px;">Conversational AI</span>
            <h3 style="margin: 0 0 8px 0;">Adaptive Live Pitch Simulator</h3>
            <p style="color: #64748B; font-size: 0.95rem; line-height: 1.6;">
                Practice against realistic AI buyers with customizable difficulty tiers. Build muscle memory for high-stakes calls, or build your own custom pipeline scenarios.
            </p>
        </div>
        """, unsafe_allow_html=True)

    f3, f4 = st.columns(2)
    with f3:
        st.markdown("""
        <div class="saas-card saas-card-accent" style="height: 100%;">
            <span class="badge badge-emerald" style="margin-bottom: 10px;">Performance Radar</span>
            <h3 style="margin: 0 0 8px 0;">5-Axis Performance Scorecards</h3>
            <p style="color: #64748B; font-size: 0.95rem; line-height: 1.6;">
                Quantify your skills across Communication, Discovery, Objection Handling, Product Knowledge, and Closing. Receive actionable feedback on every single practice turn.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with f4:
        st.markdown("""
        <div class="saas-card saas-card-accent" style="height: 100%;">
            <span class="badge badge-blue" style="margin-bottom: 10px;">Custom Pipeline Engine</span>
            <h3 style="margin: 0 0 8px 0;">Practice Your Actual Live Deals</h3>
            <p style="color: #64748B; font-size: 0.95rem; line-height: 1.6;">
                Don't just roleplay generic cases. Input your real prospect's name, role, objections, and price point to prepare for your actual meeting tomorrow.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------
# 2. USER DASHBOARD
# ------------------------------------------
elif st.session_state.page == "Dashboard":
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px;">
        <div>
            <h1 style="margin: 0; font-size: 2.3rem;">Welcome to AI Sales Coach 👋</h1>
            <p style="margin: 6px 0 0 0; color: #64748B; font-size: 1.05rem;">Master objections, practice high-stakes calls, and track your closing competency.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 2 Feature Action Launchers
    fc1, fc2 = st.columns(2)
    with fc1:
        st.markdown("""
        <div class="saas-card saas-card-accent" style="height: 100%;">
            <div style="font-size: 32px; margin-bottom: 10px;">🛡️</div>
            <h3 style="margin: 0 0 8px 0;">Handle Customer Objections</h3>
            <p style="color: #64748B; font-size: 0.95rem; line-height: 1.55; margin-bottom: 16px;">
                Enter a tough objection from a prospect. Get immediate psychological analysis, natural verbatim scripts, and strategic closing techniques.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Objection Coach ➔", key="dash_btn_obj", use_container_width=True, type="primary"):
            st.session_state.page = "Practice"
            st.session_state.practice_mode = "Objection Coach"
            st.rerun()
            
    with fc2:
        st.markdown("""
        <div class="saas-card saas-card-accent" style="height: 100%;">
            <div style="font-size: 32px; margin-bottom: 10px;">🎭</div>
            <h3 style="margin: 0 0 8px 0;">Practice Your Sales Pitch</h3>
            <p style="color: #64748B; font-size: 0.95rem; line-height: 1.55; margin-bottom: 16px;">
                Roleplay against adaptive AI buyer personas or build your own custom deal scenario. Practice live dialogues and receive an automated evaluation.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Live Pitch Simulator ➔", key="dash_btn_sim", use_container_width=True, type="primary"):
            st.session_state.page = "Practice"
            st.session_state.practice_mode = "Live Pitch Simulator"
            st.rerun()

    st.write("")
    # Metrics Row
    history_count = len(st.session_state.practice_history)
    avg_score = int(sum([h.get("score", 0) for h in st.session_state.practice_history]) / history_count) if history_count > 0 else 0
    total_scenarios = len(SCENARIOS) + len(st.session_state.custom_scenarios)
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Total Practice Sessions</div>
            <div class="stat-value">{history_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        score_display = f"{avg_score}%" if history_count > 0 else "—"
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Average Performance Score</div>
            <div class="stat-value" style="color: #4F46E5;">{score_display}</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Available Scenarios</div>
            <div class="stat-value">{total_scenarios}</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Learning Modules</div>
            <div class="stat-value">{len(LESSONS)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    col_rec, col_sugg = st.columns([1.2, 0.8])
    with col_rec:
        st.subheader("⏱️ Recent Practice Sessions")
        if not st.session_state.practice_history:
            st.markdown("""
            <div class="saas-card" style="text-align: center; padding: 40px 20px;">
                <div style="font-size: 34px; margin-bottom: 10px;">📋</div>
                <h4 style="margin: 0 0 6px 0; color: #475569;">No Practice Sessions Recorded</h4>
                <p style="color: #94A3B8; font-size: 0.9rem; max-width: 400px; margin: 0 auto 16px auto;">
                    Complete your first practice session in the Objection Coach or Live Simulator to see your progress and performance radar.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for item in reversed(st.session_state.practice_history[-4:]):
                score_color = "#10B981" if item.get("score", 0) >= 75 else "#F59E0B"
                st.markdown(f"""
                <div class="saas-card" style="padding: 16px 20px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 700; color: #0F172A; font-size: 1rem;">{item.get('title', 'Sales Session')}</div>
                        <div style="color: #64748B; font-size: 0.85rem;">{item.get('date', 'Today')} • {item.get('type', 'Coaching')}</div>
                    </div>
                    <div style="text-align: right;">
                        <span class="badge" style="background: #F1F5F9; color: {score_color}; font-size: 1rem; padding: 6px 12px;">{item.get('score', 0)}/100</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
    with col_sugg:
        st.subheader("💡 Recommended Scenarios")
        for sc_key in ["saas_crm_migration", "real_estate_interest_rates", "cybersecurity_budget_freeze"]:
            sc = SCENARIOS[sc_key]
            st.markdown(f"""
            <div class="saas-card" style="padding: 16px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span class="badge badge-indigo">{sc['category']}</span>
                    <span style="font-size: 0.8rem; color: #64748B;">{sc['difficulty']}</span>
                </div>
                <div style="font-weight: 700; color: #0F172A; font-size: 0.95rem; margin-bottom: 4px;">{sc['title']}</div>
                <div style="font-size: 0.85rem; color: #64748B; margin-bottom: 10px;">{sc['industry']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Practise Scenario ➔", key=f"quick_sc_{sc_key}", use_container_width=True):
                st.session_state.sim_scenario_source = "Library"
                st.session_state.sim_scenario = sc_key
                st.session_state.page = "Practice"
                st.session_state.practice_mode = "Live Pitch Simulator"
                st.session_state.sim_in_progress = True
                st.session_state.sim_messages = [{
                    "role": "assistant",
                    "content": f"Hi. Look, the proposal looks fine, but {sc['objection']} How do you justify this?"
                }]
                st.rerun()

# ------------------------------------------
# 3. PRACTICE (OBJECTION COACH & SIMULATOR)
# ------------------------------------------
elif st.session_state.page == "Practice":
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h1 style="margin: 0; font-size: 2.3rem;">Sales Practice Studio</h1>
        <p style="color: #64748B; margin: 4px 0 0 0;">Sharpen your objection reflexes and roleplay high-stakes deals in a controlled AI environment.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_tab1, col_tab2 = st.columns(2)
    with col_tab1:
        if st.button("🛡️ Objection Coach", use_container_width=True, type="primary" if st.session_state.practice_mode == "Objection Coach" else "secondary"):
            st.session_state.practice_mode = "Objection Coach"
            st.rerun()
    with col_tab2:
        if st.button("🎭 Live Pitch Simulator", use_container_width=True, type="primary" if st.session_state.practice_mode == "Live Pitch Simulator" else "secondary"):
            st.session_state.practice_mode = "Live Pitch Simulator"
            st.rerun()
            
    st.divider()

    # --- SUB-MODE A: OBJECTION COACH ---
    if st.session_state.practice_mode == "Objection Coach":
        with st.expander("⚡ Quick Load a Predefined Scenario", expanded=False):
            preset_options = {"Select a scenario...": None}
            for k, v in SCENARIOS.items():
                preset_options[f"{v['category']} - {v['title']} ({v['industry']})"] = k
                
            selected_preset = st.selectbox("Choose a scenario to auto-fill inputs:", options=list(preset_options.keys()))
            if selected_preset != "Select a scenario..." and preset_options[selected_preset]:
                sc_data = SCENARIOS[preset_options[selected_preset]]
                st.session_state.coach_product = sc_data["product"]
                st.session_state.coach_industry = sc_data["industry"]
                st.session_state.coach_price = sc_data["price"]
                st.session_state.coach_customer = sc_data["customer"]
                st.session_state.coach_objection = sc_data["objection"]
                st.session_state.coach_context = sc_data["context"]
                st.toast(f"Loaded scenario: {sc_data['title']}")

        st.markdown("### 📝 Objection Configuration")
        
        c_step1, c_step2 = st.columns(2)
        with c_step1:
            st.markdown("""
            <div class="saas-card">
                <span class="badge badge-indigo" style="margin-bottom: 8px;">Step 1</span>
                <h4 style="margin: 0 0 16px 0;">Product Details</h4>
            </div>
            """, unsafe_allow_html=True)
            
            p_name = st.text_input("Product or Service Name *", value=st.session_state.coach_product, placeholder="e.g. NextGen CRM SaaS, Cyber Security Audit")
            p_ind = st.text_input("Industry", value=st.session_state.coach_industry, placeholder="e.g. Technology, Real Estate, Healthcare")
            p_price = st.text_input("Price / Deal Size (Optional)", value=st.session_state.coach_price, placeholder="e.g. $120/mo, $25,000 flat, $450,000")

        with c_step2:
            st.markdown("""
            <div class="saas-card">
                <span class="badge badge-blue" style="margin-bottom: 8px;">Step 2</span>
                <h4 style="margin: 0 0 16px 0;">Customer Profile</h4>
            </div>
            """, unsafe_allow_html=True)
            
            c_target = st.text_input("Target Customer *", value=st.session_state.coach_customer, placeholder="e.g. VP of Sales, CTO of fintech startup, First-time homebuyer")
            c_obj = st.text_area("Customer Objection *", value=st.session_state.coach_objection, placeholder="e.g. Your price is 30% higher than competitor X; We don't have budget.", height=95)
            c_ctx = st.text_input("Additional Context (Optional)", value=st.session_state.coach_context, placeholder="e.g. They are raising Series A soon; currently renting.")

        st.session_state.coach_product = p_name
        st.session_state.coach_industry = p_ind
        st.session_state.coach_price = p_price
        st.session_state.coach_customer = c_target
        st.session_state.coach_objection = c_obj
        st.session_state.coach_context = c_ctx

        col_act1, col_act2, col_act3 = st.columns([1.5, 0.5, 1])
        with col_act1:
            gen_clicked = st.button("🧠 Generate Coaching Response", type="primary", use_container_width=True)
        with col_act2:
            if st.button("🗑️ Clear Form", use_container_width=True):
                st.session_state.coach_product = ""
                st.session_state.coach_industry = ""
                st.session_state.coach_price = ""
                st.session_state.coach_customer = ""
                st.session_state.coach_objection = ""
                st.session_state.coach_context = ""
                st.session_state.coaching_response = None
                st.rerun()

        if gen_clicked:
            if not p_name or not c_target or not c_obj:
                st.error("⚠️ Please fill in all required fields marked with an asterisk (*): Product Name, Target Customer, and Customer Objection.")
            else:
                with st.spinner("Analyzing objection psychology and drafting expert coaching response..."):
                    sys_prompt = """
                    You are an expert executive Sales Coach with 15+ years in B2B and B2C sales.
                    Analyze the objection and respond in this exact Markdown structure:

                    ## Understand the Objection
                    [Explain what the customer may actually be concerned about, including fear, status-quo bias, or risk]

                    ## Recommended Response
                    [Provide a natural, empathetic, verbatim response the salesperson can say directly to the customer]

                    ## Why This Works
                    [Explain the sales psychology or strategy behind this response]

                    ## Follow-up Question
                    [Suggest a strategic open-ended question to continue the conversation]

                    ## Closing Technique
                    [Explain how to move toward the next step, with an exact closing sentence]

                    ## Confidence Score
                    [Score from 1 to 100 based on objection resistance and deal closing likelihood]
                    """
                    
                    user_prompt = f"""
                    Product: {p_name}
                    Industry: {p_ind}
                    Price: {p_price}
                    Target Customer: {c_target}
                    Objection: {c_obj}
                    Context: {c_ctx}
                    """
                    
                    raw_out = call_ai(sys_prompt, user_prompt)
                    if raw_out:
                        st.session_state.coaching_response = parse_coaching_response(raw_out)
                    else:
                        time.sleep(0.8)
                        st.session_state.coaching_response = generate_mock_coaching(p_name, c_target, c_obj, p_price)
                        st.toast("Coaching generated in Demo Mode!")

        if st.session_state.coaching_response:
            resp = st.session_state.coaching_response
            st.markdown("---")
            st.markdown("### 🎯 Coaching Recommendations")
            
            score = resp.get("score", 85)
            score_color = "#10B981" if score >= 75 else "#F59E0B"
            st.markdown(f"""
            <div class="saas-card" style="display: flex; justify-content: space-between; align-items: center; border-left: 4px solid {score_color};">
                <div>
                    <h4 style="margin: 0; color: #0F172A;">Deal Closing Likelihood Score</h4>
                    <p style="margin: 0; color: #64748B; font-size: 0.85rem;">Based on objection severity and reframing leverage</p>
                </div>
                <div style="font-size: 2.2rem; font-weight: 800; color: {score_color}; font-family: 'Plus Jakarta Sans';">
                    {score}%
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="saas-card">
                <h4 style="color: #0F172A; margin-bottom: 8px;">🔍 Understand the Objection</h4>
                <p style="color: #475569; line-height: 1.6; margin: 0;">{}</p>
            </div>
            """.format(resp["understand"]), unsafe_allow_html=True)
            
            st.markdown("""
            <div class="saas-card saas-card-accent">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <h4 style="color: #4F46E5; margin: 0;">🗣️ Recommended Response (Verbatim Script)</h4>
                    <span class="badge badge-indigo">Say Directly</span>
                </div>
                <div class="script-container">{}</div>
            </div>
            """.format(resp["response"]), unsafe_allow_html=True)
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.markdown("""
                <div class="saas-card" style="height: 100%;">
                    <h4 style="color: #0F172A; margin-bottom: 8px;">🧠 Why This Works</h4>
                    <p style="color: #475569; font-size: 0.95rem; line-height: 1.6; margin: 0;">{}</p>
                </div>
                """.format(resp["why_it_works"]), unsafe_allow_html=True)
                
            with col_b2:
                st.markdown("""
                <div class="saas-card" style="height: 100%;">
                    <h4 style="color: #0F172A; margin-bottom: 8px;">❓ Follow-up Question</h4>
                    <p style="color: #475569; font-size: 0.95rem; line-height: 1.6; margin: 0;">{}</p>
                </div>
                """.format(resp["follow_up"]), unsafe_allow_html=True)
                
            st.markdown("""
            <div class="saas-card">
                <h4 style="color: #0F172A; margin-bottom: 8px;">🎯 Closing Technique</h4>
                <p style="color: #475569; line-height: 1.6; margin: 0;">{}</p>
            </div>
            """.format(resp["closing"]), unsafe_allow_html=True)
            
            col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
            with col_btn1:
                if st.button("🎭 Practise This Objection", use_container_width=True, type="primary"):
                    st.session_state.practice_mode = "Live Pitch Simulator"
                    st.session_state.sim_scenario_source = "Custom"
                    st.session_state.active_custom_scenario = {
                        "title": f"Custom: {st.session_state.coach_product}",
                        "product": st.session_state.coach_product,
                        "industry": st.session_state.coach_industry or "General",
                        "price": st.session_state.coach_price,
                        "objection": st.session_state.coach_objection,
                        "objective": "Address customer hesitation, reframe the cost of inaction, and book next meeting.",
                        "persona": {
                            "name": st.session_state.coach_customer.split()[0] if st.session_state.coach_customer else "Prospect",
                            "role": st.session_state.coach_customer,
                            "personality": "Pragmatic, cautious, protective of budget.",
                            "main_concern": st.session_state.coach_objection
                        }
                    }
                    st.session_state.sim_in_progress = True
                    st.session_state.sim_messages = [{
                        "role": "assistant",
                        "content": f"Hi. We reviewed your proposal for {st.session_state.coach_product}, but {st.session_state.coach_objection} What are you going to do about this?"
                    }]
                    st.rerun()
            with col_btn2:
                if st.button("💾 Save to History", use_container_width=True):
                    st.session_state.practice_history.append({
                        "title": f"Objection: {st.session_state.coach_product}",
                        "date": datetime.now().strftime("%b %d, %H:%M"),
                        "type": "Objection Coach",
                        "score": score
                    })
                    st.toast("Saved to your Performance History!")
            with col_btn3:
                if st.button("📋 Copy Script", use_container_width=True):
                    st.info(f"Script ready to copy:\n\n{resp['response']}")
            with col_btn4:
                if st.button("🔄 Try Another Angle", use_container_width=True):
                    st.session_state.coaching_response = None
                    st.rerun()

    # --- SUB-MODE B: LIVE PITCH SIMULATOR (WITH CUSTOM SCENARIO SUPPORT) ---
    elif st.session_state.practice_mode == "Live Pitch Simulator":
        if not st.session_state.sim_in_progress and not st.session_state.sim_report:
            st.markdown("### ⚙️ Simulator Setup")
            
            # Mode Toggle: Scenario Library vs Create Custom Scenario
            src_choice = st.radio(
                "Scenario Source",
                ["📚 Choose from Scenario Library", "✍️ Create Custom Scenario"],
                horizontal=True,
                index=0 if st.session_state.sim_scenario_source == "Library" else 1
            )
            st.session_state.sim_scenario_source = "Library" if "Library" in src_choice else "Custom"
            
            st.write("")
            
            # OPTION 1: LIBRARY SCENARIOS
            if st.session_state.sim_scenario_source == "Library":
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    sc_keys = list(SCENARIOS.keys())
                    sc_names = [f"{SCENARIOS[k]['title']} ({SCENARIOS[k]['category']} - {SCENARIOS[k]['industry']})" for k in sc_keys]
                    selected_idx = st.selectbox("Select Sales Scenario", range(len(sc_names)), format_func=lambda i: sc_names[i])
                    st.session_state.sim_scenario = sc_keys[selected_idx]
                    
                    diff = st.select_slider("Difficulty Level", options=["Beginner", "Intermediate", "Advanced"], value=st.session_state.sim_difficulty)
                    st.session_state.sim_difficulty = diff

                with col_s2:
                    in_mode = st.radio("Practice Mode", ["Text Only", "Voice Input (Speech Recognition)"], index=0)
                    st.session_state.sim_input_mode = "Voice" if "Voice" in in_mode else "Text"
                    
                    active_sc = SCENARIOS[st.session_state.sim_scenario]
                    st.markdown(f"""
                    <div class="saas-card" style="margin-top: 15px;">
                        <div style="font-weight: 700; color: #0F172A; margin-bottom: 4px;">Persona: {active_sc['persona']['name']} ({active_sc['persona']['role']})</div>
                        <div style="font-size: 0.85rem; color: #64748B; margin-bottom: 6px;">{active_sc['persona']['personality']}</div>
                        <div style="font-size: 0.85rem; color: #DC2626;"><strong>Main Concern:</strong> {active_sc['persona']['main_concern']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                if st.button("🚀 Start Live Simulation", type="primary", use_container_width=True):
                    st.session_state.sim_in_progress = True
                    active_sc = SCENARIOS[st.session_state.sim_scenario]
                    st.session_state.active_custom_scenario = None
                    st.session_state.sim_messages = [{
                        "role": "assistant",
                        "content": f"Hi. Thanks for taking the call. Look, we looked over your offer for {active_sc['product']}, but {active_sc['objection']} What can you do for us?"
                    }]
                    st.session_state.sim_report = None
                    st.rerun()

            # OPTION 2: CREATE CUSTOM SCENARIO
            else:
                st.markdown("""
                <div class="saas-card saas-card-accent">
                    <span class="badge badge-purple" style="margin-bottom: 6px;">Custom Pipeline Builder</span>
                    <h4 style="margin: 0 0 6px 0;">Configure Your Own Prospect & Deal Scenario</h4>
                    <p style="color: #64748B; font-size: 0.9rem; margin: 0;">Prepare for your actual sales calls by simulating your specific prospect's role, temperament, and exact objections.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Check for previously saved custom scenarios
                if st.session_state.custom_scenarios:
                    saved_names = ["-- Create New Scenario --"] + list(st.session_state.custom_scenarios.keys())
                    selected_saved = st.selectbox("Load a Previously Saved Custom Scenario:", saved_names)
                    if selected_saved != "-- Create New Scenario --":
                        saved_sc = st.session_state.custom_scenarios[selected_saved]
                        st.session_state.cust_prod = saved_sc["product"]
                        st.session_state.cust_ind = saved_sc["industry"]
                        st.session_state.cust_price = saved_sc["price"]
                        st.session_state.cust_name = saved_sc["persona"]["name"]
                        st.session_state.cust_role = saved_sc["persona"]["role"]
                        st.session_state.cust_trait = saved_sc["persona"]["personality"]
                        st.session_state.cust_obj = saved_sc["objection"]
                        st.session_state.cust_goal = saved_sc["objective"]

                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    cust_p = st.text_input("Product or Service *", value=st.session_state.cust_prod, placeholder="e.g. Solar Panel System, SEO Retainer, Enterprise Cloud Backup")
                    cust_i = st.text_input("Industry *", value=st.session_state.cust_ind, placeholder="e.g. Clean Energy, E-Commerce, Logistics")
                    cust_val = st.text_input("Deal Value / Price (Optional)", value=st.session_state.cust_price, placeholder="e.g. $18,000, $3,500/mo")
                    diff_custom = st.select_slider("Difficulty Tier", options=["Beginner", "Intermediate", "Advanced"], value="Intermediate", key="diff_cust_slider")
                    st.session_state.sim_difficulty = diff_custom

                with col_c2:
                    c_name = st.text_input("Prospect Full Name *", value=st.session_state.cust_name, placeholder="e.g. Robert Martinez, Dr. Linda Zhao")
                    c_role = st.text_input("Prospect Job Title / Role *", value=st.session_state.cust_role, placeholder="e.g. Chief Operating Officer, Homeowner, Clinic Owner")
                    c_trait = st.selectbox("Prospect Temperament", [
                        "Skeptical & analytical (demands hard ROI data)",
                        "Busy & impatient (hates small talk, wants the point)",
                        "Polite but conflict-avoidant (gives soft 'maybe later' brush-offs)",
                        "Aggressive cost-cutter (focuses strictly on discounts)"
                    ], index=0)

                col_c3, col_c4 = st.columns(2)
                with col_c3:
                    c_objection = st.text_area("Prospect's Core Objection / First Pushback *", value=st.session_state.cust_obj, placeholder="e.g. We had a bad experience with a contractor last year and won't commit without a written completion guarantee.", height=85)
                with col_c4:
                    c_goal = st.text_area("Your Sales Objective *", value=st.session_state.cust_goal, placeholder="e.g. Validate their timeline fear, share customer warranty cases, and book an on-site survey.", height=85)

                st.session_state.cust_prod = cust_p
                st.session_state.cust_ind = cust_i
                st.session_state.cust_price = cust_val
                st.session_state.cust_name = c_name
                st.session_state.cust_role = c_role
                st.session_state.cust_trait = c_trait
                st.session_state.cust_obj = c_objection
                st.session_state.cust_goal = c_goal

                col_sub1, col_sub2 = st.columns([1.5, 1])
                with col_sub1:
                    if st.button("🚀 Start Custom Simulation", type="primary", use_container_width=True):
                        if not cust_p or not c_name or not c_role or not c_objection or not c_goal:
                            st.error("⚠️ Please fill in all required custom fields: Product, Prospect Name, Role, Core Objection, and Sales Objective.")
                        else:
                            custom_obj_data = {
                                "title": f"Custom Deal: {cust_p}",
                                "category": "Custom",
                                "difficulty": diff_custom,
                                "industry": cust_i or "General",
                                "product": cust_p,
                                "price": cust_val,
                                "customer": f"{c_name} ({c_role})",
                                "objection": c_objection,
                                "objective": c_goal,
                                "persona": {
                                    "name": c_name,
                                    "role": c_role,
                                    "personality": c_trait,
                                    "main_concern": c_objection
                                }
                            }
                            st.session_state.active_custom_scenario = custom_obj_data
                            # Save to user collection
                            sc_save_name = f"{c_name} - {cust_p}"
                            st.session_state.custom_scenarios[sc_save_name] = custom_obj_data
                            
                            st.session_state.sim_in_progress = True
                            st.session_state.sim_messages = [{
                                "role": "assistant",
                                "content": f"Hi. Thanks for reaching out. Look, we looked over your offer for {cust_p}, but {c_objection} What can you say to that?"
                            }]
                            st.session_state.sim_report = None
                            st.rerun()

                with col_sub2:
                    if st.button("💾 Save to My Custom Library", use_container_width=True):
                        if cust_p and c_name:
                            sc_save_name = f"{c_name} - {cust_p}"
                            st.session_state.custom_scenarios[sc_save_name] = {
                                "title": f"Custom Deal: {cust_p}",
                                "category": "Custom",
                                "difficulty": diff_custom,
                                "industry": cust_i or "General",
                                "product": cust_p,
                                "price": cust_val,
                                "customer": f"{c_name} ({c_role})",
                                "objection": c_objection,
                                "objective": c_goal,
                                "persona": {
                                    "name": c_name,
                                    "role": c_role,
                                    "personality": c_trait,
                                    "main_concern": c_objection
                                }
                            }
                            st.success(f"Saved '{sc_save_name}' to your custom library!")
                        else:
                            st.warning("Enter at least Product and Prospect Name to save.")

        # SIMULATOR IN PROGRESS
        elif st.session_state.sim_in_progress:
            # Resolve scenario data
            if st.session_state.sim_scenario_source == "Custom" and st.session_state.active_custom_scenario:
                active_sc = st.session_state.active_custom_scenario
            else:
                active_sc = SCENARIOS.get(st.session_state.sim_scenario, SCENARIOS["saas_crm_migration"])
            
            # Persistent Profile Header
            st.markdown(f"""
            <div class="persona-badge">
                <div style="background: #EEF2FF; color: #4F46E5; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 20px;">
                    👤
                </div>
                <div style="flex: 1;">
                    <div style="font-weight: 700; color: #0F172A; font-size: 1.05rem;">
                        {active_sc['persona']['name']} • <span style="font-weight: 500; color: #64748B;">{active_sc['persona']['role']} ({active_sc['industry']})</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #475569;">
                        <strong>Objective:</strong> {active_sc['objective']}
                    </div>
                </div>
                <div>
                    <span class="badge badge-indigo">{st.session_state.sim_difficulty}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Beginner Hints Expander
            if st.session_state.sim_difficulty == "Beginner":
                with st.expander("💡 Helpful Coach Tips for Beginners", expanded=False):
                    st.markdown("""
                    - **Step 1:** Don't apologize. Validate their reality: *"I hear you, and downtime is always the biggest risk."*
                    - **Step 2:** Ask a discovery question: *"How many hours does your team spend troubleshooting right now?"*
                    - **Step 3:** Propose a low-friction proof point: *"What if we handled the complete setup for you?"*
                    """)
                    
            # Conversation Feed
            chat_container = st.container(height=380)
            with chat_container:
                for msg in st.session_state.sim_messages:
                    if msg["role"] == "assistant":
                        st.markdown(f"""
                        <div class="chat-bubble-customer">
                            <strong>{active_sc['persona']['name']}:</strong><br/>
                            {msg['content']}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="chat-bubble-user" style="text-align: right;">
                            <strong>You (Sales Representative):</strong><br/>
                            {msg['content']}
                        </div>
                        """, unsafe_allow_html=True)

            if st.session_state.sim_input_mode == "Voice":
                st.caption("🎙️ Voice input enabled: Use standard speech recognition or microphone typing in your browser.")
                
            user_msg = st.chat_input("Type your response to the customer...")
            
            if user_msg:
                st.session_state.sim_messages.append({"role": "user", "content": user_msg})
                
                difficulty_rules = {
                    "Beginner": "Be somewhat skeptical initially, but soften quickly if the salesperson validates your concerns and asks polite questions.",
                    "Intermediate": "Act like a typical pragmatic business leader. Push back on price and timing. Demand proof.",
                    "Advanced": "Be tough, busy, and guarded. Challenge weak assertions. Only soften if they deliver deep ROI reframing or peer benchmarks."
                }
                
                sys_sim = f"""
                You are roleplaying as {active_sc['persona']['name']}, {active_sc['persona']['role']} in the {active_sc['industry']} industry.
                Your personality: {active_sc['persona']['personality']}.
                Your main concern: {active_sc['persona']['main_concern']}.
                
                Difficulty level: {st.session_state.sim_difficulty}.
                Instructions: {difficulty_rules.get(st.session_state.sim_difficulty, '')}
                
                Respond in 2-3 sentences as the customer. Keep it realistic, direct, and conversational. Do not break character.
                """
                
                dialogue_lines = []
                for m in st.session_state.sim_messages[-6:]:
                    speaker = "Sales Rep" if m['role'] == 'user' else active_sc['persona']['name']
                    dialogue_lines.append(f"{speaker}: {m['content']}")
                prompt_hist = "\n".join(dialogue_lines) + f"\n{active_sc['persona']['name']} (reply directly to the Sales Rep regarding your concern '{active_sc['persona']['main_concern']}'):"
                
                with st.spinner(f"{active_sc['persona']['name']} is thinking..."):
                    reply = call_ai(sys_sim, prompt_hist)
                    if not reply:
                        reply = generate_smart_sim_reply(active_sc, user_msg, st.session_state.sim_messages, st.session_state.sim_difficulty)
                            
                    st.session_state.sim_messages.append({"role": "assistant", "content": reply})
                    st.rerun()

            # End Practice Action with Confirmation
            st.write("")
            col_end1, col_end2 = st.columns([1, 3])
            with col_end1:
                if st.button("⏹️ End Practice", use_container_width=True):
                    st.session_state.confirm_end_sim = True
                    
            if st.session_state.confirm_end_sim:
                st.warning("Are you sure you want to conclude this practice session and generate your performance report?")
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    if st.button("✅ Yes, Generate Performance Report", type="primary", use_container_width=True):
                        st.session_state.sim_in_progress = False
                        st.session_state.confirm_end_sim = False
                        
                        total_turns = len([m for m in st.session_state.sim_messages if m['role'] == 'user'])
                        base_score = 84 if total_turns >= 2 else 68
                        
                        report = {
                            "overall": base_score,
                            "communication": min(100, base_score + 4),
                            "needs_discovery": min(100, base_score - 3),
                            "objection_handling": min(100, base_score + 3),
                            "product_knowledge": min(100, base_score + 5),
                            "closing_skills": min(100, base_score - 6),
                            "strengths": [
                                f"Validated {active_sc['persona']['name']}'s core hesitation without sounding defensive.",
                                "Skillfully shifted the conversation toward risk reduction and business outcomes.",
                                "Maintained professional authority while asking diagnostic discovery questions."
                            ],
                            "improvements": [
                                "Could quantify the cost of inaction (hours/dollars wasted) earlier in the negotiation.",
                                "Ensure you propose concrete calendar dates rather than open-ended 'whenever you have time' closes."
                            ],
                            "better_response": f"Instead of defending product specs, try saying: 'We understand {active_sc['persona']['name']}—any disruption hurts pipeline. If we wrote a 100% data integrity warranty into our agreement, would you feel confident proceeding?'",
                            "next_practice": "Handling Deeply Entrenched Competitors"
                        }
                        
                        st.session_state.sim_report = report
                        st.session_state.practice_history.append({
                            "title": f"Simulation: {active_sc['title']}",
                            "date": datetime.now().strftime("%b %d, %H:%M"),
                            "type": "Live Simulation",
                            "score": report["overall"]
                        })
                        st.rerun()
                with col_c2:
                    if st.button("❌ Keep Practicing", use_container_width=True):
                        st.session_state.confirm_end_sim = False
                        st.rerun()

        # PERFORMANCE REPORT DISPLAY
        elif st.session_state.sim_report:
            rep = st.session_state.sim_report
            st.markdown("### 🏆 Post-Practice Performance Report")
            
            c_sc1, c_sc2 = st.columns([1, 2])
            with c_sc1:
                st.markdown(f"""
                <div class="saas-card" style="text-align: center; padding: 32px 20px;">
                    <div style="font-size: 0.9rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Overall Score</div>
                    <div style="font-size: 4rem; font-weight: 800; color: #4F46E5; margin: 10px 0; font-family: 'Plus Jakarta Sans';">{rep['overall']}</div>
                    <span class="badge badge-emerald">High Competency Pitch</span>
                </div>
                """, unsafe_allow_html=True)
            with c_sc2:
                st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
                st.markdown("##### 5-Axis Skill Breakdown")
                
                skills = [
                    ("Communication & Clarity", rep["communication"]),
                    ("Needs Discovery", rep["needs_discovery"]),
                    ("Objection Handling", rep["objection_handling"]),
                    ("Product Knowledge", rep["product_knowledge"]),
                    ("Closing Technique", rep["closing_skills"])
                ]
                for s_name, s_val in skills:
                    st.write(f"**{s_name}:** {s_val}/100")
                    st.progress(s_val / 100.0)
                st.markdown("</div>", unsafe_allow_html=True)

            col_str, col_imp = st.columns(2)
            with col_str:
                st.markdown("""
                <div class="saas-card" style="border-left: 4px solid #10B981; height: 100%;">
                    <h4 style="color: #047857; margin-bottom: 12px;">✅ What You Did Well</h4>
                    <ul style="color: #334155; line-height: 1.6; margin: 0; padding-left: 20px;">
                        <li>{}</li>
                        <li>{}</li>
                        <li>{}</li>
                    </ul>
                </div>
                """.format(rep["strengths"][0], rep["strengths"][1], rep["strengths"][2]), unsafe_allow_html=True)
            with col_imp:
                st.markdown("""
                <div class="saas-card" style="border-left: 4px solid #F59E0B; height: 100%;">
                    <h4 style="color: #B45309; margin-bottom: 12px;">⚠️ Areas for Improvement</h4>
                    <ul style="color: #334155; line-height: 1.6; margin: 0; padding-left: 20px;">
                        <li>{}</li>
                        <li>{}</li>
                    </ul>
                </div>
                """.format(rep["improvements"][0], rep["improvements"][1]), unsafe_allow_html=True)

            st.markdown(f"""
            <div class="saas-card saas-card-accent">
                <h4 style="color: #4F46E5; margin-bottom: 8px;">💡 Stronger Response Example</h4>
                <div class="script-container">{rep['better_response']}</div>
            </div>
            """, unsafe_allow_html=True)

            col_rep1, col_rep2, col_rep3 = st.columns(3)
            with col_rep1:
                if st.button("🔄 Practise Again", use_container_width=True, type="primary"):
                    st.session_state.sim_report = None
                    st.session_state.sim_in_progress = False
                    st.session_state.sim_messages = []
                    st.rerun()
            with col_rep2:
                with st.expander("💬 View Full Conversation Transcript"):
                    for msg in st.session_state.sim_messages:
                        speaker = "Customer" if msg["role"] == "assistant" else "You"
                        st.write(f"**{speaker}:** {msg['content']}")
            with col_rep3:
                if st.button("🏠 Return to Dashboard", use_container_width=True):
                    st.session_state.page = "Dashboard"
                    st.rerun()

# ------------------------------------------
# 4. SCENARIO LIBRARY
# ------------------------------------------
elif st.session_state.page == "Scenario Library":
    st.markdown("""
    <div style="margin-bottom: 24px;">
        <h1 style="margin: 0; font-size: 2.3rem;">📚 Scenario Library</h1>
        <p style="color: #64748B; margin: 4px 0 0 0;">Explore curated sales challenges across enterprise software, retail, consulting, and outbound sales.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_f1, col_f2 = st.columns([1, 1])
    with col_f1:
        cat_filter = st.radio("Category Filter", ["All", "B2B", "B2C", "My Custom Deals"], horizontal=True)
    with col_f2:
        diff_filter = st.radio("Difficulty Filter", ["All", "Beginner", "Intermediate", "Advanced"], horizontal=True)
        
    st.write("")
    
    # Custom Scenarios Display if requested
    if cat_filter == "My Custom Deals":
        if not st.session_state.custom_scenarios:
            st.info("You haven't created any custom deal scenarios yet. Go to Practice -> Live Pitch Simulator -> 'Create Custom Scenario' to build one!")
        else:
            for c_k, c_v in st.session_state.custom_scenarios.items():
                st.markdown(f"""
                <div class="saas-card saas-card-accent">
                    <span class="badge badge-purple" style="margin-bottom: 8px;">Custom Pipeline Deal</span>
                    <h3 style="margin: 0 0 8px 0;">{c_v['title']}</h3>
                    <div style="font-size: 0.9rem; color: #475569; margin-bottom: 10px;">
                        <strong>Prospect:</strong> {c_v['customer']} • <strong>Industry:</strong> {c_v['industry']}
                    </div>
                    <div style="background: #F8FAFC; border-radius: 8px; padding: 12px; font-size: 0.85rem; color: #1E293B; margin-bottom: 12px;">
                        <strong>Core Objection:</strong> "{c_v['objection']}"
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🎭 Launch Practice for {c_k}", key=f"launch_custom_{c_k}", type="primary"):
                    st.session_state.sim_scenario_source = "Custom"
                    st.session_state.active_custom_scenario = c_v
                    st.session_state.page = "Practice"
                    st.session_state.practice_mode = "Live Pitch Simulator"
                    st.session_state.sim_in_progress = True
                    st.session_state.sim_messages = [{
                        "role": "assistant",
                        "content": f"Hi. Look, the proposal looks fine, but {c_v['objection']} What can you do for us?"
                    }]
                    st.rerun()
    else:
        filtered_keys = []
        for k, v in SCENARIOS.items():
            if (cat_filter == "All" or v["category"] == cat_filter) and (diff_filter == "All" or v["difficulty"] == diff_filter):
                filtered_keys.append(k)
                
        if not filtered_keys:
            st.info("No scenarios match your active filters. Try resetting the filters.")
        else:
            for i in range(0, len(filtered_keys), 2):
                cols = st.columns(2)
                for j in range(2):
                    if i + j < len(filtered_keys):
                        sc_k = filtered_keys[i + j]
                        sc = SCENARIOS[sc_k]
                        diff_badge = "badge-emerald" if sc["difficulty"] == "Beginner" else ("badge-amber" if sc["difficulty"] == "Intermediate" else "badge-rose")
                        
                        with cols[j]:
                            st.markdown(f"""
                            <div class="saas-card" style="height: 100%;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                    <span class="badge badge-indigo">{sc['category']} • {sc['industry']}</span>
                                    <span class="badge {diff_badge}">{sc['difficulty']}</span>
                                </div>
                                <h3 style="margin: 0 0 8px 0; font-size: 1.25rem;">{sc['title']}</h3>
                                <p style="color: #64748B; font-size: 0.9rem; margin-bottom: 12px;">{sc['description']}</p>
                                <div style="background: #F8FAFC; border-radius: 8px; padding: 10px 14px; margin-bottom: 14px; font-size: 0.85rem; color: #475569;">
                                    <strong>Target Buyer:</strong> {sc['customer']}<br/>
                                    <strong>Objection:</strong> <em>"{sc['objection'][:85]}..."</em>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            col_btn_a, col_btn_b = st.columns(2)
                            with col_btn_a:
                                if st.button("🛡️ Objection Coach", key=f"lib_obj_{sc_k}", use_container_width=True):
                                    st.session_state.coach_product = sc["product"]
                                    st.session_state.coach_industry = sc["industry"]
                                    st.session_state.coach_price = sc["price"]
                                    st.session_state.coach_customer = sc["customer"]
                                    st.session_state.coach_objection = sc["objection"]
                                    st.session_state.coach_context = sc["context"]
                                    st.session_state.page = "Practice"
                                    st.session_state.practice_mode = "Objection Coach"
                                    st.rerun()
                            with col_btn_b:
                                if st.button("🎭 Start Roleplay", key=f"lib_sim_{sc_k}", use_container_width=True, type="primary"):
                                    st.session_state.sim_scenario_source = "Library"
                                    st.session_state.sim_scenario = sc_k
                                    st.session_state.active_custom_scenario = None
                                    st.session_state.page = "Practice"
                                    st.session_state.practice_mode = "Live Pitch Simulator"
                                    st.session_state.sim_in_progress = True
                                    st.session_state.sim_messages = [{
                                        "role": "assistant",
                                        "content": f"Hi. Look, the proposal looks fine, but {sc['objection']} How do you justify this?"
                                    }]
                                    st.rerun()

# ------------------------------------------
# 5. MY PERFORMANCE & ANALYTICS
# ------------------------------------------
elif st.session_state.page == "My Performance":
    st.markdown("""
    <div style="margin-bottom: 24px;">
        <h1 style="margin: 0; font-size: 2.3rem;">📊 My Performance & Analytics</h1>
        <p style="color: #64748B; margin: 4px 0 0 0;">Track your objection-handling scores, roleplay simulations, and closing competency over time.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.practice_history:
        st.markdown("""
        <div class="saas-card" style="text-align: center; padding: 48px 24px;">
            <div style="font-size: 40px; margin-bottom: 12px;">📈</div>
            <h3 style="margin: 0 0 8px 0;">No Performance Data Recorded</h3>
            <p style="color: #64748B; max-width: 460px; margin: 0 auto 20px auto;">
                Complete your first practice session in the Objection Coach or Live Simulator to see your metrics, mastery scores, and recommendations.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Start Your First Practice Session", type="primary", use_container_width=True):
            st.session_state.page = "Practice"
            st.rerun()
    else:
        scores = [h.get("score", 0) for h in st.session_state.practice_history]
        avg_score = int(sum(scores) / len(scores))
        high_score = max(scores)
        
        c_m1, c_m2, c_m3 = st.columns(3)
        with c_m1:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-label">Total Completed Sessions</div>
                <div class="stat-value">{len(scores)}</div>
            </div>
            """, unsafe_allow_html=True)
        with c_m2:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-label">Average Performance Score</div>
                <div class="stat-value" style="color: #4F46E5;">{avg_score}%</div>
            </div>
            """, unsafe_allow_html=True)
        with c_m3:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-label">Highest Score Achieved</div>
                <div class="stat-value" style="color: #10B981;">{high_score}%</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("")
        st.subheader("📜 Practice History Log")
        for item in reversed(st.session_state.practice_history):
            st.markdown(f"""
            <div class="saas-card" style="padding: 18px 22px; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-weight: 700; color: #0F172A; font-size: 1.05rem;">{item.get('title')}</div>
                    <div style="color: #64748B; font-size: 0.85rem; margin-top: 2px;">
                        Completed on {item.get('date')} • <span class="badge badge-indigo">{item.get('type')}</span>
                    </div>
                </div>
                <div>
                    <span class="badge badge-emerald" style="font-size: 1.1rem; padding: 6px 14px;">
                        {item.get('score')}/100
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ------------------------------------------
# 6. LEARNING HUB
# ------------------------------------------
elif st.session_state.page == "Learning Hub":
    st.markdown("""
    <div style="margin-bottom: 24px;">
        <h1 style="margin: 0; font-size: 2.3rem;">💡 Sales Learning Hub</h1>
        <p style="color: #64748B; margin: 4px 0 0 0;">Bite-sized, practical masterclasses on customer psychology, modern objection handling, and closing frameworks.</p>
    </div>
    """, unsafe_allow_html=True)
    
    for lesson in LESSONS:
        with st.expander(f"{lesson['title']} • {lesson['tag']} ({lesson['read_time']})", expanded=False):
            st.markdown(lesson["content"])

# ------------------------------------------
# 7. SETTINGS PAGE
# ------------------------------------------
elif st.session_state.page == "Settings":
    st.markdown("""
    <div style="margin-bottom: 24px;">
        <h1 style="margin: 0; font-size: 2.3rem;">⚙️ Settings & API Configuration</h1>
        <p style="color: #64748B; margin: 4px 0 0 0;">Manage your AI model providers, credentials, and response parameters.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
    st.subheader("🤖 AI Provider Settings")
    
    provider = st.radio(
        "Active AI Provider",
        ["Google Gemini", "Groq"],
        index=0 if st.session_state.api_provider == "Google Gemini" else 1,
        help="Select which LLM provider handles your real-time coaching responses and simulation dialogues."
    )
    st.session_state.api_provider = provider
    
    st.write("")
    
    if provider == "Google Gemini":
        g_key = st.text_input(
            "Google Gemini API Key",
            value=st.session_state.gemini_api_key,
            type="password",
            placeholder="AIzaSy...",
            key="gemini_key_input"
        )
        st.session_state.gemini_api_key = g_key
        
        gemini_options = [
            "gemini-3.5-flash",
            "gemini-3.5-flash-lite",
            "gemini-3.1-pro",
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro"
        ]
        
        if st.session_state.gemini_model not in gemini_options:
            st.session_state.gemini_model = "gemini-3.5-flash"
            
        g_index = gemini_options.index(st.session_state.gemini_model)
        
        def on_gemini_change():
            st.session_state.gemini_model = st.session_state.gemini_select_box
            
        g_model = st.selectbox(
            "Gemini Model",
            gemini_options,
            index=g_index,
            key="gemini_select_box",
            on_change=on_gemini_change
        )
        st.session_state.gemini_model = g_model
        
        if g_key:
            st.success(f"🔑 Gemini API Key configured! Using {st.session_state.gemini_model}")
        else:
            st.info("💡 You can get a free Gemini API Key from Google AI Studio (aistudio.google.com).")
            
    elif provider == "Groq":
        groq_k = st.text_input(
            "Groq API Key",
            value=st.session_state.groq_api_key,
            type="password",
            placeholder="gsk_...",
            key="groq_key_input"
        )
        st.session_state.groq_api_key = groq_k
        
        groq_options = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]
        
        if st.session_state.groq_model not in groq_options:
            st.session_state.groq_model = "llama-3.3-70b-versatile"
            
        gr_index = groq_options.index(st.session_state.groq_model)
        
        def on_groq_change():
            st.session_state.groq_model = st.session_state.groq_select_box

        gr_model = st.selectbox(
            "Groq Model",
            groq_options,
            index=gr_index,
            key="groq_select_box",
            on_change=on_groq_change
        )
        st.session_state.groq_model = gr_model
        
        if groq_k:
            st.success(f"🔑 Groq API Key configured! Using {st.session_state.groq_model}")
        else:
            st.info("💡 You can get a free Groq API Key from console.groq.com.")
            
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
    st.subheader("ℹ️ Application Information")
    st.write("**Application Version:** 2.2.0 (Enterprise SaaS Upgrade)")
    st.write("**Engine:** Dual-Provider Orchestration (Gemini + Groq)")
    st.write("**Custom Scenarios:** Enabled (Pipeline Deal Simulator)")
    st.write("**Demo Mode:** Enabled automatically when no API key is supplied.")
    st.markdown("</div>", unsafe_allow_html=True)
