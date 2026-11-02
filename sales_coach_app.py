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

# --- MODERN SAAS LIGHT THEME & STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap');

    /* Global Base */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #F8FAFC;
        color: #0F172A;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        color: #0F172A;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    /* Modern SaaS Hero Banner */
    .saas-hero {
        background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%);
        border-radius: 20px;
        padding: 42px 40px;
        color: white;
        margin-bottom: 28px;
        box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.25), 0 8px 10px -6px rgba(79, 70, 229, 0.15);
        position: relative;
        overflow: hidden;
    }
    
    .saas-hero h1 {
        color: white;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 8px;
    }
    
    .saas-hero p {
        color: #E0E7FF;
        font-size: 1.15rem;
        max-width: 680px;
        line-height: 1.6;
        margin-bottom: 20px;
    }

    /* Clean Card System */
    .saas-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04), 0 1px 2px -1px rgba(15, 23, 42, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }
    
    .saas-card:hover {
        border-color: #CBD5E1;
        box-shadow: 0 6px 20px -4px rgba(15, 23, 42, 0.08);
    }
    
    .saas-card-accent {
        border-left: 4px solid #4F46E5;
    }

    /* Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }
    
    .badge-indigo { background-color: #EEF2FF; color: #4338CA; border: 1px solid #E0E7FF; }
    .badge-emerald { background-color: #ECFDF5; color: #047857; border: 1px solid #D1FAE5; }
    .badge-amber { background-color: #FFFBEB; color: #B45309; border: 1px solid #FEF3C7; }
    .badge-blue { background-color: #EFF6FF; color: #1D4ED8; border: 1px solid #DBEAFE; }
    .badge-rose { background-color: #FFF1F2; color: #BE123C; border: 1px solid #FFE4E6; }

    /* Metric & Stat Cards */
    .stat-box {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px 20px;
        text-align: left;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 500;
        margin-bottom: 4px;
    }
    
    .stat-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0F172A;
        font-family: 'Outfit', sans-serif;
    }

    /* Script & Response Display */
    .script-container {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #4F46E5;
        border-radius: 8px;
        padding: 18px 20px;
        font-size: 1.05rem;
        line-height: 1.65;
        color: #1E293B;
        margin: 12px 0;
    }

    /* Chat Elements */
    .chat-bubble-customer {
        background: #F1F5F9;
        border: 1px solid #E2E8F0;
        border-radius: 14px 14px 14px 2px;
        padding: 14px 18px;
        margin-bottom: 14px;
        color: #0F172A;
        line-height: 1.5;
    }
    
    .chat-bubble-user {
        background: #EEF2FF;
        border: 1px solid #C7D2FE;
        border-radius: 14px 14px 2px 14px;
        padding: 14px 18px;
        margin-bottom: 14px;
        color: #312E81;
        line-height: 1.5;
    }

    /* Streamlit UI Button Overrides */
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0.55rem 1.25rem;
        transition: all 0.15s ease-in-out;
    }
    
    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15);
    }
    
    /* Persona Card */
    .persona-badge {
        display: flex;
        align-items: center;
        gap: 12px;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 20px;
    }

    /* Subtle divider */
    hr {
        border-color: #E2E8F0;
        margin: 24px 0;
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
    st.session_state.page = "Dashboard"

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

# Performance History
if "practice_history" not in st.session_state:
    st.session_state.practice_history = []

# --- API HELPER FUNCTIONS ---
def call_gemini_api(api_key, system_prompt, prompt, model="gemini-1.5-flash"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2048}
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            res_data = response.json()
            return res_data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            try:
                err_msg = response.json().get("error", {}).get("message", response.text)
            except:
                err_msg = response.text
            st.error(f"⚠️ Google API Error ({response.status_code}): {err_msg}")
            return None
    except Exception as e:
        st.error(f"Connection error to Gemini: {str(e)}")
        return None

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
                
    # Fallbacks if raw headers didn't match cleanly
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

# --- NAVIGATION SIDEBAR ---
with st.sidebar:
    # Logo & Brand Header
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
        <div style="background: #4F46E5; color: white; width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: 800;">
            🎯
        </div>
        <div>
            <h3 style="margin: 0; font-size: 1.25rem; font-weight: 800; color: #0F172A;">AI Sales Coach</h3>
            <p style="margin: 0; font-size: 0.75rem; color: #64748B; font-weight: 500;">Practice Smarter. Sell Better.</p>
        </div>
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
    
    # Quick Status Badge
    active_key = st.session_state.gemini_api_key if st.session_state.api_provider == "Google Gemini" else st.session_state.groq_api_key
    if active_key:
        st.markdown(f'<span class="badge badge-emerald">🟢 {st.session_state.api_provider} Active</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-amber">⚪ Demo Mode Active</span>', unsafe_allow_html=True)
        st.caption("Add an API key in **Settings** for live generative practice, or test using preloaded scenarios.")
        
    st.write("")
    if st.button("🌐 View Landing Page", use_container_width=True):
        st.session_state.page = "Landing"
        st.rerun()

# ==========================================
# PAGE ROUTING
# ==========================================

# ------------------------------------------
# 1. LANDING PAGE
# ------------------------------------------
if st.session_state.page == "Landing":
    st.markdown("""
    <div class="saas-hero">
        <span class="badge badge-indigo" style="background: rgba(255,255,255,0.2); color: white; border: none; margin-bottom: 12px;">Next-Gen Sales Enablement</span>
        <h1>Practice Smarter. Sell Better.</h1>
        <p>Master objection handling, refine your pitch, and close deals with confidence. Experience interactive, high-stakes sales roleplays with real-time AI critique tailored to your exact industry.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_c1, col_c2, col_c3 = st.columns([1, 1, 1])
    with col_c1:
        if st.button("🚀 Enter Dashboard", use_container_width=True, type="primary"):
            st.session_state.page = "Dashboard"
            st.rerun()
    with col_c2:
        if st.button("🎯 Start Objection Coach", use_container_width=True):
            st.session_state.page = "Practice"
            st.session_state.practice_mode = "Objection Coach"
            st.rerun()
    with col_c3:
        if st.button("📚 Browse Scenario Library", use_container_width=True):
            st.session_state.page = "Scenario Library"
            st.rerun()

    st.write("")
    st.subheader("💡 How It Works")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="saas-card">
            <span class="badge badge-blue">Step 1</span>
            <h4 style="margin-top: 10px;">Choose a Scenario</h4>
            <p style="color: #64748B; font-size: 0.95rem;">Select from our curated B2B and B2C scenario library or input your exact prospect objection, product details, and target buyer persona.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="saas-card">
            <span class="badge badge-indigo">Step 2</span>
            <h4 style="margin-top: 10px;">Practise with AI</h4>
            <p style="color: #64748B; font-size: 0.95rem;">Roleplay in a live conversational simulation against an AI prospect who reacts to your tone, empathy, discovery questions, and closing tactics.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="saas-card">
            <span class="badge badge-emerald">Step 3</span>
            <h4 style="margin-top: 10px;">Receive Instant Coaching</h4>
            <p style="color: #64748B; font-size: 0.95rem;">Get comprehensive analytics, psychographic objection breakdowns, better verbatim responses, and a quantitative score out of 100.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.subheader("⚡ Core Features Built for High-Performance Teams")
    f1, f2 = st.columns(2)
    with f1:
        st.markdown("""
        <div class="saas-card saas-card-accent">
            <h4>🛡️ Tactical Objection Coach</h4>
            <p style="color: #64748B;">Instantly analyze tough objections like price, timing, competitor lock-in, and feature gaps. Get proven scripts backed by SPIN Selling and the Challenger Sale.</p>
        </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown("""
        <div class="saas-card saas-card-accent">
            <h4>🎭 Live Pitch Roleplay Simulator</h4>
            <p style="color: #64748B;">Step into realistic customer dialogues across Beginner, Intermediate, and Advanced difficulty tiers. Build muscle memory before talking to real prospects.</p>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------
# 2. DASHBOARD
# ------------------------------------------
elif st.session_state.page == "Dashboard":
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px;">
        <div>
            <h1 style="margin: 0; font-size: 2.2rem;">Welcome to AI Sales Coach 👋</h1>
            <p style="margin: 4px 0 0 0; color: #64748B; font-size: 1.05rem;">Your personal AI sales mentor for mastering objections, pitch practice, and deal closing.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Action CTA Banner
    st.markdown("""
    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 20px 24px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
        <div>
            <h4 style="margin: 0 0 4px 0;">Ready to sharpen your pitch today?</h4>
            <p style="margin: 0; color: #64748B; font-size: 0.9rem;">Choose a scenario or handle an upcoming customer pushback.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 2 Big Feature Cards
    fc1, fc2 = st.columns(2)
    with fc1:
        st.markdown("""
        <div class="saas-card saas-card-accent" style="height: 100%;">
            <div style="font-size: 28px; margin-bottom: 8px;">🛡️</div>
            <h3 style="margin: 0 0 8px 0;">Handle Customer Objections</h3>
            <p style="color: #64748B; font-size: 0.95rem; line-height: 1.5; margin-bottom: 16px;">
                Enter a tough objection from a real prospect. Get psychological analysis, natural verbal scripts, and strategic closing techniques in seconds.
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
            <div style="font-size: 28px; margin-bottom: 8px;">🎭</div>
            <h3 style="margin: 0 0 8px 0;">Practice Your Sales Pitch</h3>
            <p style="color: #64748B; font-size: 0.95rem; line-height: 1.5; margin-bottom: 16px;">
                Roleplay against adaptive AI customer personas. Practice negotiation, handle pushbacks in real time, and receive an automated performance score.
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
            <div class="stat-label">Overall Performance Score</div>
            <div class="stat-value" style="color: #4F46E5;">{score_display}</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Scenarios Available</div>
            <div class="stat-value">{len(SCENARIOS)}</div>
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
    # Recent Practice Sessions & Recommended Scenarios
    col_rec, col_sugg = st.columns([1.2, 0.8])
    with col_rec:
        st.subheader("⏱️ Recent Practice Sessions")
        if not st.session_state.practice_history:
            st.markdown("""
            <div class="saas-card" style="text-align: center; padding: 36px 20px;">
                <div style="font-size: 32px; margin-bottom: 10px;">📋</div>
                <h4 style="margin: 0 0 6px 0; color: #475569;">No Practice Sessions Yet</h4>
                <p style="color: #94A3B8; font-size: 0.9rem; max-width: 400px; margin: 0 auto 16px auto;">
                    Complete your first practice session to see your progress, scores, and performance analytics.
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
        <h1 style="margin: 0; font-size: 2.2rem;">Sales Practice Studio</h1>
        <p style="color: #64748B; margin: 4px 0 0 0;">Select your practice mode below to either formulate objection responses or roleplay live.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sub navigation tabs
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
        # Quick Load Preset Selector
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

        # 3-Step Guided Layout
        st.markdown("### 📝 Objection Details")
        
        c_step1, c_step2 = st.columns(2)
        with c_step1:
            st.markdown("""
            <div class="saas-card">
                <span class="badge badge-indigo" style="margin-bottom: 8px;">Step 1</span>
                <h4 style="margin: 0 0 16px 0;">Product Information</h4>
            </div>
            """, unsafe_allow_html=True)
            
            p_name = st.text_input("Product or Service Name *", value=st.session_state.coach_product, placeholder="e.g. NextGen CRM SaaS, Cybersecurity Audit")
            p_ind = st.text_input("Industry", value=st.session_state.coach_industry, placeholder="e.g. Technology, Real Estate, Healthcare")
            p_price = st.text_input("Price / Contract Value (Optional)", value=st.session_state.coach_price, placeholder="e.g. $120/mo, $25,000 flat, $450,000")

        with c_step2:
            st.markdown("""
            <div class="saas-card">
                <span class="badge badge-blue" style="margin-bottom: 8px;">Step 2</span>
                <h4 style="margin: 0 0 16px 0;">Customer Information</h4>
            </div>
            """, unsafe_allow_html=True)
            
            c_target = st.text_input("Target Customer *", value=st.session_state.coach_customer, placeholder="e.g. VP of Sales, CTO of fintech startup, First-time buyer")
            c_obj = st.text_area("Customer Objection *", value=st.session_state.coach_objection, placeholder="e.g. Your price is 30% higher than competitor X; We don't have budget.", height=95)
            c_ctx = st.text_input("Additional Context (Optional)", value=st.session_state.coach_context, placeholder="e.g. They are raising Series A soon; currently renting.")

        # Update session states
        st.session_state.coach_product = p_name
        st.session_state.coach_industry = p_ind
        st.session_state.coach_price = p_price
        st.session_state.coach_customer = c_target
        st.session_state.coach_objection = c_obj
        st.session_state.coach_context = c_ctx

        # Action Buttons
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

        # Handle Generation
        if gen_clicked:
            if not p_name or not c_target or not c_obj:
                st.error("⚠️ Please fill in all required fields marked with an asterisk (*): Product Name, Target Customer, and Customer Objection.")
            else:
                with st.spinner("Analyzing objection psychology and drafting expert coaching response..."):
                    # Check for API call
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
                        # Demo Mode fallback
                        time.sleep(0.8)
                        st.session_state.coaching_response = generate_mock_coaching(p_name, c_target, c_obj, p_price)
                        st.toast("Coaching generated in Demo Mode!")

        # Display Structured Coaching Results
        if st.session_state.coaching_response:
            resp = st.session_state.coaching_response
            st.markdown("---")
            st.markdown("### 🎯 Coaching Recommendations")
            
            # Score Banner
            score = resp.get("score", 85)
            score_color = "#10B981" if score >= 75 else "#F59E0B"
            st.markdown(f"""
            <div class="saas-card" style="display: flex; justify-content: space-between; align-items: center; border-left: 4px solid {score_color};">
                <div>
                    <h4 style="margin: 0; color: #0F172A;">Deal Closing Likelihood Score</h4>
                    <p style="margin: 0; color: #64748B; font-size: 0.85rem;">Based on objection severity and reframing leverage</p>
                </div>
                <div style="font-size: 2.2rem; font-weight: 800; color: {score_color}; font-family: 'Outfit';">
                    {score}%
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Content Blocks
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
            
            # Action Buttons
            col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
            with col_btn1:
                if st.button("🎭 Practise This Objection", use_container_width=True, type="primary"):
                    st.session_state.practice_mode = "Live Pitch Simulator"
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

    # --- SUB-MODE B: LIVE PITCH SIMULATOR ---
    elif st.session_state.practice_mode == "Live Pitch Simulator":
        # Check if simulator is active or in setup
        if not st.session_state.sim_in_progress and not st.session_state.sim_report:
            st.markdown("### ⚙️ Simulator Setup")
            
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                sc_keys = list(SCENARIOS.keys())
                sc_names = [f"{SCENARIOS[k]['title']} ({SCENARIOS[k]['category']} - {SCENARIOS[k]['industry']})" for k in sc_keys]
                selected_idx = st.selectbox("Select Sales Scenario", range(len(sc_names)), format_func=lambda i: sc_names[i])
                st.session_state.sim_scenario = sc_keys[selected_idx]
                
                diff = st.select_slider("Difficulty Level", options=["Beginner", "Intermediate", "Advanced"], value="Intermediate")
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
                st.session_state.sim_messages = [{
                    "role": "assistant",
                    "content": f"Hi. Thanks for taking the call. Look, we looked over your offer for {active_sc['product']}, but {active_sc['objection']} What can you do for us?"
                }]
                st.session_state.sim_report = None
                st.rerun()

        # SIMULATOR IN PROGRESS
        elif st.session_state.sim_in_progress:
            active_sc = SCENARIOS.get(st.session_state.sim_scenario, SCENARIOS["saas_crm_migration"])
            
            # Persistent Profile Header
            st.markdown(f"""
            <div class="persona-badge">
                <div style="background: #EEF2FF; color: #4F46E5; width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px;">
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

            # Voice Input Option
            if st.session_state.sim_input_mode == "Voice":
                st.caption("🎙️ Voice input enabled: Use standard speech recognition or microphone typing in your browser.")
                
            # Input Box
            user_msg = st.chat_input("Type your response to the customer...")
            
            if user_msg:
                st.session_state.sim_messages.append({"role": "user", "content": user_msg})
                
                # Check for AI reply
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
                
                prompt_hist = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.sim_messages[-6:]])
                prompt_hist += "\nCustomer Response:"
                
                with st.spinner(f"{active_sc['persona']['name']} is thinking..."):
                    reply = call_ai(sys_sim, prompt_hist)
                    if not reply:
                        # Fallback Demo simulation responses
                        user_turn_count = len([m for m in st.session_state.sim_messages if m['role'] == 'user'])
                        if user_turn_count == 1:
                            reply = "That sounds good in theory, but my team has heard software vendors promise 'smooth transitions' before. What happens if your engineers drop the ball midway through the quarter?"
                        elif user_turn_count == 2:
                            reply = "Fair point on the productivity loss with our current setup. But how do you propose we structure the pricing so my CFO doesn't reject this immediately?"
                        else:
                            reply = "Alright, if you can put that migration warranty in writing and guarantee milestone payments, I'm open to seeing a 15-minute demo on Friday."
                            
                    st.session_state.sim_messages.append({"role": "assistant", "content": reply})
                    st.rerun()

            # End Practice Action with Confirmation
            st.write("")
            col_end1, col_end2 = st.columns([1, 3])
            with col_end1:
                if st.button("⏹️ End Practice", use_container_width=True):
                    st.session_state.confirm_end_sim = True
                    
            if st.session_state.confirm_end_sim:
                st.warning("Are you sure you want to conclude this practice session and view your performance report?")
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    if st.button("✅ Yes, Generate Performance Report", type="primary", use_container_width=True):
                        st.session_state.sim_in_progress = False
                        st.session_state.confirm_end_sim = False
                        
                        # Generate Mock / AI Performance Report
                        total_turns = len([m for m in st.session_state.sim_messages if m['role'] == 'user'])
                        base_score = 82 if total_turns >= 2 else 65
                        
                        report = {
                            "overall": base_score,
                            "communication": min(100, base_score + 5),
                            "needs_discovery": min(100, base_score - 4),
                            "objection_handling": min(100, base_score + 2),
                            "product_knowledge": min(100, base_score + 6),
                            "closing_skills": min(100, base_score - 8),
                            "strengths": [
                                "Maintained professional composure and validated the customer's initial fear.",
                                "Avoided defensive arguments when the prospect challenged pricing.",
                                "Successfully guided the dialogue toward business outcomes rather than feature lists."
                            ],
                            "improvements": [
                                "Could have asked a deeper discovery question regarding the cost of inaction earlier in the call.",
                                "Allowed the customer to dictate the meeting agenda without setting clear next-step criteria."
                            ],
                            "better_response": "Instead of saying 'our software is easy to learn', try saying: 'We provide dedicated onboarding engineers who map your data in the background so your reps lose zero active selling hours.'",
                            "next_practice": "Handling Competitor Lock-In (Snowflake / Tableau)"
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
            
            # Score Overview
            c_sc1, c_sc2 = st.columns([1, 2])
            with c_sc1:
                st.markdown(f"""
                <div class="saas-card" style="text-align: center; padding: 30px;">
                    <div style="font-size: 0.9rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Overall Score</div>
                    <div style="font-size: 4rem; font-weight: 800; color: #4F46E5; margin: 10px 0; font-family: 'Outfit';">{rep['overall']}</div>
                    <span class="badge badge-emerald">Proficient Sales Pitch</span>
                </div>
                """, unsafe_allow_html=True)
            with c_sc2:
                st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
                st.markdown("##### Skill Breakdown")
                
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

            # Strengths & Improvements
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

            # Better Response Example
            st.markdown(f"""
            <div class="saas-card saas-card-accent">
                <h4 style="color: #4F46E5; margin-bottom: 8px;">💡 Stronger Response Example</h4>
                <div class="script-container">{rep['better_response']}</div>
            </div>
            """, unsafe_allow_html=True)

            # Buttons
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
        <h1 style="margin: 0; font-size: 2.2rem;">📚 Scenario Library</h1>
        <p style="color: #64748B; margin: 4px 0 0 0;">Explore real-world sales challenges across B2B enterprise software, retail, consulting, and outbound sales.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filters
    col_f1, col_f2 = st.columns([1, 1])
    with col_f1:
        cat_filter = st.radio("Category Filter", ["All", "B2B", "B2C"], horizontal=True)
    with col_f2:
        diff_filter = st.radio("Difficulty Filter", ["All", "Beginner", "Intermediate", "Advanced"], horizontal=True)
        
    st.write("")
    
    # Filter scenarios
    filtered_keys = []
    for k, v in SCENARIOS.items():
        if (cat_filter == "All" or v["category"] == cat_filter) and (diff_filter == "All" or v["difficulty"] == diff_filter):
            filtered_keys.append(k)
            
    if not filtered_keys:
        st.info("No scenarios match your active filters. Try resetting the filters.")
    else:
        # Display Grid
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
                                st.session_state.sim_scenario = sc_k
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
        <h1 style="margin: 0; font-size: 2.2rem;">📊 My Performance & Analytics</h1>
        <p style="color: #64748B; margin: 4px 0 0 0;">Track your objection-handling scores, roleplay simulations, and competency growth over time.</p>
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
        <h1 style="margin: 0; font-size: 2.2rem;">💡 Sales Learning Hub</h1>
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
        <h1 style="margin: 0; font-size: 2.2rem;">⚙️ Settings & API Configuration</h1>
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
    st.write("**Application Version:** 2.0.0 (SaaS Redesign)")
    st.write("**Engine:** Dual-Provider Orchestration (Gemini + Groq)")
    st.write("**Demo Mode:** Enabled automatically when no API key is supplied.")
    st.markdown("</div>", unsafe_allow_html=True)
