#sec fillings analyzer

#this project helps any analyst process long fillings, extract relevant data, use it in his day to day work

#the program allows you to pick a ticker,report(10k, 10Q), year,financial statement-->process your request & return needed data in re-usable formats


#requirements & prefrences:
pip install pandas
pip install datetime
pip install numpy
pip install unstructured
pip install llamaindex
pip install chunker
pip install streamlit
pip install xlsxwriter
pip install io
api key ((https://financialmodelingprep.com/))
python 3.13.3

#workflow:
user input-->download filing as json/html-->chunk-->parse-->rag(retrieval augmented generation)-->ranker(filter)-->llm structuring & query-->output.

