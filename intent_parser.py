import json
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are a Jira automation parser.
Convert user command into structured JSON.

Supported actions:
- create_issue
- move_issue
- add_comment
- update_issue

Always return valid JSON.
Estimate hours must be <= 8.
"""

def parse_intent(user_input):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        temperature=0
    )

    return json.loads(response.choices[0].message.content)