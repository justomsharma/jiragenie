import typer
from jira_client import JiraClient
from intent_parser import parse_intent
from config import DEFAULT_PROJECT

app = typer.Typer()
jira = JiraClient()

@app.command()
def run(command: str):
    """Natural language Jira command"""
    structured = parse_intent(command)

    action = structured.get("action")

    if action == "create_issue":
        payload = {
            "fields": {
                "project": {"key": DEFAULT_PROJECT},
                "summary": structured["title"],
                "description": structured.get("description", ""),
                "issuetype": {"name": structured.get("issue_type", "Story")}
            }
        }

        response = jira.create_issue(payload)
        print(response.json())

    elif action == "move_issue":
        issue_key = structured["issue_key"]
        destination = (
    structured.get("destination")
    or structured.get("status")
)

        if not destination:
            print("No destination provided.")
            return

        destination = destination.lower()

        visited = set()
        max_attempts = 10

        for attempt in range(max_attempts):

            issue = jira.get_issue(issue_key).json()
            current_status = issue["fields"]["status"]["name"].lower()
            current_category = issue["fields"]["status"]["statusCategory"]["key"]

            print(f"\nAttempt {attempt+1}")
            print("Current:", current_status)

            if current_status == destination:
                print("Reached destination.")
                return

            if current_status in visited:
                print("Detected loop. Stopping.")
                return

            visited.add(current_status)

            transitions = jira.get_transitions(issue_key).json()["transitions"]

            # Direct transition first
            for t in transitions:
                if t["name"].lower() == destination:
                    print("Direct transition available.")
                    jira.transition_issue(issue_key, t["id"])
                    break
            else:
                # Filter out terminal states
                valid_transitions = []

                for t in transitions:
                    category = t["to"]["statusCategory"]["key"]
                    name = t["name"].lower()

                    if category == "done" and destination != name:
                        continue

                    valid_transitions.append(t)

                if not valid_transitions:
                    print("No valid transitions available.")
                    return

                # Prefer in-progress category
                chosen = None
                for t in valid_transitions:
                    if t["to"]["statusCategory"]["key"] == "indeterminate":
                        chosen = t
                        break

                if not chosen:
                    chosen = valid_transitions[0]

                print("Choosing:", chosen["name"])
                response = jira.transition_issue(issue_key, chosen["id"])

                print("Transition status code:", response.status_code)
                print("Transition response body:", response.text)

                if response.status_code == 400:

                    print("Updating required fields properly...")

                    from datetime import datetime, timedelta
                    due = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")

                    fields = {
                        "duedate": due,
                        "description": {
                            "type": "doc",
                            "version": 1,
                            "content": [{
                                "type": "paragraph",
                                "content": [{"type": "text", "text": "Auto-filled by JiraGenie"}]
                            }]
                        }
                    }

                    # 👇 THIS calls the updated jira_client method
                    jira.update_issue(
                        issue_key,
                        fields=fields,
                        timetracking="4h"
                    )

                    print("Retrying transition...")
                    response = jira.transition_issue(issue_key, chosen["id"])
                    print("Retry status:", response.status_code)
                    print("Retry response:", response.text)

        print("Failed to reach destination.")

    elif action == "add_comment":
        jira.add_comment(structured["issue_key"], structured["comment"])
        print("Comment added")

    else:
        print("Unsupported action")

if __name__ == "__main__":
    app()