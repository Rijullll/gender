import streamlit as st
import pandas as pd
import numpy as np
import joblib
import time
import os

# Set page config for a premium wide layout
st.set_page_config(
    page_title="Gender Prediction AI",
    page_icon="🧬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom CSS for premium styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

    /* Font styling */
    .stApp {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Main container and title */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FF007F, #7F00FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
        padding-top: 1rem;
    }
    
    .subtitle {
        font-size: 1.15rem;
        color: #8a99ad;
        text-align: center;
        margin-bottom: 2.5rem;
        font-weight: 300;
    }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
    }
    
    /* Custom Result Cards */
    .result-card-female {
        background: linear-gradient(135deg, rgba(255, 0, 127, 0.08), rgba(127, 0, 255, 0.08));
        border: 2px solid #FF007F;
        border-radius: 16px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(255, 0, 127, 0.15);
        animation: fadeIn 0.8s ease-in-out;
    }
    
    .result-card-male {
        background: linear-gradient(135deg, rgba(0, 127, 255, 0.08), rgba(127, 0, 255, 0.08));
        border: 2px solid #007FFF;
        border-radius: 16px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 127, 255, 0.15);
        animation: fadeIn 0.8s ease-in-out;
    }
    
    .result-label {
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #8a99ad;
        margin-bottom: 0.5rem;
    }
    
    .result-value-female {
        font-size: 3.5rem;
        font-weight: 800;
        color: #FF007F;
        margin-bottom: 0.8rem;
        text-shadow: 0 0 15px rgba(255, 0, 127, 0.4);
    }
    
    .result-value-male {
        font-size: 3.5rem;
        font-weight: 800;
        color: #007FFF;
        margin-bottom: 0.8rem;
        text-shadow: 0 0 15px rgba(0, 127, 255, 0.4);
    }
    
    .confidence-text {
        font-size: 1.1rem;
        font-weight: 500;
        color: #e2e8f0;
    }
    
    /* Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Custom style for streamlit native elements if possible */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #FF007F, #7F00FF);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 2.5rem;
        font-size: 1.1rem;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(127, 0, 255, 0.4);
    }
    
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 0, 127, 0.5);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to check model availability
def check_model_files():
    return os.path.exists('model.joblib') and os.path.exists('categories.joblib')

# App Header
st.markdown("<div class='main-title'>🧬 Gender Prediction AI</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>A machine learning application predicting gender classification based on personal preferences</div>", unsafe_allow_html=True)

if not check_model_files():
    st.error("⚠️ Model files (`model.joblib` or `categories.joblib`) not found! Please run the training script `train_model.py` first to generate the files.")
    st.info("You can run the script using the following command in your terminal:\n`python train_model.py`")
else:
    # Load model and categories mapping
    @st.cache_resource
    def load_model_and_metadata():
        model = joblib.load('model.joblib')
        categories = joblib.load('categories.joblib')
        return model, categories
    
    model, categories = load_model_and_metadata()
    
    # Wrap input form in a sleek Glassmorphism Card container
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    
    st.subheader("🎨 Tell us about your preferences")
    
    # 2x2 Grid Layout for inputs
    col1, col2 = st.columns(2)
    
    with col1:
        color = st.selectbox(
            "Favorite Color Theme",
            options=categories['Favorite Color'],
            help="Choose the tone of your favorite colors."
        )
        
        soft_drink = st.selectbox(
            "Favorite Soft Drink",
            options=categories['Favorite Soft Drink'],
            help="What soft drink do you prefer?"
        )
        
    with col2:
        music = st.selectbox(
            "Favorite Music Genre",
            options=categories['Favorite Music Genre'],
            help="What genre of music do you listen to most?"
        )
        
        beverage = st.selectbox(
            "Favorite Beverage",
            options=categories['Favorite Beverage'],
            help="What is your preferred beverage choice?"
        )
        
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Action button
    st.write("") # Spacer
    predict_clicked = st.button("🔮 Predict Gender Identity")
    
    if predict_clicked:
        with st.spinner("Analyzing preferences and executing model..."):
            time.sleep(1.0) # Add a small deliberate delay for premium feel and feedback
            
            # Formulate the input row as a pandas DataFrame matching train data columns
            input_df = pd.DataFrame([{
                'Favorite Color': color,
                'Favorite Music Genre': music,
                'Favorite Beverage': beverage,
                'Favorite Soft Drink': soft_drink
            }])
            
            # Predict and get probabilities
            prediction = model.predict(input_df)[0]
            probabilities = model.predict_proba(input_df)[0]
            
            # Find index of the predicted class to get its specific confidence
            classes = model.classes_
            pred_idx = np.where(classes == prediction)[0][0]
            confidence = probabilities[pred_idx] * 100
            
            # Render beautiful prediction results based on gender
            st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
            
            if prediction == 'Female':
                st.markdown(f"""
                <div class="result-card-female">
                    <div class="result-label">Predicted Profile</div>
                    <div class="result-value-female">♀️ Female</div>
                    <div class="confidence-text">Model Confidence: {confidence:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="result-card-male">
                    <div class="result-label">Predicted Profile</div>
                    <div class="result-value-male">♂️ Male</div>
                    <div class="confidence-text">Model Confidence: {confidence:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.balloons()

    # Expander for dataset details and stats
    with st.expander("📊 Dataset Insights & Model Metrics", expanded=False):
        st.markdown("""
        ### About the Model
        The application is powered by a **Decision Tree Classifier** trained on survey data collected from university students. 
        It learns pattern mappings between lifestyle choices (colors, music, drinks) and binary gender identities.
        
        - **Training Features**: Favorite Color, Music Genre, Beverage, Soft Drink
        - **Classification Algorithm**: Scikit-Learn `DecisionTreeClassifier`
        - **Model Accuracy (Cross-Validation)**: `~54.6%`
        """)
        
        # Load raw dataset to show distribution charts
        if os.path.exists('dataset.csv'):
            raw_data = pd.read_csv('dataset.csv')
            
            st.markdown("### Feature Distribution in Dataset")
            
            feat_to_plot = st.selectbox("Select Feature to view Distribution:", ['Favorite Color', 'Favorite Music Genre', 'Favorite Beverage', 'Favorite Soft Drink'])
            
            # Show a nice interactive bar chart using streamlit built-in function
            dist_df = raw_data.groupby([feat_to_plot, 'Gender']).size().unstack(fill_value=0)
            dist_df.columns = ['Female (F)', 'Male (M)']
            st.bar_chart(dist_df)
            
            st.markdown("### Sample Raw Data rows (Total: 66 entries)")
            st.dataframe(raw_data.head(5), use_container_width=True)
