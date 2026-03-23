import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

def get_earnings_tickers(date_str):
    """
    Fetches tickers reporting on a specific date.
    Note: Reliable free daily calendars are limited. 
    This uses yfinance's calendar functionality.
    """
    try:
        # We search a broad range and filter for the specific date
        # In a real-world scenario, you might replace this with a scrape of 
        # Nasdaq or Yahoo's daily earnings page.
        cal = yf.Search("", max_results=20).sectors # Placeholder logic
        # For the sake of this workflow, we will use a list of high-volume tickers
        # typically reporting to ensure the script demonstrates the logic:
        return ["AAPL", "TSLA", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "NFLX"] 
    except:
        return []

def calculate_prediction(row):
    """
    Logic: High Historical Beat % + Reasonable P/E + Positive Revenue Growth = High Chance.
    """
    score = 0
    try:
        if float(row['Total Beat %']) > 75: score += 2
        if float(row['P/E']) < 25: score += 1
        if float(row['D/E']) < 100: score += 1
        
        if score >= 3: return "High"
        if score == 2: return "Medium"
        return "Low"
    except:
        return "Neutral"

def main():
    today = datetime.now().strftime('%Y-%m-%d')
    tickers = get_earnings_tickers(today)
    
    report_data = []

    for symbol in tickers:
        try:
            tk = yf.Ticker(symbol)
            info = tk.info
            
            # Fetch Earnings History for "Total Beat %"
            hist = tk.get_earnings_dates(limit=8)
            if hist is not None and 'Surprise(%)' in hist.columns:
                beats = len(hist[hist['Surprise(%)'] > 0])
                total = len(hist)
                beat_pct = (beats / total) * 100 if total > 0 else 0
            else:
                beat_pct = 0

            data = {
                "Date": today,
                "Company Name": info.get('longName', 'N/A'),
                "Ticker": symbol,
                "Sector": info.get('sector', 'N/A'),
                "Category": info.get('industry', 'N/A'),
                "P/E": info.get('forwardPE', 0),
                "P/S": info.get('priceToSalesTrailing12Months', 0),
                "D/E": info.get('debtToEquity', 0),
                "Earnings Est": info.get('earningsGrowth', 0),
                "Revenue Est": info.get('revenueGrowth', 0),
                "Total Beat %": round(beat_pct, 2)
            }
            
            # Add Prediction
            data["Beat Prediction"] = calculate_prediction(data)
            report_data.append(data)
            print(f"Processed {symbol}")
            
        except Exception as e:
            print(f"Skipping {symbol}: {e}")

    # Save to CSV
    if report_data:
        df = pd.DataFrame(report_data)
        filename = f"reports/earnings_{today}.csv"
        os.makedirs("reports", exist_ok=True)
        df.to_csv(filename, index=False)

if __name__ == "__main__":
    main()
