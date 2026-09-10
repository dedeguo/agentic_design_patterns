import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# --- 配置 ---
# 从 .env 文件加载环境变量（用于 OPENAI_API_KEY）
load_dotenv()

# 检查 API Key 是否已设置
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError(
        "在 .env 文件中未找到 OPENAI_API_KEY，请添加该配置。"
    )

# 初始化 Chat LLM。这里使用 gpt-4o 以获得更好的推理能力。
# 使用较低的温度以获得更确定的输出。
llm = ChatOpenAI(
    model_name=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    temperature=0)


def run_reflection_loop():
    """
    演示多轮 AI 反思循环，逐步改进一个 Python 函数。
    """
    # --- 核心任务 ---
    task_prompt = """
你的任务是编写一个名为 `calculate_factorial` 的 Python 函数。
该函数需要做到以下几点：
1. 接收一个整数 `n` 作为输入。
2. 计算它的阶乘（n!）。
3. 包含清晰的 docstring，说明该函数的作用。
4. 处理边界情况：0 的阶乘是 1。
5. 处理无效输入：如果输入是负数，则抛出 ValueError。
"""

    # --- 反思循环 ---
    max_iterations = 3
    current_code = ""

    # 我们会构建一个对话历史，以便在每一步提供上下文。
    message_history = [HumanMessage(content=task_prompt)]

    for i in range(max_iterations):
        print(
            "\n"
            + "=" * 25
            + f" 反思循环：第 {i + 1} 轮 "
            + "=" * 25
        )

        # --- 1. 生成 / 优化阶段 ---
        # 第一轮进行生成，后续轮次进行优化。
        if i == 0:
            print("\n>>> 阶段 1：正在生成初始代码...")
            # 第一条消息只是任务提示词。
            response = llm.invoke(message_history)
            current_code = response.content
        else:
            print("\n>>> 阶段 1：根据上轮批评意见优化代码...")
            # 此时对话历史中已包含任务提示词、上一版代码以及上一轮批评意见。
            # 我们指示模型根据这些批评意见进行优化。
            message_history.append(
                HumanMessage(
                    content="请根据上面提供的批评意见对代码进行优化。"
                )
            )
            response = llm.invoke(message_history)
            current_code = response.content

        print("\n--- 生成的代码（第 " + str(i + 1) + " 版）---\n" + current_code)
        message_history.append(response)

        # --- 2. 反思阶段 ---
        print("\n>>> 阶段 2：正在对生成的代码进行反思...")

        # 为反思者（评审 Agent）创建一个专门的提示词。
        # 这里让模型扮演一名资深代码评审专家。
        reflector_prompt = [
            SystemMessage(
                content="""
你是一名资深软件工程师，同时也是 Python 专家。
你的职责是进行严谨细致的代码评审。
请对照原始任务要求，严格评估所提供的 Python 代码。
重点关注：Bug、风格问题、遗漏的边界情况以及可改进之处。
如果代码已经完美并满足所有要求，
请只回复短语 'CODE_IS_PERFECT'。
否则，请以项目符号列表的形式列出你的批评意见。
"""
            ),
            HumanMessage(
                content=f"原始任务：\n{task_prompt}\n\n待评审的代码：\n{current_code}"
            ),
        ]

        critique_response = llm.invoke(reflector_prompt)
        critique = critique_response.content

        # --- 3. 停止条件 ---
        if "CODE_IS_PERFECT" in critique:
            print(
                "\n--- 评审意见 ---\n没有发现进一步的批评意见，代码已满足要求。"
            )
            break

        print("\n--- 评审意见 ---\n" + critique)

        # 将批评意见加入历史，供下一轮优化使用。
        message_history.append(
            HumanMessage(content=f"上一版代码的批评意见：\n{critique}")
        )

    print("\n" + "=" * 30 + " 最终结果 " + "=" * 30)
    print("\n反思过程结束后最终优化得到的代码：\n")
    print(current_code)


if __name__ == "__main__":
    run_reflection_loop()
