import yfinance as yf
import pandas as pd
from datetime import datetime
import os

def calculate_prediction(row):
    score = 0
    try:
        # Prediction Logic
        if float(row['Total Beat %']) > 75: score += 2
        if float(row['P/E']) != 'N/A' and float(row['P/E']) < 30: score += 1
        if float(row['D/E']) != 'N/A' and float(row['D/E']) < 150: score += 1
        
        if score >= 3: return "High"
        if score == 2: return "Medium"
        return "Low"
    except:
        return "Neutral"

def main():
    # TEST LIST: We use these for the test to ensure we get data
    test_tickers = ["AAPL", "MSFT", "TSLA", "NVDA", "GOOGL"]
    
    today = datetime.now().strftime('%Y-%m-%d')
    report_data = []

    print(f"Starting test for: {today}")

    for symbol in test_tickers:
        try:
            print(f"Processing {symbol}...")
            tk = yf.Ticker(symbol)
            info = tk.info
            
            # Get historical earnings to calculate Beat %
            # Note: .earnings_dates is the most reliable yfinance call for this
            hist = tk.earnings_dates
            if hist is not None and not hist.empty and 'Surprise(%)' in hist.columns:
                # Filter out rows where Surprise is NaN
                valid_surprises = hist['Surprise(%)'].dropna()
                beats = len(valid_surprises[valid_surprises > 0])
                total = len(valid_surprises)
                beat_pct = (beats / total) * 100 if total > 0 else 0
            else:
                beat_pct = 0

            data = {
                "Date": today,
                "Company Name": info.get('longName', 'N/A'),
                "Ticker": symbol,
                "Sector": info.get('sector', 'N/A'),
                "Category": info.get('industry', 'N/A'),
                "P/E": info.get('forwardPE', 'N/A'),
                "P/S": info.get('priceToSalesTrailing12Months', 'N/A'),
                "D/E": info.get('debtToEquity', 'N/A'),
                "Total Beat %": round(beat_pct, 2)
            }
            
            data["Beat Prediction"] = calculate_prediction(data)
            report_data.append(data)
            
        except Exception as e:
            print(f"Error on {symbol}: {e}")

    # Save Results
    if report_data:
        df = pd.DataFrame(report_data)
        os.makedirs("reports", exist_ok=True)
        filename = f"reports/test_run_{today}.csv"
        df.to_csv(filename, index=False)
        print(f"Successfully saved {filename}")
    else:
        print("No data collected.")

if __name__ == "__main__":
    main()
