import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
import joblib

def main():
    # 1. Load dataset
    print("Loading dataset...")
    df = pd.read_csv('dataset.csv')
    
    # 2. Separate features and target
    X = df.drop(columns=['Gender'])
    y = df['Gender'].map({'F': 'Female', 'M': 'Male'})
    
    print("\nDataset columns:", X.columns.tolist())
    print("Dataset shape:", df.shape)
    
    # Identify categorical columns
    categorical_cols = X.columns.tolist()
    
    # 3. Define candidate models
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
        ]
    )
    
    models = {
        'Logistic Regression': LogisticRegression(C=1.0, max_iter=1000, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42),
        'Decision Tree': DecisionTreeClassifier(max_depth=5, random_state=42)
    }
    
    # 4. Evaluate models using cross-validation
    best_score = -1
    best_model_name = None
    best_pipeline = None
    
    print("\nEvaluating models via 5-fold cross-validation:")
    for name, model in models.items():
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', model)
        ])
        # Use StratifiedKFold cross-validation
        scores = cross_val_score(pipeline, X, y, cv=5, scoring='accuracy')
        mean_score = np.mean(scores)
        print(f"- {name}: Mean Accuracy = {mean_score:.4f} (+/- {np.std(scores):.4f})")
        
        if mean_score > best_score:
            best_score = mean_score
            best_model_name = name
            best_pipeline = pipeline

    print(f"\nBest model selected: {best_model_name} with {best_score:.4f} accuracy")
    
    # 5. Retrain the best model on the entire dataset
    print(f"Retraining {best_model_name} on the full dataset...")
    best_pipeline.fit(X, y)
    
    # 6. Save the trained pipeline
    model_filename = 'model.joblib'
    joblib.dump(best_pipeline, model_filename)
    print(f"Model successfully saved to '{model_filename}'")
    
    # Save the categories for Streamlit reference
    categories = {}
    for col in categorical_cols:
        categories[col] = sorted(df[col].dropna().unique().tolist())
    joblib.dump(categories, 'categories.joblib')
    print("Categories reference saved to 'categories.joblib'")

if __name__ == '__main__':
    main()
