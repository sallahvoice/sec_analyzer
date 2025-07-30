import os
from dotenv import load_dotenv
from pathlib import Path
import requests
import pandas as pd

env_path = Path(__file__).resolve().parent.parent/".env"
load_dotenv(dotenv_path=env_path)
api = os.getenv("API_KEY")


class Financial_fetch:
    
    def __init__(self,base_url,ticker):
        self.base_url = base_url
        self.ticker = ticker
        self.selected_financial_data = ""


    def fetch_data(self, selected_financial_data):
        url = f"{self.base_url}/{selected_financial_data}/{self.ticker}?apikey={api}"
        response = requests.get(url)
        if response.status_code !=200:
            return None
        else:
            try:    
                data = response.json()
                if isinstance(data,dict):
                    df = pd.DataFrame([data])
                else:
                    df = pd.DataFrame(data)
            except Exception:
                return None
            return df
        
    def save_data(self,df,filename):
        print("=== SAVE_DATA DEBUG ===")
        print(f"DataFrame shape: {df.shape}")  
        print(f"DataFrame empty: {df.empty}")
        print(f"Ticker: {self.ticker}")
        print(f"Filename: {filename}")
        
        file_path = Path(__file__).resolve().parent.parent/f"./data/{self.ticker}_{filename}.csv"
        print(f"Saving to: {file_path}")
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if os.path.exists(file_path):
            print("File exists - appending")
            df.to_csv(file_path,mode="a", header=False, index=False)
        else:
            print("Creating new file")
            df.to_csv(file_path, index=False)
        
        print("=== SAVE COMPLETE ===")

    def to_millions(self, df):
        df_millions = df.copy()
        numeric_col_names = df_millions.select_dtypes(include="number").columns
        for col in numeric_col_names:
            mask = df_millions[col].abs() >= 1000000
            df_millions.loc[mask, col] = df_millions.loc[mask, col]/1000000
        return df_millions    

    

    # url for 10k, limitations on free plan
    #"https://financialmodelingprep.com/stable/financial-reports-json?symbol=AAPL&year=2022&period=FY&apikey=ja4fWEYpqhiO92mY7ebM9lxF0XCQwYDL"
    #redis cach
                
                

                
                    
    
                




    

 
