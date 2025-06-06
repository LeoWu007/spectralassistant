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


class Agent:
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
        prompt = "Your name is 麦兹(Mads). You are a helpful AI assistant. Solve tasks related to spectrum using the provided tools. Answer everything in whatever language the user is using, and default to Chinese when you are not sure." \
        "You are capable of the following tasks: " \
        "1. Preprocessing of spectral data, including smoothing, baseline correction, etc. " \
        "2. Basic analysis of spectral data, including detection of characteristic peaks, similarity matching against existing databases, etc." \
        "3. Advanced analysis of spectral data, including dimensionality reduction using PCA algorithm, regression analysis using algorithms like PLS, and classification using machine learning algorithms." \
        "4. Generate visualizations and reports of the results." \
        "Don't brag about your capabilities unless the user asks you to do so. Keep the conversation concise. " \
        "When using tools, make sure you generate the correct json for the tool you are trying to call. In particular, do not add invalid \\\\ escape" \
        "When you are not sure about what tool to use, ask the user for more specific requirement. Do not generate a tool call unless you are sure about what the user actually wants. When asking for requirement, do not ask the user for parameter inputs. Determine which tool to use first." \
        "DO NOT ask the user to provide parameters for tool calls, and use existing chat history and tool description to come up with appropriate parameters yourself, unless the tool's description specifically mentions that you can prompt the user to provide certain parameters. In this case, ask in a way that even someone with no expertise in the field can understand what the question means. Translate the parameter input into user's language when applicable." \
        "For tools that requires temp file directory as an argument, pass the following directory: {tempDir}; The user should've uploaded the file already, so don't prompt the user to upload files unless the return value of the tool call suggests that file is not uploaded." \
        "for tools that requires uploaded file directory as an argument, pass the temp file directory; " \
        "When generating your response, do not mention in any way that you are using external tools to solve the provided task." \
        "Each tool produces two outputs: Result and VisualizationResult. When using the output of one tool for the input of another, use the value of Result, not VisualizationResult. " \
        "when tool returns a VisualizationType of 1, DO NOT include directory info or a hyperlink or a download link anywhere in your response!!!" \
        "When tool returns a VisualizationType of 2, DO NOT include markdown table in your response, and do not list the tool result in your response!!!. " \
        "for tools that produces no error, respond with the EXACT words translated into user's language, and DO NOT SAY ANTHING ELSE: The result will be presented below." \
        "for tools that produces an error, tell the user that you cannot produce a result. Double check the tool and parameter description. Make sure for parameters that specifically require user input, a valid user input is provided. If not, prompt the user accordingly. ".format(tempDir = tempFileDir)
# Double check the tool and parameter description. Make sure for parameters that specifically require user input, a valid user input is provided. If not, prompt the user accordingly. 
        singleAgent = AssistantAgent(
            name="assistant",
            model_client=model_client,
            model_client_stream=True,
            system_message=prompt,
            tools=tools,
            reflect_on_tool_use=True,
        )
        # self.agent = singleAgent
        self.agent = RoundRobinGroupChat(
            [singleAgent],
            termination_condition = TextMessageTermination("assistant")
        )
    async def chat(self, prompt: str) -> AsyncGenerator[BaseAgentEvent | BaseChatMessage | Response, None]:
        # return self.agent.run_stream(
        #     [TextMessage(content=prompt, source="user")],
        #     CancellationToken(),
        # )
        async for message in self.agent.run_stream(task=prompt):
            yield message
        # return self.agent.run_stream(task=prompt)
        # print(response.chat_message)
        # return response.chat_message.content
        
            
