import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        (
            "human",
            [
                {"type": "text", "text": "{question}"},
                {"type": "image_url", "image_url": {"url": "{image_url}"}},
            ],
        ),
    ]
)
model = ChatGoogleGenerativeAI(api_key=os.getenv("GEMINI_API_KEY"), model="gemini-2.5-flash")
output_parser = StrOutputParser()
chain = prompt | model | output_parser

user_question = input("Question: ")
user_image_url = input("Image URL (optional): ")
invoke_params = {"question": user_question, "image_url": ""}
if user_image_url:
    invoke_params["image_url"] = user_image_url
output = chain.invoke(invoke_params)

print(output)
