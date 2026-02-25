import pandas as pd
import numpy as np

def load_and_clean_data(filepath):
    print("Reading file... please wait.")
    
    # Detect format
    try:
        df_temp = pd.read_csv(filepath, sep=None, engine='python', nrows=0)
    except:
        df_temp = pd.read_csv(filepath, sep='\t', nrows=0)
        
    actual_columns = df_temp.columns.tolist()
    grade_col = next((c for c in ['nutrition_grade_fr', 'nutriscore_grade'] if c in actual_columns), None)

    # Core components easily found on every packet
    cols_to_use = [
        'product_name', 'ingredients_text', 'energy_100g', 'fat_100g', 
        'saturated-fat_100g', 'trans-fat_100g', 'carbohydrates_100g',
        'sugars_100g', 'salt_100g', 'proteins_100g', 'fiber_100g', grade_col
    ]
    
    # Filter for columns that exist
    cols_present = [c for c in cols_to_use if c in actual_columns]
    df = pd.read_csv(filepath, sep=None, engine='python', usecols=cols_present, on_bad_lines='skip')
    
    # Fill missing nutritional values with 0
    num_cols = df.select_dtypes(include=[np.number]).columns
    df[num_cols] = df[num_cols].fillna(0)
    df = df.dropna(subset=['product_name', 'ingredients_text', grade_col])

    # Convert Grade to Score
    score_map = {'a': 100, 'b': 75, 'c': 50, 'd': 25, 'e': 0}
    df['health_score'] = df[grade_col].str.lower().map(score_map)
    
    return df

try:
    df = load_and_clean_data('open-food-facts-initial-filter.csv')
    df.to_csv('cleaned_food_data.csv', index=False)
    print("✅ Success! Cleaned data ready for Search & ML.")
except Exception as e:
    print(f"❌ Error: {e}")