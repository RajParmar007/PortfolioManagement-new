from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import os 

# Load environment variables from a .env file
load_dotenv()

# Initialize the Google Generative AI model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

