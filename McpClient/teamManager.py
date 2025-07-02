import yaml
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import TextMessage, BaseAgentEvent, BaseChatMessage
from autogen_core import CancellationToken
from autogen_core.models import ChatCompletionClient
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools, SseServerParams, SseMcpToolAdapter
from autogen_agentchat.teams import RoundRobinGroupChat, Swarm, SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination, TextMessageTermination
from typing import AsyncGenerator
import agentNames


class TeamManager:
    def Initialize(self, agents) -> None:
        with open("model_config.yml", "r") as f:
            model_config = yaml.safe_load(f)
        model_client = ChatCompletionClient.load_component(model_config)
        selector_prompt = """选择一个智能体执行任务.

        {roles}

        当前对话上下文:
        {history}

        基于上面的对话，从{participants}中选择一个智能体去执行下一步任务。若当前的任务不需要基于用户上传的文件进行（即使用户已经上传文件），直接调用manager。若当前的任务必须基于用户上传的数据进行，请确保先反复调用dataImporter，直到它输出一个格式转换后的文件路径后，再调用其他智能体。当你认为manager的回答已经满足了客户的需求，请调用summarizer总结！
        禁止一次选择多个智能体！
        若调用智能体5次后还没有结果，必须直接调用summarizer开始总结！！！必须直接调用summarizer开始总结！！！必须直接调用summarizer开始总结！！！
        """
        # self.agent = Swarm(
        #     agents,
        #     termination_condition = TextMessageTermination(agentNames.managerAgentName)
        # )
        self.agent = SelectorGroupChat(
            agents,
            model_client=model_client,
            termination_condition=TextMessageTermination(agentNames.outputAgentName),
            selector_prompt=selector_prompt,
            allow_repeated_speaker=True,  # Allow an agent to speak multiple turns in a row.
        )
    async def chat(self, prompt: str) -> AsyncGenerator[BaseAgentEvent | BaseChatMessage | Response, None]:
        async for message in self.agent.run_stream(task=prompt):
            yield message
        
            
