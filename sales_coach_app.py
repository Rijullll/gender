import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import os
import re
import time

# Set Page Config
st.set_page_config(
    page_title="AI Sales Coach - Handle Objections & Close Deals",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');

    /* Global Fonts & Theme overrides */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
    }

    /* Gradient Title */
    .main-title {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FF8008, #FFC837);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
        text-shadow: 0 4px 12px rgba(255, 128, 8, 0.1);
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: #94a3b8;
        margin-bottom: 2rem;
        font-weight: 300;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25);
    }
    
    .stat-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        box-shadow: inset 0 0 10px rgba(255, 255, 255, 0.01);
    }

    /* Copyable script style */
    .script-box {
        background: rgba(15, 23, 42, 0.6);
        border-left: 4px solid #FF8008;
        padding: 20px;
        border-radius: 4px 12px 12px 4px;
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        line-height: 1.6;
        color: #e2e8f0;
        margin: 15px 0;
    }

    .sms-box {
        background: rgba(15, 23, 42, 0.6);
        border-left: 4px solid #10b981;
        padding: 20px;
        border-radius: 4px 12px 12px 4px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 1rem;
        line-height: 1.5;
        color: #10b981;
        margin: 15px 0;
    }

    /* Custom progress bar styles */
    .progress-container {
        position: relative;
        height: 24px;
        width: 100%;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        margin: 10px 0;
        overflow: hidden;
    }
    
    .progress-bar-fill {
        height: 100%;
        border-radius: 12px;
        text-align: right;
        padding-right: 10px;
        line-height: 24px;
        color: white;
        font-weight: 700;
        font-size: 0.85rem;
        transition: width 1s ease-in-out;
    }
    
    /* Coach speech bubble */
    .coach-bubble {
        background: linear-gradient(135deg, rgba(255, 128, 8, 0.1), rgba(255, 200, 55, 0.1));
        border: 1px solid rgba(255, 128, 8, 0.2);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* Animation classes */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .active-card {
        border: 1px solid rgba(255, 128, 8, 0.4);
        box-shadow: 0 0 15px rgba(255, 128, 8, 0.15);
    }
    
    /* Primary buttons custom */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #FF8008, #FFC837);
        color: #0f172a;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        padding: 0.7rem 2rem;
        font-size: 1.1rem;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 128, 8, 0.3);
    }
    
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 128, 8, 0.45);
        color: #0f172a;
    }
</style>
""", unsafe_allow_html=True)

# Define Presets Dictionary
PRESETS = {
    "Select a Scenario...": None,
    "B2B SaaS - CRM Data Migration Blocker": {
        "product": "Premium AI CRM Software",
        "industry": "Technology / SaaS",
        "customer": "VP of Sales (Mid-market company, 120 reps)",
        "objection": "We already use HubSpot, and it's too much work to migrate our team's data. Our reps hate change and it will disrupt our sales cycle.",
        "price": "$120 per user / month",
        "context": "They complained that HubSpot's analytics are slow and reps don't update fields because it's too clunky. However, the migration cost is their primary hurdle.",
        "demo_result": """
## Customer Analysis
- Customer Type: B2B Enterprise Decision Maker
- Buying Intent: High (They actively complain about current system speed and compliance, indicating strong dissatisfaction)
- Main Concern: Operations disruption and productivity loss during the migration process.
- Pain Points: Slow reporting speeds, rep adoption resistance, administrative overhead.

## Best Sales Response
"I completely understand where you're coming from. A CRM is only as good as the data in it, and if your team stops updating it during a messy migration, that hurts sales. But let me ask you: if we could handle the entire migration for you in the background with zero downtime, and guarantee your reps are trained and active in under 5 days, would you be open to seeing how our real-time reporting can save your reps 4 hours a week?"

## How to Handle the Objection
1. **Empathize & Validate**: Acknowledge the pain of system transition. Do not dismiss the friction of data migration; it is a valid organizational fear.
2. **Reframe the Blocker**: Pivot the discussion from "migration pain" to "daily friction cost". Highlight that they are already paying a weekly productivity tax with their current clunky tool.
3. **De-risk the Migration**: Introduce a white-glove migration package. Show how your team does the heavy lifting, making it a non-event for their sales reps.
4. **Demonstrate the Future Value**: Connect the switch to immediate time-savings (4 hours/rep/week) to justify the short transition period.

## Recommended Sales Technique
- Challenger Sale

Explain why you selected it:
The customer is stuck in status quo bias. They know their current system (HubSpot) is slow, but they fear change more than they hate inefficiency. By using the Challenger Sale, you teach them about the hidden costs of keeping their team on a slow CRM, tailor the message to their VP of Sales role (focusing on lost coaching time), and take control of the transition by showing them a proven migration blueprint.

## Closing Strategy
- Trial Close

Provide an example sentence:
"If we wrote it into our service agreement that our engineering team handles the complete migration and maps all your custom fields for free before you pay a single dollar, would you be comfortable moving forward with a pilot for your East Coast division next month?"

## Follow-up Message
Subject: Streamlining your team's migration (with zero downtime)

Hi [First Name],

It was great chatting today. I completely respect your focus on maintaining your team's sales momentum. 

To help address your migration concerns, I've attached our 90-Day Migration & Training Blueprint which outlines how we transitioned [Competitor Name] with zero downtime. 

If we can handle the heavy lifting to save your team 4 hours per rep every week, is it worth a quick 10-minute sync next Tuesday at 2 PM to look at the transition timeline?

Best,
[Your Name]

## Confidence Score
Confidence Score: 85

## Tips to Increase Success
1. **Offer White-Glove Migration**: Absorb the migration cost or offer dedicated transition engineers to eliminate the fear of technical friction.
2. **Quantify the Inaction Cost**: Calculate the hours lost per month due to slow reports (e.g., 120 reps x 4 hours/week = 480 hours/month wasted).
3. **Use a Phased Rollout**: Suggest starting with a pilot team (e.g., 10 reps) to build internal champions before pushing it company-wide.
4. **Offer a Migration Warranty**: Guarantee data integrity in writing, offering service credits if deadlines or mappings are missed.
5. **Enlist HubSpot Champions**: Identify the 3 most frustrated HubSpot users on their team and get them on a demo early so they can lobby for you.
"""
    },
    "B2C Real Estate - First-time Buyers Waiting on Interest Rates": {
        "product": "Suburban 3-Bedroom Family Home",
        "industry": "Real Estate / Residential",
        "customer": "First-time Homebuyers (Young married couple with a 2-year-old child)",
        "objection": "The house is absolutely perfect for us, but we're worried interest rates are going to drop in the next 6-12 months. We think we should wait and buy then.",
        "price": "$450,000",
        "context": "They are currently renting an apartment for $2,500/month. The school district of this house is excellent, and they want to move in before their child gets older.",
        "demo_result": """
## Customer Analysis
- Customer Type: B2C Family Consumers
- Buying Intent: High (They admit the house is 'perfect' and want the school district)
- Main Concern: Financial anxiety over interest rate fluctuations and missing a 'better deal'.
- Pain Points: Renting is a complete loss of equity ($2,500/mo), fear of overpaying, school enrollment timing.

## Best Sales Response
"I completely understand. Buying your first home is a huge decision, and with rates where they are, waiting sounds sensible. But let me show you the math on that. Right now, you are paying $2,500 a month in rent, which is a 100% interest rate—none of that builds your equity. If rates drop in 6 months, two things will happen: you will have paid $15,000 in rent that you'll never see again, and buyers who were waiting will flood the market, bidding this exact house up by $20,000 or $30,000. If we find a home you love today, you can buy it now and refinance later when rates drop, avoiding the bidding wars. Does that timing make sense?"

## How to Handle the Objection
1. **Validate and Empathize**: Agree that rates are a smart thing to watch. This builds rapport and reduces defensive walls.
2. **Reframe Renting Cost**: Shift their focus from the interest rate to the "rent cost of waiting" ($2,500/month = zero equity build).
3. **Illustrate Supply/Demand Mechanics**: Explain that rate drops trigger demand increases, which drives home prices up, offsetting interest savings.
4. **Offer the Refinance Solution**: Emphasize the real estate adage: "Marry the house, date the rate." You can change your interest rate later; you cannot change your purchase price or school district.

## Recommended Sales Technique
- Consultative Selling

Explain why you selected it:
First-time homebuyers are driven by high emotion and fear of making a mistake. They do not want to be pushed. Consultative Selling positions you as a trusted advisor who lays out the math and market realities, helping them make a logical financial decision that aligns with their personal family goals (school district, space for child).

## Closing Strategy
- Alternative Choice Close

Provide an example sentence:
"Since we know this school district is your top priority, would you prefer to make an offer with a standard 30-day closing so you can move in before the school year starts, or would a 45-day closing give you more time to wrap up your current lease?"

## Follow-up Message
Hi [Name] & [Name],

It was so great walking through the property with you and [Child's Name] today. Seeing how much they loved the backyard was the highlight of my day!

I put together a quick spreadsheet comparing:
1. Buying today + refinancing in 12 months.
2. Renting for another year and buying at a 1% lower rate (but a 5% higher home price).

I think you'll find the numbers surprising. Let me know if I can drop it over WhatsApp or if you'd like to grab a quick coffee tomorrow to go over it!

Best,
[Your Name]

## Confidence Score
Confidence Score: 78

## Tips to Increase Success
1. **Perform the Rent vs. Buy Analysis**: Show them exactly how much equity they lose by paying $2,500 rent for 12 more months ($30,000 total loss).
2. **Explain Bidding War Costs**: Share data on home price spikes from the last rate cut to prove that home prices outpace minor rate drops.
3. **Introduce Preferred Lenders**: Introduce a lender offering a "free refinance" or low-cost refinance option within the next 2 years.
4. **Focus on Quality of Life**: Remind them of the emotional cost of spending another year in a cramped apartment instead of raising their child in this yard.
5. **Suggest a Seller Rate Buy-Down**: Negotiate with the seller to contribute to a 2-1 interest rate buy-down, lowering their payments for the first 2 years.
"""
    },
    "B2B Professional Services - Consulting Budget Objection": {
        "product": "Custom Cybersecurity Audit & Compliance Assessment",
        "industry": "Professional Services / Cyber Security",
        "customer": "CTO (Fintech Startup, 30 employees)",
        "objection": "Your $25k fee is twice what we budgeted for cybersecurity compliance. We are looking at cheap templates online or a smaller local consultant to get it done for $10k.",
        "price": "$25,000 flat fee",
        "context": "They are preparing for a Series A funding round in 3 months. If they fail due diligence, they won't secure funding. The CTO is technical but the CEO holds the budget.",
        "demo_result": """
## Customer Analysis
- Customer Type: B2B Technical Decision Maker (Influencing CEO)
- Buying Intent: High (They need compliance for Series A due diligence)
- Main Concern: Budget mismatch versus the perceived risk of cheap compliance.
- Pain Points: Impending due diligence deadline, startup cash constraints, lack of internal security expertise.

## Best Sales Response
"I completely get it—as a growing startup, every dollar of capital counts, and $25,000 is a real investment. But here is what we are really protecting here: your upcoming Series A. A cheap compliance template might check a box on paper, but VCs hire institutional auditors who will poke holes in a template in five minutes. If your due diligence stalls or fails, it delays a multi-million dollar round. Our audits are built specifically to pass institutional due diligence, and we represent you directly during the audit calls. If we can structure our payment into milestones linked to your funding schedule, would that solve the cash flow concern so you can secure this round with absolute confidence?"

## How to Handle the Objection
1. **Acknowledge Cash Flow Limits**: Show respect for startup cash conservation.
2. **Reframe Compliance Quality**: Shift the context from "checking a compliance box" to "VC risk mitigation". A failed audit is not a $15,000 budget problem; it is a failed funding round problem.
3. **Align with Executive Incentives**: Give the CTO the ammunition they need to sell this up to the CEO (the true budget holder). Focus on risk reduction for the company's valuation.
4. **Offer Payment Flexibility**: Provide milestone payments (e.g., 25% down, 50% on audit delivery, 25% post-funding round) to ease short-term cash flow constraints.

## Recommended Sales Technique
- Value-Based Selling

Explain why you selected it:
The customer is viewing your service as a commodity ("compliance templates"). Value-Based Selling attaches your price tag to the size of the outcome you protect—in this case, a successful Series A funding round worth millions. You are not selling an audit report; you are selling an insurance policy on their venture capital transaction.

## Closing Strategy
- Assumptive Close

Provide an example sentence:
"Let's go ahead and draft the engagement letter with the payments split 30/70, so our cybersecurity team can kick off the vulnerability scan this Monday and keep you exactly on schedule for your October due diligence."

## Follow-up Message
Hi [CTO First Name],

Thanks for the candid chat about budget parameters. I know how critical cash flow management is right before raising a round.

I put together a brief 1-page document detailing 'The 3 Compliance Pitfalls that Stall Startup Series A Rounds' based on audits we did last quarter. 

To help make this work for your board, I spoke with our CFO and got approval to divide our $25k fee into 3 milestone-based payments over the next 4 months. 

I've attached the proposal adjustments. Let's touch base tomorrow morning to see if this helps the CEO green-light the kickoff?

Best regards,
[Your Name]

## Confidence Score
Confidence Score: 82

## Tips to Increase Success
1. **Map Out the Board Deck Slides**: Provide the CTO with 2 slides showing exactly how this audit de-risks VC due diligence, which they can copy directly into their board meetings.
2. **Offer Milestone Payments**: Split the fee to match startup cash availability.
3. **Provide VC Reference Cases**: Share case studies of other startups who used your audit to successfully raise capital from reputable VC firms.
4. **Highlight the 'Audit Defense' Clause**: Emphasize that your fee includes audit representation, meaning your experts handle auditor questions so they don't have to.
5. **Establish a 'No-Delay' Guarantee**: Guarantee in writing that the audit will be completed on time for their diligence window, preventing costly funding delays.
"""
    }
}

# Gemini API Caller
def call_gemini_api(api_key, system_prompt, prompt, model="gemini-1.5-flash"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048
        }
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            res_data = response.json()
            return res_data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            try:
                err_json = response.json()
                err_msg = err_json.get("error", {}).get("message", response.text)
            except:
                err_msg = response.text
                
            if response.status_code == 400:
                st.error(f"⚠️ **Bad Request (400):** {err_msg}\n\n*Tip: The model you selected may not be supported on this API key's tier, or the request format is invalid.*")
            elif response.status_code == 403:
                st.error(f"⚠️ **Invalid API Key (403):** {err_msg}\n\n*Tip: Please check for spelling mistakes, spaces, or restrictions on your Gemini API key in Google AI Studio.*")
            elif response.status_code == 429:
                st.error(f"⚠️ **Rate Limit Exceeded (429):** {err_msg}\n\n*Tip: You are using the free tier and have sent too many requests. Wait 60 seconds and try again.*")
            else:
                st.error(f"⚠️ **Google API Error ({response.status_code}):** {err_msg}")
            return None
    except Exception as e:
        st.error(f"Failed to connect to the model: {str(e)}")
        return None

# Parse Structured response
def parse_coach_response(text):
    sections = {
        "customer_analysis": "",
        "best_sales_response": "",
        "how_to_handle": "",
        "recommended_technique": "",
        "closing_strategy": "",
        "follow_up_message": "",
        "confidence_score": "50",
        "tips_to_increase_success": ""
    }
    
    headers = [
        ("Customer Analysis", "customer_analysis"),
        ("Best Sales Response", "best_sales_response"),
        ("How to Handle the Objection", "how_to_handle"),
        ("Recommended Sales Technique", "recommended_technique"),
        ("Closing Strategy", "closing_strategy"),
        ("Follow-up Message", "follow_up_message"),
        ("Confidence Score", "confidence_score"),
        ("Tips to Increase Success", "tips_to_increase_success")
    ]
    
    for i, (title, key) in enumerate(headers):
        next_title = headers[i+1][0] if i+1 < len(headers) else None
        
        if next_title:
            pattern = re.compile(rf"##\s*{re.escape(title)}\s*\n(.*?)(?=\n##\s*{re.escape(next_title)})", re.DOTALL | re.IGNORECASE)
        else:
            pattern = re.compile(rf"##\s*{re.escape(title)}\s*\n(.*)", re.DOTALL | re.IGNORECASE)
            
        match = pattern.search(text)
        if match:
            sections[key] = match.group(1).strip()
        else:
            # Alt pattern search
            pattern_alt = re.compile(rf"##\s*{re.escape(title)}.*?\n(.*?)(?=\n##|$)", re.DOTALL | re.IGNORECASE)
            match_alt = pattern_alt.search(text)
            if match_alt:
                sections[key] = match_alt.group(1).strip()
    
    # Try to extract the score cleanly
    score_txt = sections["confidence_score"]
    numbers = re.findall(r"\b\d{1,3}\b", score_txt)
    for num in numbers:
        val = int(num)
        if 0 <= val <= 100:
            sections["confidence_score"] = str(val)
            break
            
    return sections

# --- App Layout Header ---
st.markdown('<div class="main-title">🏆 AI Sales Coach</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">15+ Years of Expert B2B & B2C Sales Objection Handling, Closing Strategies, and Pitch Design.</div>', unsafe_allow_html=True)

# --- Sidebar Configuration ---
with st.sidebar:
    st.markdown("### ⚙️ Coach Settings")
    
    # API Key handling
    env_key = os.getenv("GEMINI_API_KEY", "")
    api_key_input = st.text_input(
        "Gemini API Key",
        value=env_key,
        type="password",
        placeholder="AIzaSy..."
    )
    
    if api_key_input:
        st.success("🔑 API Key configured successfully!")
    else:
        st.warning("⚠️ Using DEMO mode with mock analysis. Enter an API key to test custom objections.")

    model_option = st.selectbox(
        "AI Coaching Model",
        [
            "gemini-3.5-flash",
            "gemini-3.5-flash-lite",
            "gemini-3.1-pro",
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro"
        ],
        index=5  # Default to gemini-1.5-flash as the most robust free fallback
    )
    
    st.divider()
    
    # Presets Selector
    st.markdown("### 💡 Quick Load Scenarios")
    preset_choice = st.selectbox(
        "Select a template to auto-fill inputs:",
        options=list(PRESETS.keys())
    )
    
    st.divider()
    st.info("💡 **Coach Tip:** The best objection handlers validate the customer first, then reframe the value before asking a closing question.")

# Initialize session state variables
if "product" not in st.session_state:
    st.session_state.product = ""
if "industry" not in st.session_state:
    st.session_state.industry = ""
if "customer" not in st.session_state:
    st.session_state.customer = ""
if "objection" not in st.session_state:
    st.session_state.objection = ""
if "price" not in st.session_state:
    st.session_state.price = ""
if "context" not in st.session_state:
    st.session_state.context = ""
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "sim_intro_sent" not in st.session_state:
    st.session_state.sim_intro_sent = False

# Auto-populate inputs when preset choice changes
if preset_choice != "Select a Scenario..." and PRESETS[preset_choice] is not None:
    data = PRESETS[preset_choice]
    st.session_state.product = data["product"]
    st.session_state.industry = data["industry"]
    st.session_state.customer = data["customer"]
    st.session_state.objection = data["objection"]
    st.session_state.price = data["price"]
    st.session_state.context = data["context"]
    # Clear previous chat session when changing presets
    st.session_state.chat_history = []
    st.session_state.sim_intro_sent = False

# Workspace Layout tabs
tab_coach, tab_simulator = st.tabs(["📊 Objection Coach & Advisor", "💬 Live Pitch Simulator"])

# --- TAB 1: COACH AND ADVISOR ---
with tab_coach:
    # Form layout
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📝 Customer Objection Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        product_input = st.text_input(
            "Product or Service Name",
            value=st.session_state.product,
            placeholder="e.g., Enterprise Cybersecurity Audit, Luxury Watches, CRM SaaS",
            key="product_widget"
        )
        industry_input = st.text_input(
            "Industry",
            value=st.session_state.industry,
            placeholder="e.g., Professional Services, Retail, Technology",
            key="industry_widget"
        )
        target_cust = st.text_input(
            "Target Customer",
            value=st.session_state.customer,
            placeholder="e.g., Mid-market VP of Sales, CTO of fintech startup, Young couple",
            key="customer_widget"
        )
        
    with col2:
        price_input = st.text_input(
            "Price (Optional)",
            value=st.session_state.price,
            placeholder="e.g., $25,000 flat, $120/mo, $450,000",
            key="price_widget"
        )
        objection_input = st.text_area(
            "Customer Objection",
            value=st.session_state.objection,
            placeholder="e.g., Your price is too high; We don't have budget; I need to wait; We use competitor X.",
            height=68,
            key="objection_widget"
        )
        context_input = st.text_area(
            "Additional Context (Optional)",
            value=st.session_state.context,
            placeholder="e.g., They are raising a Series A funding soon; They are currently renting a house; etc.",
            height=68,
            key="context_widget"
        )
        
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Trigger Coaching button
    st.write("")
    analyze_btn = st.button("🧠 Generate Expert Coach Response", use_container_width=True)
    
    # Process Analysis request
    if analyze_btn:
        if not product_input or not target_cust or not objection_input:
            st.error("⚠️ Please fill in at least the **Product Name**, **Target Customer**, and the **Customer Objection** fields to get coaching.")
        else:
            # Sync session state
            st.session_state.product = product_input
            st.session_state.industry = industry_input
            st.session_state.customer = target_cust
            st.session_state.objection = objection_input
            st.session_state.price = price_input
            st.session_state.context = context_input
            
            with st.spinner("Analyzing objection, mapping sales methodologies, and composing script..."):
                # Handle demo results for presets if no API key
                is_preset = preset_choice in PRESETS and PRESETS[preset_choice] is not None
                if not api_key_input and is_preset:
                    time.sleep(1.0) # Premium feel delay
                    raw_text = PRESETS[preset_choice]["demo_result"]
                    st.session_state.analysis_results = parse_coach_response(raw_text)
                    st.toast("Loaded pre-computed coach analysis in DEMO mode!")
                else:
                    if not api_key_input:
                        st.error("⚠️ Gemini API Key is required for analyzing custom inputs. Please enter your key in the sidebar.")
                    else:
                        # Call API
                        system_instructions = """
                        You are an expert AI Sales Coach with 15+ years of experience in B2B and B2C sales.
                        Your job is to help sales representatives handle customer objections, improve their pitch, and increase their chances of closing a sale.

                        Analyze the information provided and generate a response that matches the following format exactly. Do not skip any headers.

                        ## Customer Analysis
                        - Customer Type: [Detail who they are]
                        - Buying Intent: [High/Medium/Low with rationale]
                        - Main Concern: [The underlying driver of their objection]
                        - Pain Points: [Key issues they need solved]

                        ## Best Sales Response
                        [Natural, empathetic script they can say verbatim. Make it sound human and persuasive, not sales-y]

                        ## How to Handle the Objection
                        [Provide step-by-step logic, psychology, and transitions]

                        ## Recommended Sales Technique
                        [Choose one: SPIN Selling, Consultative Selling, Challenger Sale, or Value-Based Selling. Explain why in details]

                        ## Closing Strategy
                        [Choose one: Assumptive Close, Urgency Close, Alternative Choice Close, or Trial Close. Explain why, and write an example sentence]

                        ## Follow-up Message
                        [Short, high-conversion WhatsApp or Email script]

                        ## Confidence Score
                        Confidence Score: [Provide a number from 1 to 100 based on transaction complexity and objection resistance]

                        ## Tips to Increase Success
                        [Provide exactly 5 bullet points with clear, actionable ideas to make closing more likely]
                        """
                        
                        prompt = f"""
                        Analyze this sales scenario:
                        - Product/Service: {product_input}
                        - Industry: {industry_input}
                        - Target Customer: {target_cust}
                        - Customer Objection: {objection_input}
                        - Price: {price_input if price_input else 'Not specified'}
                        - Context: {context_input if context_input else 'None provided'}
                        """
                        
                        raw_text = call_gemini_api(api_key_input, system_instructions, prompt, model_option)
                        if raw_text:
                            st.session_state.analysis_results = parse_coach_response(raw_text)
                            st.toast("Coach Analysis Generated!")
                            
                            # Clean up simulator state to align with new scenario
                            st.session_state.chat_history = []
                            st.session_state.sim_intro_sent = False

    # Render results dashboard if available in state
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
        
        # Grid layout for Dashboard
        col_res1, col_res2 = st.columns([1.1, 0.9])
        
        with col_res1:
            # 1. Customer analysis & Recommended technique side-by-side
            st.markdown("<div class='glass-card active-card'>", unsafe_allow_html=True)
            st.subheader("🎯 Coach's Strategic Analysis")
            
            # Sub columns
            col_sub1, col_sub2 = st.columns(2)
            with col_sub1:
                st.markdown("##### 👥 Customer Profile")
                # Format bullets nicely
                cust_analysis = results["customer_analysis"]
                st.markdown(cust_analysis)
            with col_sub2:
                st.markdown("##### ⚙️ Methodology & Close")
                st.markdown(f"**Recommended Technique:**")
                st.markdown(results["recommended_technique"])
                st.write("")
                st.markdown(f"**Closing Strategy:**")
                st.markdown(results["closing_strategy"])
                
            st.markdown("</div>", unsafe_allow_html=True)
            
            # 2. How to Handle the objection step by step
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.subheader("🗺️ Step-by-Step Objection Handling Plan")
            st.markdown(results["how_to_handle"])
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_res2:
            # 3. Confidence score & Success tips
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.subheader("📊 Likelihood of Closing")
            
            score_val = 50
            try:
                score_val = int(results["confidence_score"])
            except:
                pass
                
            # Determine color theme based on score
            if score_val >= 75:
                bar_color = "linear-gradient(90deg, #10b981, #059669)" # Green
                status_txt = "Strong closing potential. High intent present."
            elif score_val >= 50:
                bar_color = "linear-gradient(90deg, #f59e0b, #d97706)" # Amber
                status_txt = "Standard closing likelihood. Success rests on negotiation execution."
            else:
                bar_color = "linear-gradient(90deg, #ef4444, #dc2626)" # Red
                status_txt = "Hard objection. High risk of losing deal without perfect execution."
            
            st.markdown(f"""
            <div class='stat-card'>
                <h4 style="margin: 0; color: #94a3b8; font-size: 0.95rem; text-transform: uppercase;">Confidence Score</h4>
                <div style="font-size: 3.5rem; font-weight: 800; margin: 10px 0; background: {bar_color}; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    {score_val}%
                </div>
                <div class="progress-container">
                    <div class="progress-bar-fill" style="width: {score_val}%; background: {bar_color};"></div>
                </div>
                <p style="font-size: 0.85rem; color: #94a3b8; margin: 5px 0 0 0;">{status_txt}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
            
            st.markdown("##### 🚀 5 Actionable Tips to Close")
            st.markdown(results["tips_to_increase_success"])
            st.markdown("</div>", unsafe_allow_html=True)
            
        # Full width blocks for Script & Messages
        st.divider()
        st.subheader("💬 Ready-to-Use Scripts & Outreach Templates")
        
        tab_speech, tab_outreach = st.tabs(["🗣️ Objection Response Script", "✉️ WhatsApp / Email Follow-up"])
        
        with tab_speech:
            st.markdown("💡 **What to say directly to the customer:**")
            st.markdown(f"<div class='script-box'>{results['best_sales_response']}</div>", unsafe_allow_html=True)
            st.caption("Copy this script and adapt it to your natural voice. Ensure you pause to let the client absorb the questions.")
            
        with tab_outreach:
            st.markdown("💡 **Warm follow-up outreach message:**")
            st.markdown(f"<div class='sms-box'>{results['follow_up_message']}</div>", unsafe_allow_html=True)
            st.caption("Use this follow-up immediately after the call or meeting to keep momentum alive.")


# --- TAB 2: INTERACTIVE SIMULATOR ---
with tab_simulator:
    st.subheader("🎭 Objection Roleplay Simulator")
    
    # Validation check
    if not st.session_state.product or not st.session_state.objection:
        st.info("💡 Please complete the objection analysis on the **Objection Coach & Advisor** tab first to set up the simulator scenario.")
    else:
        st.markdown(f"""
        <div class="coach-bubble">
            <strong>Coach's Simulator Setup:</strong><br/>
            You are speaking to a <strong>{st.session_state.customer}</strong> in the <strong>{st.session_state.industry}</strong> industry. 
            They are looking at buying <strong>{st.session_state.product}</strong>, but they have objection: 
            <em>"{st.session_state.objection}"</em>.<br/><br/>
            Type your response below to practice handling this objection. I will roleplay as the customer, reply to you, and give you coaching tips on your sales pitch.
        </div>
        """, unsafe_allow_html=True)
        
        # Check if we have an API Key for chat
        if not api_key_input:
            st.warning("⚠️ Practice simulator is disabled in DEMO mode because it requires live conversational AI. Enter your Gemini API Key in the sidebar to begin roleplaying!")
        else:
            # Set up introductory customer prompt if chat is empty
            if not st.session_state.chat_history:
                st.session_state.chat_history = [
                    {
                        "role": "assistant",
                        "content": f"Hi. Look, the proposal you sent for {st.session_state.product} looks fine, but we've got some major concerns. Honestly, {st.session_state.objection} What can you do for us here?"
                    }
                ]
            
            # Display chat messages
            chat_container = st.container(height=400)
            with chat_container:
                for msg in st.session_state.chat_history:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])
            
            # User input chat box
            user_input = st.chat_input("Type your response to the customer...")
            
            if user_input:
                # Add user pitch to history
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                with chat_container:
                    with st.chat_message("user"):
                        st.markdown(user_input)
                
                # Call LLM to respond as customer + give sidebar coaching comments
                sim_system = f"""
                You are roleplaying as a customer and their sales coach concurrently.
                Scenario:
                - Product: {st.session_state.product}
                - Customer Role: {st.session_state.customer}
                - Objection: {st.session_state.objection}
                - Additional Context: {st.session_state.context}
                
                Your response must contain two parts:
                1. **Customer Response**: Respond in character as the customer. Be realistic. If the salesperson's pitch is empathy-driven, structured, and addresses your core concern, show signs of softening. If it is high-pressure, argumentative, or fails to address the concern, push back harder.
                2. **Coach's Feedback**: Break character and provide 2-3 lines of expert coaching tips (in brackets [COACH FEEDBACK]...[/COACH FEEDBACK]). Evaluate if they validated your objection, reframed the value, or asked an engaging open-ended question.
                """
                
                # Build context from recent history
                history_prompt = ""
                for msg in st.session_state.chat_history[-6:]: # look back last 6 responses
                    history_prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"
                
                history_prompt += "Assistant (Customer + Coach feedback):"
                
                with st.spinner("Customer is thinking of their reply..."):
                    reply = call_gemini_api(api_key_input, sim_system, history_prompt, model_option)
                    if reply:
                        st.session_state.chat_history.append({"role": "assistant", "content": reply})
                        st.rerun()
