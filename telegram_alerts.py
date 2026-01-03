import requests
import pandas as pd

TOKEN = "8469692637:AAGjmIAjZXMwSvMbKzTgyeYq47G1lSOn_7w"
CHAT_ID = "8230796725"

df = pd.read_csv("enriched_shortlist.csv")

top = df.sort_values(by="Score", ascending=False).head(10)

msg = "Top 10 NSE breakout candidates:\n"
for i, row in top.iterrows():
    msg += f"{row['Symbol']} | Score: {row['Score']} | MarketCap: {row['MarketCap']}\n"

requests.get(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    params={"chat_id": CHAT_ID, "text": msg}
)

print("Alert sent")
