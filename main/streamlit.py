import streamlit as st
from main import Financial_fetch
from llm import extract_info_gemini
from io import BytesIO
import pandas as pd

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
financial_fetcher = Financial_fetch(base_url,"")

ticker = st.sidebar.text_input("enter a ticker", value="TSLA").upper()
financial_data_options= st.sidebar.selectbox("financial data type",options=("income-statement", "balance-sheet-statement", "cash-flow-statement",
                                                                     "ratios-ttm", "ratios", "financial-growth", "enterprise-values",
                                                                     "key-metrics-ttm", "rating", "historical-rating",
                                                                     "discounted-cash-flow", "historical-discounted-cash-flow-statement"
                                                                     ))
financial_fetcher.selected_financial_data = financial_data_options
user_prompt = st.sidebar.text_area("enter a question")

if st.button("fetch data"):
    with st.spinner("loading"):
        financial_fetcher.ticker = ticker
        df = financial_fetcher.fetch_data(financial_data_options)
        if df is not None:
            df = financial_fetcher.to_millions(df)
            st.markdown("<div class='format'>Large figures are displayed in millions of $</div>", unsafe_allow_html=True)

            financial_fetcher.save_data(df,financial_data_options)

            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="financials")
            excel_data = output.getvalue()
            st.download_button(
                label ="download as excel",
                data=excel_data,
                file_name=f"{ticker}-{financial_data_options}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            if user_prompt:
                st.subheader("AI analysis")
                st.markdown("<div class='ai-analysis-container'>", unsafe_allow_html=True)
                try:
                    result = extract_info_gemini(df,f"for {ticker},{user_prompt}")  
                    st.dataframe(result)
                except Exception as e:
                    st.error(f"error handling the prompt: {e}")
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                # Convert to string to fix display issues            
                if "date" in df.columns:
                    transpose_df = df.set_index("date").T.reset_index()
                    transpose_df = transpose_df.rename(columns={"index":"metric"})
                    try:
                        st.dataframe(transpose_df.astype(str), hide_index=True)
                    except:
                        st.dataframe("Transpose view formatting failed")
                else:
                    try:
                        st.dataframe(df.astype(str))
                    except Exception as e:
                        st.dataframe(f"data fetched but display failed {e}")            
        



                        


