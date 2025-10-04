import streamlit as st
import openai
import os
from dotenv import load_dotenv
import hashlib
import sqlite3
import json
import uuid

load_dotenv()

SYSTEM_PROMPT = "You are the world's best data analyst, specializing exclusively in analyzing bicycle sales data for our company. You never make calculation errors. When appropriate, describe graphics or charts to visualize the data. Do not respond to any topics outside of sales data analysis. If the query is not about sales data, politely decline. You can query the sales database using the query_sales_db function. The sales table has columns: id (INTEGER), date (TEXT), product (TEXT), quantity (INTEGER), price (REAL), total (REAL)."

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_sales_db",
            "description": "Execute a SQL query on the sales database and return the results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL query to execute on the sales table."
                    }
                },
                "required": ["query"]
            }
        }
    }
]

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password_hash TEXT)''')
    # Insert default user if not exists
    c.execute("INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)", ('admin', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'))
    conn.commit()
    conn.close()

def query_sales_db(query):
    """
    Execute a SQL query on the sales.db database.
    """
    try:
        conn = sqlite3.connect('sales.db')
        c = conn.cursor()
        c.execute(query)
        rows = c.fetchall()
        conn.close()
        return str(rows)
    except Exception as e:
        return f"Error: {str(e)}"

init_db()

# Session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        hashed_input = hashlib.sha256(password.encode()).hexdigest()
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, hashed_input))
        if c.fetchone():
            st.session_state.username = username
            st.session_state.session_id = uuid.uuid4().hex
            st.session_state.messages = []
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials")
        conn.close()
else:
    st.title("Chatbot con OpenAI")

    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        st.error("Please set the OPENAI_API_KEY environment variable.")
        st.stop()

    # Initialize OpenAI client
    client = openai.OpenAI(api_key=api_key)

    # Session state for messages
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    # User input
    if prompt := st.chat_input("Escribe tu mensaje"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            try:
                # Prepare messages with system prompt
                messages_with_system = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages_with_system,
                    tools=TOOLS,
                    tool_choice="auto"
                )
                # Handle tool calls
                if response.choices[0].message.tool_calls:
                    tool_call = response.choices[0].message.tool_calls[0]
                    if tool_call.function.name == "query_sales_db":
                        query = eval(tool_call.function.arguments)["query"]
                        result = query_sales_db(query)
                        # Add tool response
                        st.session_state.messages.append({"role": "assistant", "content": "", "tool_calls": response.choices[0].message.tool_calls})
                        st.session_state.messages.append({"role": "tool", "content": result, "tool_call_id": tool_call.id})
                        # Get final response
                        final_response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=messages_with_system + [{"role": "assistant", "content": "", "tool_calls": response.choices[0].message.tool_calls}, {"role": "tool", "content": result, "tool_call_id": tool_call.id}]
                        )
                        full_response = final_response.choices[0].message.content
                    else:
                        full_response = "Unknown tool called."
                else:
                    full_response = response.choices[0].message.content
                message_placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"Error: {str(e)}"
                message_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

    # Logout button
    if st.button("Logout"):
        # Save messages
        username = st.session_state.get('username', 'unknown')
        serializable_messages = []
        for msg in st.session_state.messages:
            if msg.get('role') in ['user', 'assistant']:
                serializable_msg = {k: v for k, v in msg.items() if k != 'tool_calls'}
                serializable_messages.append(serializable_msg)
        session_id = st.session_state.get('session_id')
        filename = f"{username}_{session_id}_messages.json" if session_id else f"{username}_messages.json"
        try:
            with open(filename, "w") as f:
                json.dump(serializable_messages, f)
        except TypeError:
            # If serialization fails, persist an empty conversation for traceability
            with open(filename, "w") as f:
                json.dump([], f)
        st.session_state.logged_in = False
        st.session_state.pop('messages', None)
        st.session_state.pop('session_id', None)
        st.session_state.pop('username', None)
        st.rerun()