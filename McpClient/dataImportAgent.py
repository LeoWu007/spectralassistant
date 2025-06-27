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

class DataImportAgent:
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
        # server_params = StdioServerParams(
        #     command="ConsoleApp1.exe", args=[]
        # )
        server_params = SseServerParams(
            url="http://127.0.0.1:3002/sse",
            headers={},
            timeout=30,  # Connection timeout in seconds
        )
        # Get all available tools from the server
        tools = await mcp_server_tools(server_params)
        # tools = await SseMcpToolAdapter.from_server_params(server_params, "DoHelloWorldTest")
        # Load the model client from config.
        with open("model_config.yml", "r") as f:
            model_config = yaml.safe_load(f)
        model_client = ChatCompletionClient.load_component(model_config)
        prompt = "你是一位经验丰富的数据分析师，用户会提供一个包含光谱数据的文件，文件中除了光谱数据以外，可能包含元数据、空行/列、无意义行/列、标题行、列等非数据行/列。你的任务如下（按顺序执行）：\n" \
        "1. 分析读取到的内容，确认非数据行及非数据列的个数\n" \
        "2. 调用工具，转换该文件的格式\n" \
        "注意点：\n" \
        "1. 非数据行/列最明显的特征是包含无法转换为浮点数的内容。只要有非浮点数的内容，则一定是非数据行/列。但全部是浮点数也不一定不是非数据行/列，要注意甄别。\n" \
        "2. 非数据行/列的个数错误会直接导致工具调用失败，请确保其正确！\n" \
        "3. 若转换文件格式的工具调用失败时，表明你给出的非数据行及非数据列个数有误，应该重新确认数量后再次调用该工具。严禁将相同的参数输入进去重试！\n" \
        "4. 禁止输出任何文本信息，直接调用工具即可。后续参考示例中的文本信息仅为你思考的过程，并非要输出的内容\n" \

        "参考示例：\n" \
        "上传文件路径：D:\\data.csv\n" \
        "上传文件内容：\n" \
        "Name,Origin-NOVA2S001,Origin-NOVA2S001,Origin-NOVA2S001,Origin-NOVA2S001,Origin-NOVA2S001\n" \
        "SerialNumber,NOVA2S001,NOVA2S001,NOVA2S001,NOVA2S001,NOVA2S001\n" \
        "IntegrationTime,100,100,100,100,100\n" \
        "Boxer,0,0,0,0,0\n" \
        "Time,0,0.11,0.211,0.311,0.412\n" \
        ",,,,,\n" \
        ",,,,,\n" \
        "Wavelength [nm],Counts [a.u.],Counts [a.u.],Counts [a.u.],Counts [a.u.],Counts [a.u.]\n" \
        "180.759,77.875,9.875,-64.125,-77.125,88.875\n" \
        "181.578,22.375,13.375,-40.625,37.375,30.375\n" \
        "182.397,-27.125,-60.125,-21.125,67.875,-81.125\n" \
        "183.216,78.375,91.375,72.375,2.375,49.375\n" \
        "184.035,24.875,-54.125,-96.125,19.875,51.875\n" \
        "184.854,-39.625,-57.625,19.375,12.375,-87.625\n" \
        "185.672,-95.625,99.375,-45.625,44.375,-7.625\n\n" \

        "1. 分析：\n" \
        "该文件中包含5行元数据，2行空行，1行标题，共8个非数据行，没有发现非数据列\n\n" \
        
        "2. 调用转换格式工具，工具参数：\n" \
        "filePath: D:\\data.csv, rowsToSkip: 8, columnsToSkip: 0".format(managerAgentName = agentNames.managerAgentName)
        # Double check the tool and parameter description. Make sure for parameters that specifically require user input, a valid user input is provided. If not, prompt the user accordingly. 
        self.InternalAgent = AssistantAgent(
            name=agentNames.DataImportAgentName,
            description="负责解析用户上传数据的智能体。若当前的任务需要用到用户上传的数据时，第一步必须为该智能体",
            model_client=model_client,
            model_client_stream=True,
            system_message=prompt,
            tools=tools,
        )
        
            
