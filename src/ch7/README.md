# Python LangChain 智能体任务规划 Demo

这是一个适合课堂讲解的 Plan-and-Execute（规划并执行）示例。
输入一个目标，程序让模型生成计划，每次执行一个步骤，再由模型检查结果并更新剩余计划。
同一个模型承担规划器、执行器、检查器三个逻辑角色；不需要部署三个模型。

## 1. 示例任务

> 根据课程资料，为 Java Web 项目实训制定4周教学安排，计算总课时，列出每周任务、交付物和验收标准。

课程数据是内置教学演示数据。read_course_brief实际读取内置字典；calculate_hours实际运行Python计算。
示例不联网搜索、不操作学生数据，也不会真正开发或部署Java项目。

## 2. 准备与运行

要求 Python 3.10+，推荐3.11或3.12。

```bash
python -m venv .venv
```

Windows PowerShell激活：

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS激活：

```bash
source .venv/bin/activate
```

如果Windows禁止激活脚本，可以直接使用 `.\.venv\Scripts\python.exe` 替代后续命令中的 `python`。

```bash
python -m pip install -r requirements.txt
```

复制 `.env.example` 为 `.env`，填写实际模型配置。例如本地vLLM的兼容接口：

```dotenv
LLM_API_KEY=EMPTY
LLM_MODEL=服务端实际暴露的模型名称
LLM_BASE_URL=http://localhost:8000/v1
```

只有服务端不验证密钥时才用EMPTY；远程部署时将localhost换为实际服务器地址。
接入其他兼容服务时填写其真实密钥、模型名和API根地址。不要将.env提交到Git。
本Demo要求接口与模型支持tool calling，包括结构化输出所需的工具调用。
vLLM还需要对应模型的工具调用解析配置；仅兼容普通聊天接口不保证本Demo能运行。

```bash
python main.py
python main.py "根据课程资料，制定4周Java Web实训安排，每周提供可检查的验收标准" --max-steps 6
```

运行中打印初始计划、当前步骤、工具调用/结果、检查意见、更新后的计划和最终答案。
默认将结果与执行历史保存到当前目录的 `run-result.json`。
可用 `--output result.json` 指定输出文件（已有同名文件会覆盖）。

## 3. 代码阅读顺序

| 组件 | 作用 |
|---|---|
| Plan | Pydantic定义步骤列表，保证计划可被程序读取 |
| Review | 检查结果必须是continue或finish，并验证剩余步骤与答案 |
| read_course_brief | 为执行器提供可引用的课程事实 |
| calculate_hours | 为执行器提供真实的Python课时计算 |
| build_agents | 用create_agent创建三个逻辑角色 |
| run | 执行计划循环，记录历史并限制最大步数 |

核心逻辑等价于：

```python
plan = planner(目标)
for _ in range(最大步数):
    result = executor(plan[0], 历史)
    历史.append(result)
    review = reviewer(目标, 历史, plan[1:])
    if review.action == 'finish':
        return review.answer
    plan = review.steps
```

上面是便于讲解的伪代码，完整实现见main.py。

规划器只拆任务；执行器负责当前子任务并自行选择是否调用工具；检查器结合历史决定后续工作。
更新计划时可以补充遗漏步骤、调整顺序、删除不再必要的步骤。
例如发现最终方案没有验收标准，就补充“为每周交付物编写可检查的验收条件”。
这属于行为示意，并非固定输出；真实计划和工具调用会随模型变化。

## 4. 与普通聊天、ReAct的区别

普通聊天可以输出一份计划，但不会自动逐步执行它。
本例的外层循环显式维护任务清单和执行历史；内层create_agent会循环选择工具并处理工具结果。
因此它是“外层Plan-and-Execute + 内层工具调用Agent”。
程序没有输出模型内部思维链，只展示用户可审阅的任务计划、实际调用、结果与简短检查意见。

## 5. 边界与扩展

- 当前是串行任务规划，不是并行DAG调度，也没有跨进程恢复。
- max_steps限制外层步骤数，recursion_limit限制单次Agent图调用；它们不是token预算。
- 每个请求有超时与重试，失败步骤进入历史供检查器处理；规划/检查失败则明确终止。
- 检查仍由模型完成，不是确定性正确性证明。生产环境可增加规则校验或人工验收。
- 达到步数上限返回max_steps_reached，退出码为2，不伪装成功。
- 历史每次传给模型，长任务会增加上下文与费用；生产环境需摘要或裁剪。
- 替换read_course_brief为课程文件/RAG检索工具，即可演示基于真实资料的规划。
- 增加LangGraph StateGraph与checkpointer，可进一步实现流程可视化、暂停恢复等。

## 6. 验证

```bash
python -m unittest -v test_flow.py
```

测试通过可控替身验证继续/重规划、执行异常、步数上限、结构化结果约束及真实课时工具。
替身测试不调用模型，不证明任何服务商的远程API兼容性。
交付时未进行真实模型端到端调用（未配置模型凭证）。
requirements.txt给出主版本兼容范围；requirements-tested.txt记录交付环境实际安装的核心包版本。

## 7. 官方参考

- https://docs.langchain.com/oss/python/langchain/agents
- https://docs.langchain.com/oss/python/langchain/structured-output
- https://docs.langchain.com/oss/python/integrations/chat/openai
