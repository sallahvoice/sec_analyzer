from redis_conn import redis_client
import streamlit as st
from financial_fetch import Financial_fetch
from llm import extract_info_gemini
from io import BytesIO
import pandas as pd
import pickle
import requests
import logging

logger = logging.getLogger(__name__)

def notify_cache_expiry(cache_key):
    try:
        resp = requests.post(
            "http://localhost:8000/expire_cache/",
            json={"cache_key": cache_key},
            timeout=1
        )
        if resp.status_code == 200:
            st.info(f"Webhook: {resp.json().get('message')}")
        else:
            st.warning("Webhook call failed.")
    except Exception as e:
        st.warning(f"Webhook error: {e}")

def are_dataframes_equal(df1, df2):
    try:
        return df1.equals(df2)
    except:
        return False

st.set_page_config(layout="wide")

def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Error: CSS file '{file_name}' not found. Make sure it's in the same directory.")

local_css("style.css")

st.title("financial data with ai")

base_url = "https://financialmodelingprep.com/api/v3"
financial_fetcher = Financial_fetch(base_url, "")

ticker = st.sidebar.text_input("enter a ticker", value="TSLA").upper()
financial_data_options = st.sidebar.selectbox("financial data type", options=(
    "income-statement", "balance-sheet-statement", "cash-flow-statement",
    "ratios-ttm", "ratios", "financial-growth", "enterprise-values",
    "key-metrics-ttm", "rating", "historical-rating",
    "discounted-cash-flow", "historical-discounted-cash-flow-statement"
))

user_prompt = st.sidebar.text_area("enter a question")

if st.button("fetch data"):
    with st.spinner("loading"):
        financial_fetcher.ticker = ticker
        cache_key = f"{ticker}_{financial_data_options}"
        df = None

        if redis_client:
            try:
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    # Load cached data
                    cached_df = pickle.loads(cached_data)
                    
                    # Fetch fresh data and transform it
                    api_df = financial_fetcher.fetch_data(financial_data_options)
                    transform_api_df = financial_fetcher.to_millions(api_df)
                    
                    # Compare dataframes to check if data changed
                    if not are_dataframes_equal(transform_api_df, cached_df):
                        # Data changed - expire cache and use fresh data
                        notify_cache_expiry(cache_key)
                        redis_client.set(cache_key, pickle.dumps(transform_api_df))
                        df = transform_api_df
                        st.info("API data updated, cache refreshed.")
                    else:
                        # Data unchanged - use cached data
                        df = cached_df
                        st.success("Loaded data from cache.")
                else:
                    # No cache - fetch, transform, and store
                    df = financial_fetcher.fetch_data(financial_data_options)
                    df = financial_fetcher.to_millions(df)
                    redis_client.set(cache_key, pickle.dumps(df))
                    st.success("Fresh data cached.")
                    
            except Exception as e:
                # Redis error - fetch without caching
                st.warning(f"Cache error: {e}")
                df = financial_fetcher.fetch_data(financial_data_options)
                df = financial_fetcher.to_millions(df)
        else:
            # No Redis - just fetch and transform
            df = financial_fetcher.fetch_data(financial_data_options)
            df = financial_fetcher.to_millions(df)

    # Excel download
    if df is not None:
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name=f"financials")
        excel_data = output.getvalue()
        st.download_button(
            label="download as excel",
            data=excel_data,
            file_name=f"{ticker}-{financial_data_options}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    # AI Analysis or Data Display
    if df is not None:
        if user_prompt:
            st.subheader("AI analysis")
            st.markdown("<div class='ai-analysis-container'>", unsafe_allow_html=True)
            try:
                result = extract_info_gemini(df, f"for {ticker},{user_prompt}")  
                st.dataframe(result)
            except Exception as e:
                st.error(f"error handling the prompt: {e}")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Display data
            if "date" in df.columns:
                transpose_df = df.set_index("date").T.reset_index()
                transpose_df = transpose_df.rename(columns={"index": "metric"})
                try:
                    # Convert all columns to string to avoid Arrow serialization issues
                    display_df = transpose_df.astype(str)
                    st.dataframe(display_df, hide_index=True)
                except:
                    st.dataframe("Transpose view formatting failed")
            else:
                try:
                    st.dataframe(df.astype(str))
                except Exception as e:
                    st.dataframe(f"data fetched but display failed {e}")
    else:
        st.error("Failed to fetch data")