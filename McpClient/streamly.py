import streamlit as st
import logging
from PIL import Image, ImageEnhance
import time
import json
import requests
import base64

import asyncio
import tempfile
import pathlib
import os.path
import re
import pandas
from pandas import DataFrame
from pathlib import Path
from agent import Agent
from autogen_agentchat.messages import ThoughtEvent, ModelClientStreamingChunkEvent, ToolCallExecutionEvent
from autogen_agentchat.base import TaskResult
from autogen_core.models import FunctionExecutionResult
from streamlit_extras.bottom_container import bottom
from audiorecorder import audiorecorder
from socket import *
import pickle
import json

CHAT_HISTORY_KEY = "messages"
CHAT_HISTORY_ROLE_KEY = "role"
CHAT_HISTORY_TEXT_KEY = "content"
CHAT_HISTORY_VISUALIZATION_TYPE_KEY = "VisualizationType"
CHAT_HISTORY_VISUALIZATION_KEY = "Visualization"
AGENT_KEY = "agent"
STT_SOCKET_KEY = "sttSocket"
TEMP_FILE_DIR_KEY = "tempFileDir"
EVENT_LOOP_KEY = "asyncEventLoop"
USER_AVATAR_IMG = "imgs/stuser.png"
ASSISTANT_AVATAR_IMG = "imgs/avatar_streamly.png"

# Configure logging
logging.basicConfig(level=logging.INFO)

# Constants
NUMBER_OF_MESSAGES_TO_DISPLAY = 20
API_DOCS_URL = "https://docs.streamlit.io/library/api-reference"

# Streamlit Page Configuration
st.set_page_config(
    page_title="MADS - A Spectral AI Assistant",
    page_icon="imgs/avatar_streamly.png",
    # layout="wide",
    initial_sidebar_state="auto",
)

# Streamlit Title
st.title("The First Spectral AI Assistant")
# Version
st.markdown('<small> v0.7 Beta </small>', unsafe_allow_html=True)

def ProcessTaskResult(streamedText: str, result: TaskResult) -> str:
    visualizationType = None
    visualizationData = None
    for message in result.messages:
        if isinstance(message, ToolCallExecutionEvent) is False:
            continue
        if isinstance(message.content[-1], FunctionExecutionResult) is False:
            continue
        print("parsing result")
        execRes = message.content[-1].content

        resJsonStr = re.findall(r'"text": "(.*)",', execRes)
        if len(resJsonStr) == 0:
            continue
        resFormatted = resJsonStr[0].replace(r"\\", "\\").replace(r"\"", "\"")
        print(resJsonStr)
        resJson = json.loads(resFormatted)
        if resJson['IsError'] is True:
            print("Tool returned error, abort")
            continue
        visualizationType = resJson['VisualizationType']
        match resJson['VisualizationType']:
            case 0:
                continue
            case 1:
                if os.path.isfile(resJson['VisualizationResult']):
                    print("plotting data")
                    visualizationData = PlotData(resJson['VisualizationResult'])
            case 2:
                config = {
                    "Images": st.column_config.ImageColumn(),
                    "TrustScores": st.column_config.ProgressColumn(),
                }
                visualizationData = pandas.read_json(json.dumps(resJson['VisualizationResult']))
                print(visualizationData)
                st.dataframe(visualizationData, column_config=config)
    st.session_state.messages.append({CHAT_HISTORY_ROLE_KEY: "assistant", CHAT_HISTORY_TEXT_KEY: streamedText, CHAT_HISTORY_VISUALIZATION_TYPE_KEY: visualizationType, CHAT_HISTORY_VISUALIZATION_KEY: visualizationData})
    return ""

def PlotData(dataPath: str) -> DataFrame:
    data = pandas.read_csv(dataPath)
    PlotDataframe(data)
    return data

def PlotDataframe(dataframe: DataFrame) : 
    columnNames = dataframe.columns.tolist()
    chart = st.line_chart(dataframe, x=columnNames[0], y_label="Y")
    return chart

async def HandleUserInput(prompt: str) : 
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar = USER_AVATAR_IMG):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar = ASSISTANT_AVATAR_IMG):
        container = st.empty()
        responseStream = st.session_state["agent"].chat(prompt)
        print("got response stream")
        streamedText = ""
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
                ProcessTaskResult(streamedText, chunk)    

def img_to_base64(image_path):
    """Convert image to base64."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        logging.error(f"Error converting image to base64: {str(e)}")
        return None


def initialize_conversation() -> None:
    """
    Initialize the conversation history with system and assistant messages.

    Returns:
    - list: Initialized conversation history.
    """
        # Display chat history
    # for message in st.session_state.history[-NUMBER_OF_MESSAGES_TO_DISPLAY:]:
    #     role = message["role"]
    #     avatar_image = "imgs/avatar_streamly.png" if role == "assistant" else "imgs/stuser.png" if role == "user" else None
    #     with st.chat_message(role, avatar=avatar_image):
    #         st.write(message["content"])
    if CHAT_HISTORY_KEY not in st.session_state:
        st.session_state[CHAT_HISTORY_KEY] = []
        initial_bot_message = "Sorry, I'm late!"
        st.session_state[CHAT_HISTORY_KEY].append({"role": "assistant", "content": initial_bot_message})
    # displying chat history messages
    for message in st.session_state[CHAT_HISTORY_KEY]:
        with st.chat_message(message[CHAT_HISTORY_ROLE_KEY], avatar = get_avatar_image(message)):
            st.markdown(message[CHAT_HISTORY_TEXT_KEY])
            if(CHAT_HISTORY_VISUALIZATION_TYPE_KEY in message):
                match message[CHAT_HISTORY_VISUALIZATION_TYPE_KEY]:
                    case 0:
                        continue
                    case 1:
                        PlotDataframe(message[CHAT_HISTORY_VISUALIZATION_KEY])
                    case 2:
                        config = {
                            "Images": st.column_config.ImageColumn(),
                            "TrustScores": st.column_config.ProgressColumn(),
                        }
                        st.dataframe(message[CHAT_HISTORY_VISUALIZATION_KEY], column_config=config)

def get_avatar_image(message) -> str:
    role = message["role"]
    return ASSISTANT_AVATAR_IMG if role == "assistant" else USER_AVATAR_IMG if role == "user" else None

async def initialize_session_state():
    """Initialize session state variables."""
    if TEMP_FILE_DIR_KEY not in st.session_state:
        st.session_state[TEMP_FILE_DIR_KEY] = tempfile.TemporaryDirectory()
    # st.write(st.session_state.tempFileDir)
    # stramlit reruns the script on every user interaction
    if AGENT_KEY not in st.session_state:
        curAgent = Agent()
        await curAgent.Initialize(st.session_state.tempFileDir.name)
        st.session_state[AGENT_KEY] = curAgent
    if STT_SOCKET_KEY not in st.session_state:
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect(('127.0.0.1', 41100))
        st.session_state[STT_SOCKET_KEY] = clientSocket

async def main():
    # Display Streamlit updates and handle the chat interface.
    with tempfile.TemporaryDirectory() as testTmpDir:
        
        

        print(testTmpDir)
        await initialize_session_state()

        initialize_conversation()

        # Insert custom CSS for glowing effect
        st.markdown(
            """
            <style>
            .cover-glow {
                width: 100%;
                height: auto;
                padding: 3px;
                box-shadow: 
                    0 0 5px #330000,
                    0 0 10px #660000,
                    0 0 15px #990000,
                    0 0 20px #CC0000,
                    0 0 25px #FF0000,
                    0 0 30px #FF3333,
                    0 0 35px #FF6666;
                position: relative;
                z-index: -1;
                border-radius: 45px;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Load and display sidebar image
        img_path = "imgs/sidebar_streamly_avatar.png"
        img_base64 = img_to_base64(img_path)
        if img_base64:
            st.sidebar.markdown(
                f'<img src="data:image/png;base64,{img_base64}" class="cover-glow">',
                unsafe_allow_html=True,
            )

        st.sidebar.markdown("---")

        with st.sidebar:
            uploadedFile = st.file_uploader("Upload any attachment here")
            filePath = pathlib.Path(st.session_state.tempFileDir.name)/"data.csv"
            print(uploadedFile)
            if uploadedFile is not None:
                print("writing file")
                f = open(filePath, 'wb')
                f.write(uploadedFile.read())
                f.close()


        st.sidebar.markdown("---")

        audioInput = None
        with bottom():
            col1, col2 = st.columns([1,0.1], gap="small")
            st.markdown("""
                <style>
                .st-emotion-cache-ocqkz7 {
                    gap: 0rem
                }
                .st-emotion-cache-1tvzk6f{
                    margin-top: 2px
                }
                </style>
                """,unsafe_allow_html=True)
            with col1:
                userInput = st.chat_input("Ask me about spectral questions:")  
            with col2:
                audio = audiorecorder(
                    start_prompt="🎤", 
                    stop_prompt="⏹", 
                    pause_prompt="", 
                    custom_style={'border-width': '0px', 'box-shadow': 'none'},
                    start_style={'border-width': '0px', 'box-shadow': 'none'},
                    stop_style={'color': 'red', 'border-width': '0px', 'box-shadow': 'none'})
                try:
                    audioBytes = pickle.dumps(audio)
                    print("audio length: ", len(audioBytes))
                    audioBytesLen = len(audioBytes).to_bytes(4, 'big')
                    st.session_state["sttSocket"].send(audioBytesLen)
                    st.session_state["sttSocket"].send(audioBytes)
                    lengthBytes = st.session_state["sttSocket"].recv(4)
                    if lengthBytes.decode('utf8') != "errr":
                        recvLen = int.from_bytes(lengthBytes, 'big')
                        recvBytes = st.session_state["sttSocket"].recv(recvLen)
                        recvData = recvBytes.decode('utf8')
                        if recvData in (None, '') or not recvData.strip():
                            print("emtpy string received")
                        else:
                            print(recvData)
                            audioInput = recvData
                except:
                    audioInput = None
                # print(type(audio))
        print(audioInput)
        if audioInput or userInput:
            print(type(userInput))
            print(userInput)
            prompt = None
            if userInput:
                prompt = userInput
            else:
                prompt = audioInput
            await HandleUserInput(prompt)
if __name__ == "__main__":
    if EVENT_LOOP_KEY not in st.session_state:
        loop = asyncio.new_event_loop()
        st.session_state[EVENT_LOOP_KEY] = loop
    else:
        loop = st.session_state[EVENT_LOOP_KEY]
    loop.run_until_complete(main())
    # asyncio.run(main())