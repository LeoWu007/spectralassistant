import yaml
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import TextMessage, BaseAgentEvent, BaseChatMessage
from autogen_core import CancellationToken
from autogen_core.models import ChatCompletionClient
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools, SseServerParams, SseMcpToolAdapter
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, TextMessageTermination
from typing import AsyncGenerator
import agentNames

class OutputAgent:
    # def __init__(self) -> None:
        # server_params = StdioServerParams(
        #     command="ConsoleApp1.exe", args=[]
        # )

        # # Get all available tools from the server
        # tools = await mcp_server_tools(server_params)
        # # Load the model client from config.
        # with open("model_config.yml", "r") as f:
        #     model_config = yaml.safe_load(f)
        # model_client = ChatCompletionClient.load_component(model_config)
        # self.agent = AssistantAgent(
        #     name="assistant",
        #     model_client=model_client,
        #     system_message="You are a helpful AI assistant.",
        # )
    async def Initialize(self) -> None:

        with open("model_config.yml", "r") as f:
            model_config = yaml.safe_load(f)
        model_client = ChatCompletionClient.load_component(model_config)
        prompt = "你是一位经验丰富的ai助手。你的任务是基于其他ai助手的输出，生成合适的回复发送给用户。\n\n" \
        "生成回复时，有以下注意点：\n" \
        "1. 使用用户的语言回答问题，当不确定语言时，默认使用中文。\n" \
        "2. 你的回答越短越好，不要列举你能够完成的任务，除非用户要求。\n" \
        "3. 回答问题时，禁止以任何形式提到之前的工作使用了外部工具和函数等。\n" \
        "4. 你的回答中禁止提到与dataImporter的工作相关的内容\n" \
        "5. 严禁在你的回答中包含任何路径、超链接、下载链接等内容！\n" \
        # "6. 若其他ai助手通过工具成功完成了用户给的任务，回答以下文字（翻译至用户的语言），严禁增删改任何内容：分析结果如下所示。\n" \
        "7. 若用户的任务不是通过工具完成的，润色一下manager agent的输出即可。"

        self.InternalAgent = AssistantAgent(
            name=agentNames.outputAgentName,
            description="负责润色其他agent的输出，并生成回复的智能体。",
            model_client=model_client,
            model_client_stream=True,
            system_message=prompt,
        )
            
