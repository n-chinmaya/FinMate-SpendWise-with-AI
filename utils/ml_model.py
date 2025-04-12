import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib

# --- Feature Engineering ---
def prepare_features(df):
    # Convert Date column to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Extract day of the week (0=Monday, 6=Sunday)
    df['DayOfWeek'] = df['Date'].dt.dayofweek
    
    # Extract the week of the year (1 to 52)
    df['WeekOfYear'] = df['Date'].dt.isocalendar().week
    
    # Extract the month
    df['Month'] = df['Date'].dt.month
    
    # Create lag features for previous spending
    df['AmountLag1'] = df['Amount'].shift(1).fillna(0)
    df['AmountLag7'] = df['Amount'].shift(7).fillna(0)  # Spending 7 days ago
    
    # Ensure all required columns are present
    required_columns = ['DayOfWeek', 'WeekOfYear', 'Month', 'AmountLag1', 'AmountLag7']
    for col in required_columns:
        if col not in df.columns:
            df[col] = 0  # Add missing columns with default values
    
    return df

# --- Training the Model ---
def train_model(df):
    df = prepare_features(df)
    
    # Features and target variable
    X = df[['DayOfWeek', 'WeekOfYear', 'Month', 'AmountLag1', 'AmountLag7']]
    y = df['Amount']
    
    # Split the data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Initialize and train the Random Forest Regressor
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Save the model
    joblib.dump(model, "model.pkl")
    
    # Evaluate the model
    test_score = model.score(X_test, y_test)
    print(f"Model R^2 score: {test_score:.4f}")
    
    return model

# --- Predicting Future Spending ---
def predict_future_spending(df):
    # Load the trained model
    model = joblib.load("model.pkl")
    
    # Prepare features for prediction
    df = prepare_features(df)
    latest_data = df.tail(1)  # Use the last available data
    
    # Predict the next day's spending
    prediction = model.predict(latest_data[['DayOfWeek', 'WeekOfYear', 'Month', 'AmountLag1', 'AmountLag7']])
    return prediction[0]