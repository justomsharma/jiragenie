import requests
from requests.auth import HTTPBasicAuth
from config import JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN

class JiraClient:
    def __init__(self):
        self.base = JIRA_BASE_URL
        self.auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
        self.headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def create_issue(self, payload):
        url = f"{self.base}/rest/api/3/issue"
        return requests.post(url, json=payload, headers=self.headers, auth=self.auth)

    def update_issue(self, issue_key, fields=None, timetracking=None):
        url = f"{self.base}/rest/api/3/issue/{issue_key}"

        payload = {}

        if fields:
            payload["fields"] = fields

        if timetracking:
            payload["update"] = {
                "timetracking": [
                    {
                        "edit": {
                            "originalEstimate": timetracking
                        }
                    }
                ]
            }

        response = requests.put(
            url,
            json=payload,
            headers=self.headers,
            auth=self.auth
        )

        return response

    def transition_issue(self, issue_key, transition_id, fields=None):
        url = f"{self.base}/rest/api/3/issue/{issue_key}/transitions"

        payload = {
            "transition": {
                "id": transition_id
            }
        }

        if fields:
            payload["fields"] = fields

        response = requests.post(
            url,
            json=payload,
            headers=self.headers,
            auth=self.auth
        )

        return response

    def get_transitions(self, issue_key):
        url = f"{self.base}/rest/api/3/issue/{issue_key}/transitions"
        return requests.get(url, headers=self.headers, auth=self.auth)

    def add_comment(self, issue_key, comment):
        url = f"{self.base}/rest/api/3/issue/{issue_key}/comment"
        return requests.post(url, json={"body": comment}, headers=self.headers, auth=self.auth)

    def get_create_meta(self, project_key, issue_type):
        url = f"{self.base}/rest/api/3/issue/createmeta"
        params = {
            "projectKeys": project_key,
            "issuetypeNames": issue_type,
            "expand": "projects.issuetypes.fields"
        }
        return requests.get(url, headers=self.headers, auth=self.auth, params=params)
    
    def get_issue(self, issue_key):
        url = f"{self.base}/rest/api/3/issue/{issue_key}"
        return requests.get(url, headers=self.headers, auth=self.auth)

    def get_edit_meta(self, issue_key):
        url = f"{self.base}/rest/api/3/issue/{issue_key}/editmeta"
        return requests.get(url, headers=self.headers, auth=self.auth)