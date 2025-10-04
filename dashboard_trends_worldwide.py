import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ===========================
# Page configuration
# ===========================
st.set_page_config(page_title="Topics on Gaza/Israel/USA", layout="wide")
st.title("📊 Real-Time Topics on Reddit — Gaza / Israel / USA")
st.markdown(
    "Dashboard showing recent Reddit posts related to Gaza, Palestine, Israel, Flotilla Global Sumud, USA, and Trump."
)

# ===========================
# Relevant subreddits
# ===========================
subreddits = ["worldnews", "politics", "news", "MiddleEast", "Israel", "Palestine"]

# ===========================
# Keywords to filter posts
# ===========================
keywords = ["gaza", "palestina", "israel", "flotilla global sumud", "eua", "trump"]
keywords = [k.lower() for k in keywords]

# ===========================
# Function to fetch posts from Reddit
# ===========================
@st.cache_data(ttl=300)  # Cache results for 5 minutes
def get_reddit_posts(subreddit):
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=50"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        st.write(f"Subreddit: {subreddit} — Status code: {r.status_code}")
        r.raise_for_status()
        data = r.json().get("data", {})
        posts = data.get("children", [])
    except Exception as e:
        st.error(f"Error fetching posts from {subreddit}: {e}")
        return pd.DataFrame()
    
    if not posts:
        st.info(f"No posts found for subreddit: {subreddit}")
        return pd.DataFrame()
    
    data_list = []
    for p in posts:
        post = p.get("data", {})
        data_list.append({
            "title": post.get("title", ""),
            "author": post.get("author", ""),
            "score": post.get("score", 0),
            "num_comments": post.get("num_comments", 0),
            "subreddit": subreddit,
            "url": "https://www.reddit.com" + post.get("permalink", "")
        })
    return pd.DataFrame(data_list)

# ===========================
# Aggregate posts from all subreddits
# ===========================
df_list = [get_reddit_posts(sr) for sr in subreddits]
df = pd.concat(df_list, ignore_index=True) if df_list else pd.DataFrame()

# ===========================
# Filter by keywords
# ===========================
if df.empty:
    st.warning("No posts fetched from Reddit. Try again later or check the API limits.")
else:
    mask = df["title"].str.lower().apply(lambda x: any(k in x for k in keywords))
    df_filtered = df[mask]

    if df_filtered.empty:
        st.warning("No posts found matching the specified keywords.")
    else:
        st.subheader("🔥 Recent posts related to selected topics")
        st.dataframe(
            df_filtered[["title", "subreddit", "score", "num_comments"]]
            .sort_values(by="score", ascending=False),
            use_container_width=True
        )

        # ===========================
        # Engagement chart (Top 10)
        # ===========================
        top_posts = df_filtered.sort_values(by="score", ascending=False).head(10)
        fig = px.bar(
            top_posts,
            x="title",
            y="score",
            text="num_comments",
            labels={"title": "Topic", "score": "Upvotes", "num_comments": "Comments"},
            title="Top 10 posts — Score vs Comments"
        )
        fig.update_xaxes(showticklabels=False)
        st.plotly_chart(fig, use_container_width=True)

        # ===========================
        # Word cloud of post titles
        # ===========================
        st.subheader("🗯️ Word Cloud of Titles")
        text = " ".join(df_filtered["title"].tolist())
        if text.strip():
            wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
            fig_wc, ax = plt.subplots(figsize=(10,5))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig_wc)
        else:
            st.info("No titles available to generate the word cloud.")
