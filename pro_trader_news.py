import streamlit as st
from gnews import GNews
from textblob import TextBlob
from datetime import datetime

st.set_page_config(page_title="Pro Trader News Alerts", layout="wide")
st.title("🚨 Pro Trader Market News Dashboard")

# ========== CONFIG ==========
gn = GNews(language='en', country='US', max_results=50)
CATEGORIES = {
    "Macro/Political": [
        "fed", "inflation", "interest rate", "election", "war", "gdp",
        "unemployment", "recession", "cpi", "conflict", "debt"
    ],
    "Crypto Regulation": [
        "crypto", "bitcoin", "ethereum", "regulation", "sec", "binance", 
        "coinbase", "etf", "ban", "law", "mi ca"
    ],
    "Tech": [
        "ai", "chip", "nvidia", "semiconductor", "cyber", "hacker", 
        "apple", "microsoft", "cloud", "openai", "intel", "quantum"
    ],
    "Market Movers": [
        "earnings", "profit", "merger", "acquisition", "upgrade", 
        "downgrade", "buyback", "ipo", "layoffs"
    ]
}
URGENT_KEYWORDS = [
    "crisis", "emergency", "ban", "lawsuit", "default", "collapse", 
    "arrest", "explosion", "attack", "sanction", "hack", "raid"
]
# =============================

@st.cache_data(ttl=60)
def fetch_news():
    return gn.get_top_news()

def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return "Bullish 🔺", "green"
    elif polarity < -0.1:
        return "Bearish 🔻", "red"
    else:
        return "Neutral ⚪", "gray"

def match_category(title):
    for cat, keywords in CATEGORIES.items():
        if any(k in title.lower() for k in keywords):
            return cat
    return "Other"

def is_urgent(title):
    return any(k in title.lower() for k in URGENT_KEYWORDS)

# === Sidebar Filters ===
st.sidebar.header("⚙️ Filters")
active_cats = st.sidebar.multiselect("News Categories", list(CATEGORIES.keys()), default=list(CATEGORIES.keys()))
only_urgent = st.sidebar.checkbox("🔴 Urgent Only", False)

# === Display News ===
news_items = fetch_news()
filtered = []

for item in news_items:
    title = item['title']
    url = item['url']
    category = match_category(title)
    if category not in active_cats:
        continue
    if only_urgent and not is_urgent(title):
        continue
    sentiment, color = analyze_sentiment(title)
    urgent_flag = "⚠️" if is_urgent(title) else ""
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    filtered.append((category, f"<a href='{url}' target='_blank' style='color:{color}'><b>{sentiment}</b> {urgent_flag}</a><br><a href='{url}' target='_blank'>{title}</a><br><small><i>{category} | {time_str}</i></small><hr>"))

# === Show Results ===
st.markdown(f"### 📰 {len(filtered)} Headlines Found")
for _, html in filtered:
    st.markdown(html, unsafe_allow_html=True)

if not filtered:
    st.info("No news matched your filters.")

st.caption("⏱️ Auto-refreshes every 60 seconds.")
st.experimental_rerun()
