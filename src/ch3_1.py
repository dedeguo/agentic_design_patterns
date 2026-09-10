import os
import asyncio
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable, RunnableParallel, RunnablePassthrough


# Load environment variables from a .env file.
from dotenv import load_dotenv
import os

load_dotenv()

# Make sure your OPENAI_API_KEY is set in the .env file.

# --- Configuration ---
# Ensure your API key environment variable is set, e.g., OPENAI_API_KEY
try:
    # Initialize the Language Model.

    llm = ChatOpenAI(
    model_name=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    temperature=0)
except Exception as e:
    print(f"Error initializing language model: {e}")
    llm = None


# --- Define Independent Chains ---
# These chains represent distinct tasks that can be executed in parallel.

summarize_chain: Runnable = (
    ChatPromptTemplate.from_messages([
        ("system", "用一两句话概括这道菜/这家店的主要特点，回答要简洁。"),
        ("user", "{topic}")
    ])
    | llm
    | StrOutputParser()
)

questions_chain: Runnable = (
    ChatPromptTemplate.from_messages([
        ("system", "如果你是第一次想尝试它的食客，请提出 3 个最想知道的、接地气的问题。"),
        ("user", "{topic}")
    ])
    | llm
    | StrOutputParser()
)

terms_chain: Runnable = (
    ChatPromptTemplate.from_messages([
        ("system", "请提取 5-10 个与它相关的关键词，用顿号分隔。"),
        ("user", "{topic}")
    ])
    | llm
    | StrOutputParser()
)


# --- Build the Parallel + Synthesis Chain ---
# 1. Define the block of tasks to run in parallel.
map_chain = RunnableParallel(
    {
        "summary": summarize_chain,
        "questions": questions_chain,
        "key_terms": terms_chain,
        "topic": RunnablePassthrough()  # Pass the original topic through
    }
)

# 2. Define the final synthesis prompt which will combine the parallel results.
synthesis_prompt = ChatPromptTemplate.from_messages([
    ("system", """请根据下面三方面的信息，综合成一段通俗易懂的介绍：

概括：{summary}
大家关心的问题：{questions}
相关关键词：{key_terms}
请综合成一份完整的介绍。"""),
    ("user", "话题：{topic}")
])

# 3. Construct the full chain by piping the parallel results into the synthesis prompt,
# followed by the LLM and output parser.
full_parallel_chain = map_chain | synthesis_prompt | llm | StrOutputParser()


# --- Run the Chain ---
async def run_parallel_example(topic: str) -> None:
    """
    Asynchronously invokes the parallel processing chain with a specific topic
    and prints the synthesized result.

    Args:
        topic: The input topic to be processed by the LangChain chains.
    """
    if not llm:
        print("LLM not initialized. Cannot run example.")
        return

    print(f"\n--- Running Parallel LangChain Example for Topic: '{topic}' ---")

    try:
        # The input to 'ainvoke' is the single 'topic' string,
        # then passed to each runnable in the 'map_chain'.
        response = await full_parallel_chain.ainvoke(topic)
        print("\n--- Final Response ---")
        print(response)
    except Exception as e:
        print(f"\nAn error occurred during chain execution: {e}")


if __name__ == "__main__":
    test_topic = "红烧肉"
    # In Python 3.7+, asyncio.run is the standard way to run an async function.
    asyncio.run(run_parallel_example(test_topic))