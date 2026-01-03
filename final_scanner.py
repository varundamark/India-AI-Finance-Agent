import pandas as pd
import yfinance as yf
import numpy as np
import time
from datetime import datetime

df = pd.read_csv("agent_shortlist.csv")

final_list = []

for sym in df["Symbol"].head(300):  # testing first 300, we'll scale later
    try:
        stock = yf.Ticker(sym)
        hist = stock.history(period="6mo")

        if hist.empty or len(hist) < 50:
            continue

        close = hist["Close"]
        high = hist["High"]
        low = hist["Low"]
        volume = hist["Volume"]

        # ---- ADI (manual)
        clv = ((close - low) - (high - close)) / (high - low)
        clv = clv.replace([np.inf, -np.inf], 0).fillna(0)
        adi = (clv * volume).cumsum().iloc[-1]

        # ---- MFI (manual, 14 period)
        typical_price = (high + low + close) / 3
        money_flow = typical_price * volume
        pos_mf = np.where(typical_price > typical_price.shift(1), money_flow, 0)
        neg_mf = np.where(typical_price < typical_price.shift(1), money_flow, 0)
        pos_mf = pd.Series(pos_mf, index=hist.index).rolling(14).sum()
        neg_mf = pd.Series(neg_mf, index=hist.index).rolling(14).sum()
        mfi = 100 - (100 / (1 + (pos_mf / (neg_mf + 1e-9)))).iloc[-1]

        # ---- Candlestick breakout reconfirmation
        high_prev = hist["High"].iloc[-2]
        breakout = close.iloc[-1] > high_prev

        # ---- VCP tightening reconfirmation (volatility shrinking)
        hist["range"] = high - low
        vol_shrink = hist["range"].rolling(20).mean().diff().tail(10).lt(0).all()

        # ---- Score composition
        score = 0
        if breakout: score += 35
        if vol_shrink: score += 25
        if adi > 0: score += 20
        if mfi > 50: score += 20

        final_list.append({
            "Symbol": sym,
            "Score": score,
            "ADI": round(adi,2),
            "MFI": round(mfi,2),
            "Breakout": breakout,
            "VolTightening": vol_shrink,
            "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    except Exception as e:
        print("Error:", sym, e)
        continue

    time.sleep(0.2)

df_final = pd.DataFrame(final_list)
df_final = df_final.sort_values(by="Score", ascending=False)
df_final.to_csv("final_shortlist.csv", index=False)

print("\nTop 20 final candidates:")
print(df_final.head(20))
print("\nSaved to final_shortlist.csv")
