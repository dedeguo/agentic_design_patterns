from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# langchain 目前不原生支持skill

load_dotenv()
model = ChatOpenAI(
   model_name=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    temperature=0.1,
    max_tokens=1000,
    timeout=30
    # ...（其他参数）
)

@tool
def load_skill(skill_name: str) -> str:
    """Load a specialized skill prompt.

    Available skills:
    - write_sql: SQL query writing expert
    - review_legal_doc: Legal document reviewer

    Returns the skill's prompt and context.
    """
    # Load skill content from file/database
    ...
    return f"Skill prompt for {skill_name}"
def get_weather(city: str) -> str:
    """获取指定城市的天气。"""
    return f"{city}总是阳光明媚！"
tools = [get_weather, load_skill]
agent = create_agent(model, tools=tools)
