from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API"))
model = genai.GenerativeModel(model_name = "gemini-2.5-flash")

def extract_info_gemini(df, user_prompt):
    text_csv = df.to_csv(index=False)
    prompt = f"""i will provide you with financial data for a certain
    publicly traded company in a csv format.
csv: {text_csv}
now answer this:
{user_prompt}

only give the precise & relevant part."""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[gemini error] {e}"









#chat = model.start_chat(history=[])

#while True:
    #user_input = input(">")
    #if user_input == "exit":
        #break
#res = chat.send_message(user_input)  
#print(res.text)  
#config={
#"system_instruction":""
#"telperature":0.8}

