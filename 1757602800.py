import os

import requests
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


@tool
def github_repo_info(owner: str, repo: str) -> dict:
    """Retrieves information about a GitHub repository."""
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        response = requests.get(repo_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred during the GitHub API request: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred while processing repository information: {e}"}


@tool
def request_url(url: str) -> dict:
    """Performs HTTP GET to URL, restricted to 'https://api.github.com'."""
    if not url.startswith("https://api.github.com"):
        return {"error": "Unauthorized origin. The URL must start with 'https://api.github.com'."}
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred during the request to the URL: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred while processing the URL: {e}"}


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("human", "{question}"),
    ]
)
model = ChatGoogleGenerativeAI(api_key=os.getenv("GEMINI_API_KEY"), model="gemini-2.5-flash")
llm_with_tools = model.bind_tools([github_repo_info, request_url])
chain = prompt | llm_with_tools
original_question_text = input("Question: ")
response = chain.invoke({"question": original_question_text})

if response.tool_calls:
    print("Tool calls detected:")
    for tool_call in response.tool_calls:
        print(f"  Tool Name: {tool_call['name']}")
        print(f"  Args: {tool_call['args']}")
        if tool_call["name"] == "github_repo_info":
            owner = tool_call["args"].get("owner")
            repo = tool_call["args"].get("repo")
            if owner and repo:
                tool_output = github_repo_info.invoke({"owner": owner, "repo": repo})
            else:
                print("  Missing owner or repo for github_repo_info.")
                tool_output = {"error": "Missing owner or repo for github_repo_info."}
        elif tool_call["name"] == "request_url":
            url = tool_call["args"].get("url")
            if url:
                tool_output = request_url.invoke({"url": url})
            else:
                print("  Missing url for request_url.")
                tool_output = {"error": "Missing url for request_url."}
        else:
            print(f"  Unknown tool: {tool_call['name']}")
            tool_output = {"error": f"Unknown tool: {tool_call['name']}"}
        if tool_output:
            follow_up_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "human",
                        "Original question: {original_question_text}"
                        "Result of tool '{tool_name}' execution: {tool_output}"
                        "Based on this information, please answer the original question.",
                    )
                ]
            )
            follow_up_chain = follow_up_prompt | model
            final_ai_response = follow_up_chain.invoke(
                {
                    "original_question_text": original_question_text,
                    "tool_name": tool_call["name"],
                    "tool_output": tool_output,
                }
            )
            print(f"  AI's Final Answer: {final_ai_response.content}")
        else:
            print(f"  Tool execution resulted in an error: {tool_output}")
else:
    output_parser = StrOutputParser()
    print("No tool calls. LLM response:")
    print(output_parser.invoke(response.content))
