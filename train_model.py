import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

df = pd.read_csv('cleaned_food_data.csv')

# NLP for ingredients
tfidf = TfidfVectorizer(max_features=100, stop_words='english')
ing_features = tfidf.fit_transform(df['ingredients_text'].astype(str)).toarray()

# Core 8 Nutrients
num_cols = ['energy_100g', 'fat_100g', 'saturated-fat_100g', 'trans-fat_100g', 
            'carbohydrates_100g', 'sugars_100g', 'salt_100g', 'proteins_100g', 'fiber_100g']

X = np.hstack((df[num_cols].values, ing_features))
y = df['health_score']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save everything
joblib.dump(model, 'food_model.pkl')
joblib.dump(tfidf, 'tfidf_vectorizer.pkl')
print(f"✅ Model Trained. Accuracy: {model.score(X_test, y_test)*100:.2f}%")