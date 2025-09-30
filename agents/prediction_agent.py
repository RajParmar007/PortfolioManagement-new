# 


import torch
import torch.nn as nn
import pickle
import numpy as np
import pandas as pd
import json
import os
from langchain_core.tools import tool

# --- Global Cache for Models and Scalers ---
# This avoids reloading files from disk on every call for the same ticker.
MODELS_CACHE = {}
SCALERS_CACHE = {}

# --- LSTM Model Architecture Definition ---
# This class must be defined at the global scope so the tool can access it.
class BalancedLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size, dropout=0.2):
        super(BalancedLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers,
                            batch_first=True, dropout=dropout if num_layers > 1 else 0)
        self.dropout = nn.Dropout(dropout)
        self.fc1 = nn.Linear(hidden_size, hidden_size // 2)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size // 2, output_size)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.dropout(out[:, -1, :])
        out = self.fc1(out)
        out = self.relu(out)
        out = self.fc2(out)
        return out

@tool("get_stock_prediction", return_direct=False)
def get_stock_prediction(ticker: str) -> str:
    """
    Predicts the next day's stock price movement for a given ticker.
    Uses a pre-trained LSTM model and pre-calculated historical feature data
    stored in local files. The function returns a formatted string with the
    prediction details.
    """
    try:
        device = torch.device('cpu')
        
        # --- 1. Load Model and Scalers (from cache if available) ---
        if ticker not in MODELS_CACHE:
            print(f"Cache miss for {ticker}. Loading model and scalers from disk...")
            MODEL_PATH = f'external_utils/{ticker}_balanced_lstm.pth'
            SCALER_PATH = f'external_utils/{ticker}_balanced_scalers.pkl'
            
            # Gracefully handle cases where a model for the ticker doesn't exist
            if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
                return f"Error: No prediction model is available for the ticker '{ticker}'."
            
            # Load Model
            model_data = torch.load(MODEL_PATH, map_location=device)
            model_config = model_data['model_config']
            model_state_dict = model_data['model_state_dict']
            
            model = BalancedLSTM(
                input_size=model_config['input_size'], hidden_size=model_config['hidden_size'],
                num_layers=model_config['num_layers'], output_size=model_config['output_size'],
                dropout=model_config['dropout']
            )
            model.load_state_dict(model_state_dict)
            model.to(device)
            model.eval()
            MODELS_CACHE[ticker] = model

            # Load Scalers
            with open(SCALER_PATH, 'rb') as f:
                SCALERS_CACHE[ticker] = pickle.load(f)
        
        model = MODELS_CACHE[ticker]
        scalers = SCALERS_CACHE[ticker]
        
        X_mean, X_std = scalers['X_mean'], scalers['X_std']
        y_mean, y_std = scalers['y_mean'], scalers['y_std']
        features, time_steps = scalers['features'], scalers['time_steps']

        # --- 2. Load and Prepare Data from JSON ---
        DATA_PATH = f'data/{ticker}_stock_data.json'
        with open(DATA_PATH, 'r') as f:
            stock_data = json.load(f)

        data = pd.DataFrame.from_dict(stock_data, orient='index')
        data.index = pd.to_datetime(data.index.to_series().astype(float), unit='ms')
        data = data.apply(pd.to_numeric, errors='coerce')
        data.sort_index(inplace=True)
        data.rename(columns={
            'open': 'Open', 'high': 'High', 'low': 'Low', 
            'volume': 'Volume', 'close': 'Close'
        }, inplace=True)
        
        data = data.tail(50).copy()
        data_features = data[features].copy()
        data_features.dropna(inplace=True)

        if len(data_features) < time_steps:
            return f"Error: Not enough data for {ticker} to form a {time_steps}-day sequence."

        # --- 3. Isolate, Scale, and Predict ---
        last_sequence_df = data_features.tail(time_steps)
        scaled_sequence = (last_sequence_df.values - X_mean) / X_std
        input_tensor = torch.tensor(scaled_sequence, dtype=torch.float32).unsqueeze(0).to(device)

        with torch.no_grad():
            scaled_prediction = model(input_tensor)

        # --- 4. Inverse Transform and Format Results ---
        predicted_return = scaled_prediction.item() * y_std + y_mean
        last_close_price = data['Close'].iloc[-1]
        predicted_price = last_close_price * (1 + predicted_return)
        price_change = predicted_price - last_close_price
        
        result = (
            f"Prediction for {ticker}:\n"
            f"  - Last Closing Price: ${last_close_price:.2f}\n"
            f"  - Predicted Return for Next Day: {predicted_return * 100:+.2f}%\n"
            f"  - Predicted Price Change: ${price_change:+.2f}\n"
            f"  - Predicted Next Day Close Price: ${predicted_price:.2f}"
        )
        return result

    except FileNotFoundError as e:
        return f"Error: Missing a required data file for ticker '{ticker}'. Ensure the JSON data file exists. Details: {e}"
    except KeyError as e:
        return f"Error: A required column or key was not found for ticker '{ticker}'. Check data consistency. Details: {e}"
    except Exception as e:
        return f"An unexpected error occurred for ticker '{ticker}': {e}"

# # Example of how to use the tool
if __name__ == '__main__':
    # Make sure you have the required files in the correct directories
    # e.g., external_utils/AVGO_balanced_lstm.pth, data/AVGO_stock_data.json, etc.
    prediction_result = get_stock_prediction("AVGO")
    print(prediction_result)
    # Example for a ticker that doesn't have a model
    prediction_result_fake = get_stock_prediction("FAKETICKER")
    print(prediction_result_fake)