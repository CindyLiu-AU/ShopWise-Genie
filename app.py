from openai import OpenAI
import streamlit as st
import time
import os

client = OpenAI()
assistant_id = client.beta.assistants.retrieve(assistant_id=os.environ['OPENAI_ASS_KEY'])

# Initialize session state for chat management
if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(page_title="ShopWise", page_icon=":speech_balloon:")

# When "Start Chat" button is clicked
if st.button("Say Hello!"):
    st.session_state.start_chat = True
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

    # Simulate a user message (e.g., initial message)
    simulated_message = "Hello!"

    # Add the simulated user message if not already present
    if not any(msg["content"] == simulated_message and msg["role"] == "user" for msg in st.session_state.messages):
        # Add the simulated user message to the chat history
        st.session_state.messages.append({"role": "user", "content": simulated_message})
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=simulated_message
        )

        # Start the AI bot run
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id.id,
        )

        # Wait for the run to complete
        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )

        # Fetch assistant's response
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )
        assistant_messages_for_run = [
            message for message in messages
            if message.run_id == run.id and message.role == "assistant"
        ]
        for message in assistant_messages_for_run:
            # Ensure each assistant message is only added once
            if not any(msg["content"] == message.content[0].text.value and msg["role"] == "assistant" for msg in st.session_state.messages):
                st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})

st.title("ShopWise Genie")

# Display the chat history accurately, ensuring no duplication
if st.session_state.start_chat:
    # Loop through the stored messages to display them in the chat
    for idx, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        elif message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(message["content"])

    # Handle user input from the chat
    if prompt := st.chat_input("Message"):
        # Add the user's message to the session state and display it
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Send the user input to the API
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )

        # Start a new run for the user input
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id.id,
        )

        # Wait for the run to complete
        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )

        # Fetch the assistant's response for the current prompt
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )
        assistant_messages_for_run = [
            message for message in messages
            if message.run_id == run.id and message.role == "assistant"
        ]
        for message in assistant_messages_for_run:
            # Ensure the assistant's response is only added once
            if not any(msg["content"] == message.content[0].text.value and msg["role"] == "assistant" for msg in st.session_state.messages):
                st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
                with st.chat_message("assistant"):
                    st.markdown(message.content[0].text.value)

else:
    st.write("Click 'Say Hello!' to begin.")
