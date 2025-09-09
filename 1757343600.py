import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

user_question = input("Question: ")
user_image_url = input("Image URL: ")

human_message_content = [{"type": "text", "text": "{question}"}]
if user_image_url:
    human_message_content.append(
        {
            "type": "image",
            "source_type": "url",
            "url": user_image_url,
        }
    )
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("human", human_message_content),
    ]
)
model = ChatGoogleGenerativeAI(api_key=os.getenv("GEMINI_API_KEY"), model="gemini-2.5-flash")
output_parser = StrOutputParser()
chain = prompt | model | output_parser
output = chain.invoke({"question": user_question})

print(output)
