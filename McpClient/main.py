import asyncio
import tempfile
import pathlib
import re
import pandas
from pandas import DataFrame
from pathlib import Path
import streamlit as st
from agent import Agent
from autogen_agentchat.messages import ThoughtEvent, ModelClientStreamingChunkEvent, ToolCallExecutionEvent
from autogen_agentchat.base import TaskResult
from autogen_core.models import FunctionExecutionResult

def GetPathOfResultDataFile(result: TaskResult) -> str:
    for message in result.messages:
        if isinstance(message, ToolCallExecutionEvent) is False:
            continue
        if isinstance(message.content[-1], FunctionExecutionResult) is False:
            continue
        print("parsing result")
        execRes = message.content[-1].content
        resContent = re.search(r'\(.*\)', execRes)
        res = re.findall(r'(\w*)=([^\,]+)', resContent.group(0).strip("()"))
        propertyDict = {}
        for property in res:
            propertyDict[property[0]] = property[1]
        return propertyDict.get("text", "").strip("\'")
    return ""

def PlotData(dataPath: str) -> DataFrame:
    data = pandas.read_csv(dataPath)
    PlotDataframe(data)
    return data

def PlotDataframe(dataframe: DataFrame) : 
    columnNames = dataframe.columns.tolist()
    chart = st.line_chart(dataframe, x=columnNames[0], y_label="Y")
    return chart

async def main() -> None:
    st.set_page_config(page_title="AI Chat Assistant", page_icon="🤖")
    st.title("AI Chat Assistant 🤖")
    if "tempFileDir" not in st.session_state:
        st.session_state["tempFileDir"] = tempfile.TemporaryDirectory()
    st.write(st.session_state.tempFileDir)
    with st.sidebar:
        uploadedFile = st.file_uploader("Upload any attachment here")
        filePath = pathlib.Path(st.session_state.tempFileDir.name)/"data.csv"
        print(uploadedFile)
        if uploadedFile is not None:
            print("writing file")
            f = open(filePath, 'wb')
            f.write(uploadedFile.read())
            f.close()
    # adding agent object to session state to persist across sessions
    # stramlit reruns the script on every user interaction
    if "agent" not in st.session_state:
        curAgent = Agent()
        await curAgent.Initialize(st.session_state.tempFileDir.name)
        st.session_state["agent"] = curAgent
    # initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # displying chat history messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "LineChart" in message and message["LineChart"] is not None:
                PlotDataframe(message["LineChart"])
    
    if prompt := st.chat_input("Type a message..."):
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            container = st.empty()
            responseStream = st.session_state["agent"].chat(prompt)
            print("got response stream")
            streamedText = ""
            chartDisp = None
            async for chunk in responseStream:
                print(chunk)
                if isinstance(chunk, ThoughtEvent):
                    streamedText = streamedText + "\n\n"
                    container.markdown(streamedText) 
                elif isinstance(chunk, ModelClientStreamingChunkEvent):
                    streamedText += chunk.content
                    container.markdown(streamedText) 
                elif isinstance(chunk, TaskResult):
                    print("received taskresult")
                    dataResultPath = GetPathOfResultDataFile(chunk)
                    if len(dataResultPath) != 0:
                        chartDisp = PlotData(dataResultPath)

            st.session_state.messages.append({"role": "assistant", "content": streamedText, "LineChart": chartDisp})
    # st.file_uploader("Upload any attachment here")


if __name__ == "__main__":
    # asyncio.run(main())
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
