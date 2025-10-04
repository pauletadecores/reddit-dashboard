import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import praw

# ===========================
# Page configuration
# ===========================
st.set_page_config(page_title="Topics on Gaza/Israel/USA", layout="wide")
st.title("📊 Real-Time Topics on Reddit — Gaza / Israel / USA")
st.markdown(
    "Dashboard showing recent Reddit posts related to Gaza, Palestine, Israel, Flotilla Global Sumud, USA, and Trump."
)

# ===========================
# Reddit API credentials (from Streamlit Secrets)
# ===========================
CLIENT_ID = st.secrets["reddit"]["client_id"]
CLIENT_SECRET = st.secrets["reddit"]["client_secret"]
USER_AGENT = st.secrets["reddit"]["user_agent"]

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
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
# Function to fetch posts
# ===========================
@st.cache_data(ttl=300)
def get_reddit_posts(subreddit, limit=50):
    try:
        posts = []
        for post in reddit.subreddit(subreddit).hot(limit=limit):
            posts.append({
                "title": post.title,
                "author": post.author.name if post.author else "",
                "score": post.score,
                "num_comments": post.num_comments,
                "subreddit": subreddit,
                "url": post.url
            })
        return pd.DataFrame(posts)
    except Exception as e:
        st.error(f"Error fetching posts from {subreddit}: {e}")
        return pd.DataFrame()

# ===========================
# Aggregate posts from all subreddits
# ===========================
df_list = [get_reddit_posts(sr) for sr in subreddits]
df = pd.concat(df_list, ignore_index=True) if df_list else pd.DataFrame()

# ===========================
# Filter by keywords
# ===========================
if df.empty:
    st.warning("No posts fetched from Reddit. Check your API credentials or try again later.")
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
