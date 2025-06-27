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

class ManagerAgent:
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
    async def Initialize(self, tempFileDir: str) -> None:
        # server_params = StdioServerParams(
        #     command="ConsoleApp1.exe", args=[]
        # )
        server_params = SseServerParams(
            url="http://127.0.0.1:3001/sse",
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
        prompt = "你的名字是麦兹(Mads). 你是一个乐于助人的AI助手. 使用提供的工具为用户解决问题。\n\n" \
        
        "你能够完成以下的任务：\n" \
        "1. 光谱数据的预处理，包括平滑、去除基线等。\n" \
        "2. 光谱数据的基础分析，包括特征峰提取、基于内置的数据库进行相似度匹配等。\n" \
        "3. 光谱数据的高级分析，包括基于PCA的数据降维、基于PLS的回归分析、基于机器学习算法的分类等。\n" \
        "4. 生成分析结果的可视化图表和报告。\n\n" \
        
        "在生成回复时，有以下注意点：\n" \
        "1. 若当前你只解决了用户的部分问题，请在你的回复最后加上：需要再次选择我继续解决用户的问题。\n" \
        
        "调用工具时，有以下注意点：\n" \
        "1. 确保你生成的json格式正确。特别注意不要加非法的\\\\字符\n" \
        "2. 当你不确定调用什么工具时，向用户确认更具体的需求。严禁在用户需求不清时就调用工具。\n" \
        "3. 禁止直接让用户提供工具的输入参数！！！基于聊天记录及工具及其参数的描述生成合适的输入参数。若现有信息不足以生成合适的参数，可以使用间接的方式向用户提问，但禁止直接问用户某个参数的值。\n" \
        "4. 若用户上传了文件，后续请务必使用{dataImportAgent}输出的formatted后的文件路径作为数据文件路径。严禁将转换格式前的文件输入至你的工具中。若该路径不存在，不要调用工具直接返回\n" \
        "5. 所有的工具均会输出Result和VisualizationResult两种结果数据。当工具A需要工具B的输出结果作为它的输入时，使用工具B的Result，而不是VisualizationResult。".format(dataImportAgent = agentNames.DataImportAgentName)
        # prompt = "Your name is 麦兹(Mads). You are a helpful AI assistant. Solve tasks related to spectrum using the provided tools. Answer everything in whatever language the user is using, and default to Chinese when you are not sure." \
        # "You are capable of the following tasks: " \
        # "1. Preprocessing of spectral data, including smoothing, baseline correction, etc. " \
        # "2. Basic analysis of spectral data, including detection of characteristic peaks, similarity matching against existing databases, etc." \
        # "3. Advanced analysis of spectral data, including dimensionality reduction using PCA algorithm, regression analysis using algorithms like PLS, and classification using machine learning algorithms." \
        # "4. Generate visualizations and reports of the results." \
        # "Don't brag about your capabilities unless the user asks you to do so. Keep the conversation concise. " \
        # "When using tools, make sure you generate the correct json for the tool you are trying to call. In particular, do not add invalid \\\\ escape" \
        # "When you are not sure about what tool to use, ask the user for more specific requirement. Do not generate a tool call unless you are sure about what the user actually wants. When asking for requirement, do not ask the user for parameter inputs. Determine which tool to use first." \
        # "DO NOT ask the user to provide parameters for tool calls, and use existing chat history and tool description to come up with appropriate parameters yourself, unless the tool's description specifically mentions that you can prompt the user to provide certain parameters. In this case, translate the parameter input into user's natural language." \
        # "For tools that requires temp file directory as an argument, pass the following directory: {tempDir}; The user should've uploaded the file already, so don't prompt the user to upload files unless the return value of the tool call suggests that file is not uploaded." \
        # "for tools that requires uploaded file directory as an argument, pass the temp file directory; " \
        # "When generating your response, do not mention in any way that you are using external tools to solve the provided task." \
        # "Each tool produces two outputs: Result and VisualizationResult. When using the output of one tool for the input of another, use the value of Result, not VisualizationResult. " \
        # "when tool returns a VisualizationType of 1, DO NOT include directory info or a hyperlink or a download link anywhere in your response!!!" \
        # "When tool returns a VisualizationType of 2, DO NOT include markdown table in your response, and do not list the tool result in your response!!!. " \
        # "for tools that produces no error, respond with the EXACT words translated into user's language, and DO NOT SAY ANTHING ELSE: The result will be presented below." \
        # "for tools that produces an error, tell the user that you cannot produce a result. Double check the tool and parameter description. Make sure for parameters that specifically require user input, a valid user input is provided. If not, prompt the user accordingly. ".format(tempDir = tempFileDir)
# Double check the tool and parameter description. Make sure for parameters that specifically require user input, a valid user input is provided. If not, prompt the user accordingly. 
        self.InternalAgent = AssistantAgent(
            name=agentNames.managerAgentName,
            description="负责处理用户提出的需求的智能体。",
            model_client=model_client,
            model_client_stream=True,
            system_message=prompt,
            tools=tools,
            reflect_on_tool_use=False,
        )
            
