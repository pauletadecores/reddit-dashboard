# Reddit Dashboard — Real-Time Topics on Gaza/Israel/USA

This Streamlit dashboard shows real-time trending posts from Reddit related to Gaza, Palestine, Israel, Flotilla Global Sumud, USA, and Trump.

## Features

- Aggregates posts from multiple subreddits: `worldnews`, `politics`, `news`, `MiddleEast`, `Israel`, `Palestine`
- Filters posts by keywords
- Displays top 10 posts by score (upvotes)
- Shows a Word Cloud of post titles
- Updates every 5 minutes

## How to Run

1. Create a Reddit app to get your `client_id` and `client_secret`: [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Set up a Streamlit Secret for your credentials:

<pre> ``` 
  [reddit] 
  client_id = "YOUR_CLIENT_ID" 
  client_secret = "YOUR_CLIENT_SECRET" 
  user_agent = "dashboard_app by /u/YOUR_USERNAME" 
  ``` </pre>


3. Install requirements:
pip install -r requirements.txt


4. Run locally:

streamlit run reddit_dashboard_worldwide.py


5. Deploy on [Streamlit Cloud](https://streamlit.io/cloud) and it will automatically use the secrets.

## Notes

- The dashboard caches results for 5 minutes to reduce API calls.
- Make sure your Reddit credentials are correct to avoid 403 errors.
- Works both locally and on Streamlit Cloud.
