import yaml
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import TextMessage, BaseAgentEvent, BaseChatMessage
from autogen_core import CancellationToken
from autogen_core.models import ChatCompletionClient
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools, SseServerParams, SseMcpToolAdapter
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
        prompt = "You are a helpful AI assistant. Solve tasks using the provided tools. Answer everything in whatever language the user is using. " \
        "When generating your response, do not mention in any way that you are using external tools to solve the provided task." \
        "When using tools, make sure you generate the correct json for the tool you are trying to call. In particular, do not add invalid \\\\ escape" \
        "When you are not sure about what tool to use, ask the user for more specific requirement. Do not generate a tool call unless you are sure about what the user actually wants. " \
        "For tools that requires temp file directory as an argument, pass the following directory: {tempDir}; " \
        "for tools that requires uploaded file directory as an argument, pass the temp file directory; " \
        "for tools that processes data and returns a path to a result file, the front end will attempt to plot the result in a chart. Form your response in a way that implys the result will be shown below, and DO NOT EVER include path to result file.".format(tempDir = tempFileDir)
        self.agent = AssistantAgent(
            name="assistant",
            model_client=model_client,
            model_client_stream=True,
            system_message=prompt,
            tools=tools,
            reflect_on_tool_use=True,
        )
    def chat(self, prompt: str) -> AsyncGenerator[BaseAgentEvent | BaseChatMessage | Response, None]:
        # return self.agent.run_stream(
        #     [TextMessage(content=prompt, source="user")],
        #     CancellationToken(),
        # )
        return self.agent.run_stream(task=prompt)
        # print(response.chat_message)
        # return response.chat_message.content
        
            
