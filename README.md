<<<<<<< HEAD
# IA-ChatBot
=======
# ChatBot Streamlit

A simple chatbot built with Streamlit and OpenAI API, with login authentication using a SQLite database. The chatbot specializes in bicycle sales data analysis.

## Setup

1. Install dependencies: `pip install -r requirements.txt`

2. Set your OpenAI API key in a `.env` file: `OPENAI_API_KEY=your_key_here`

3. Run the app: `streamlit run app.py`

## Usage

- Login with username: `admin`, password: `password` (default user stored in `users.db`)
- To add more users, run `python add_user.py` and follow the prompts, or manually insert into the SQLite database `users.db` with hashed passwords (SHA-256).
- Type your message and press enter to chat with the AI.
- The chatbot can access `sales.db` for data analysis. Mention keywords like "sales", "data", "analysis", "bicycle", or "bike" in your message to include sales data in the conversation.
- The AI is programmed as the world's best data analyst for sales data, never makes calculation errors, and describes graphics when appropriate. It only responds to sales data analysis queries.
- Click "Logout" to return to the login screen.
- Each login starts a fresh chat session. When you log out, the transcript is saved to a file named `<username>_<session_id>_messages.json` in the project directory.
>>>>>>> bb4690f (InitialCommit-Streamlit_Chatbot)
