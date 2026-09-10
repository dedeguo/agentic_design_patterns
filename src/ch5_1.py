import os, getpass
import asyncio
import nest_asyncio
from typing import List
from dotenv import load_dotenv
import logging
from langchain_core.tools import tool as langchain_tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

load_dotenv()


try:
    # 需要具备函数/工具调用能力的模型。
    llm = ChatOpenAI(
    model_name=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    temperature=0)
    print(f" 语言模型初始化完成：{llm.model}")
except Exception as e:
    print(f" 初始化语言模型时出错：{e}")
    llm = None


# --- 定义一个工具 ---
@langchain_tool
def search_information(query: str) -> str:
    """
    提供关于某个主题的事实性信息。使用此工具
    可以查找类似“法国的首都是什么”或“伦敦的天气怎么样”等问题的答案。
    """

    print(
        f"\n--- 工具被调用：search_information，"
        f"查询：'{query}' ---"
    )

    # 用一个预定义结果的字典来模拟搜索工具。
    simulated_results = {
        "weather in london":
            "伦敦的天气目前多云，气温 15°C。",

        "capital of france":
            "法国的首都是巴黎。",

        "population of earth":
            "地球的估计人口约为 80 亿人。",

        "tallest mountain":
            "珠穆朗玛峰是海拔最高的山峰。",

        "default":
            f"关于 '{query}' 的模拟搜索结果："
            "未找到具体信息，不过这个话题看起来很有趣。"
    }

    result = simulated_results.get(
        query.lower(),
        simulated_results["default"]
    )

    print(f"--- 工具结果：{result} ---")
    return result


tools = [search_information]


# --- 创建工具调用型 Agent ---
if llm:

    # 创建 Agent，将 LLM、工具和系统提示词绑定在一起。
    # langchain 1.x 的 create_agent 会自动管理内部推理步骤（scratchpad）。
    agent = create_agent(
        llm,
        tools=tools,
        system_prompt="你是一个乐于助人的助手。",
    )

    async def run_agent_with_tool(query: str):
        """
        使用一个查询调用 Agent，并打印最终回复。
        """

        print(
            f"\n--- 正在使用查询：'{query}' 运行 Agent ---"
        )

        try:
            response = await agent.ainvoke(
                {"messages": [("user", query)]}
            )
        except Exception as e:
            print(
                f"\n Agent 执行过程中发生错误：{e}"
            )
            return

        print("\n--- Agent 最终回复 ---")
        print(response["messages"][-1].content)

    async def main():
        """并发运行所有 Agent 查询。"""
        tasks = [
            run_agent_with_tool(
                "法国的首都是什么？"
            ),

            run_agent_with_tool(
                "伦敦的天气怎么样？"
            ),

            run_agent_with_tool(
                "给我讲讲关于狗的事情。"
            )
            # 应触发工具的默认回复
        ]

        await asyncio.gather(*tasks)

    nest_asyncio.apply()
    asyncio.run(main())
