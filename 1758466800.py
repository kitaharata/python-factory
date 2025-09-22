import base64
import json
import mimetypes
import os

from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def get_image_data_and_mime_type(image_path):
    if not os.path.exists(image_path):
        return None, None
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
        encoded_image_data = base64.b64encode(image_data).decode("utf-8")
        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type is None:
            mime_type = "image/png"
            ext = os.path.splitext(image_path)[1].lower()
            if ext in (".jpg", ".jpeg"):
                mime_type = "image/jpeg"
            elif ext == ".gif":
                mime_type = "image/gif"
            elif ext == ".webp":
                mime_type = "image/webp"
            elif ext == ".avif":
                mime_type = "image/avif"
        return encoded_image_data, mime_type
    except Exception:
        return None, None


user_question = input("Question: ")
user_image_path = input("Image file path: ")

human_message_content = [{"type": "text", "text": "{question}"}]
if user_image_path:
    image_data, mime_type = get_image_data_and_mime_type(user_image_path)
    if image_data:
        human_message_content.append(
            {
                "type": "image",
                "source_type": "base64",
                "data": image_data,
                "mime_type": mime_type,
            }
        )
parser = JsonOutputParser()
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant.\n{format_instructions}"),
        ("human", human_message_content),
    ]
).partial(format_instructions=parser.get_format_instructions())
model = ChatGoogleGenerativeAI(api_key=os.getenv("GEMINI_API_KEY"), model="gemini-2.5-flash")
chain = prompt | model | parser
output = chain.invoke({"question": user_question})

print(json.dumps(output, indent=2))
