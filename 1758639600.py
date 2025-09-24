import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

user_question = input("Question: ")
user_binary_path = input("Binary file path: ")

extracted_text = ""
if user_binary_path:
    try:
        with open(user_binary_path, "rb") as f:
            data = f.read()
        extracted_text = "".join(chr(b) for b in data if 32 <= b <= 126)
    except Exception as e:
        print(f"Error reading file: {e}")

full_question = user_question
if extracted_text:
    full_question += f"\n\nExtracted printable ASCII from binary file: {extracted_text}"

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("human", "{question}"),
    ]
)
model = ChatGoogleGenerativeAI(api_key=os.getenv("GEMINI_API_KEY"), model="gemini-2.5-flash")
output_parser = StrOutputParser()
chain = prompt | model | output_parser
output = chain.invoke({"question": full_question})

print(output)
