
# ChatBot Streamlit

A simple chatbot built with Streamlit and the OpenAI API, featuring login authentication backed by SQLite. The assistant is specialized in data analysis.

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Set your OpenAI API key in a `.env` file: `OPENAI_API_KEY=your_key_here`
3. Run the app: `streamlit run app.py`

## Usage

- Login with username `admin` and password `password` (default user stored in `users.db`).
- To add more users, run `python add_user.py` and follow the prompts, or insert records directly into the `users` table with SHA-256 hashed passwords.
- Type your message and press Enter to chat with the AI.
- The chatbot can access `sales.db` for data analysis. Mention keywords like "sales", "data", "analysis", "bicycle", or "bike" to encourage database use.
- The AI is configured as the world's best sales data analyst, never makes calculation errors, and describes charts when appropriate. It politely declines non-sales requests.
- Conversation transcripts are written to `conversations/<username>_<session_id>_messages.json` (or `<username>_messages.json` if no session ID). The file is updated after every assistant reply and again when you click **Logout**.
- Click **Logout** to return to the login screen. After logging out you'll see a **Conversation saved to ...** banner with the relative path to the transcript.
- If you do not see files in the `conversations` folder, make sure the Streamlit app is shut down via the **Logout** button or that it has generated at least one assistant response. The folder is ignored by Git via `.gitignore`, so new transcripts won't appear in `git status`.
- Each login starts a fresh chat session.
