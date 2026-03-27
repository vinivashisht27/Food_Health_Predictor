PureLabel — Food Health Predictor

• What it does:
  - Search and analyze food products from dataset
  - Show nutrition (calories, protein, fat, carbs, sugar, salt)
  - Generate health score (Excellent, Good, Moderate, Caution)
  - Apply smart filters (High Protein, Low Sugar, etc.)
  - Compare up to 4 products
  - Provide visual insights (charts)
  - Allow manual food entry
  - Save favourites and support dark/light mode

• How it works:
  - Uses Atwater formula (Protein*4 + Carbs*4 + Fat*9)
  - Based on WHO and UK FSA standards
  - ML components: food_model.pkl, tfidf_vectorizer.pkl

• Tech Stack:
  - Python, Streamlit
  - Pandas, NumPy
  - Plotly

• Dataset:
  - Open Food Facts (~300k products)
  - https://www.kaggle.com/datasets/openfoodfacts/world-food-facts

• Note:
  - Educational tool, not medical advice
