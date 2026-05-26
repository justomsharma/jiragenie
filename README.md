# JiraGenie

A natural-language CLI for Jira, powered by an LLM intent parser and a self-healing transition engine.

You type what you want in plain English. JiraGenie figures out the action, talks to the Jira REST API, and recovers when Jira blocks the operation because a required field is missing.

```bash
jiragenie run "create a story called 'Fix login bug' in project ENG"
jiragenie run "move ENG-142 to done"
jiragenie run "comment on ENG-142: blocked on auth team"
```

## Why this exists

Jira's REST API is powerful but brittle in two ways:

1. **You need to know the schema.** Creating an issue, moving it through workflow, and updating fields all require knowing project keys, issue type names, transition IDs, and the editable fields for the current workflow state.
2. **Workflow transitions fail in obscure ways.** Jira will reject a transition because a required field (e.g. `duedate`, `timetracking`) isn't set, but it tells you only after you try.

JiraGenie wraps both problems behind a natural-language interface. An LLM parses intent into a structured action; an execution loop walks the workflow graph; when a transition fails, a repair layer reads the error, fills in the required fields, and retries.

## How it works

```
   user input
       │
       ▼
┌─────────────────┐
│ intent_parser   │  ── GPT-4o-mini → structured JSON
│  {action,        │     {action: "move_issue",
│   target, ...}   │      issue_key: "ENG-142",
└─────────────────┘      destination: "done"}
       │
       ▼
┌─────────────────┐
│ cli dispatcher  │  ── route to create / move / comment
└─────────────────┘
       │
       ▼
┌─────────────────┐
│ workflow walker │  ── BFS through valid transitions toward
│ + loop guard    │     destination; prefers "in progress"
│                 │     category over terminal states
└─────────────────┘
       │
       ▼
┌─────────────────┐
│ repair engine   │  ── on 400: parse missing fields,
│                 │     auto-fill (duedate, description,
│                 │     timetracking), retry transition
└─────────────────┘
       │
       ▼
   Jira REST API
```

### Three design ideas worth noting

**1. The workflow graph isn't always a tree.** A "Done" transition may exist from "In Review" but not from "To Do". JiraGenie does a bounded walk through `get_transitions` to find a reachable path to the destination, with a loop guard so it never revisits a state.

**2. The destination isn't always available as a direct transition.** When it's not, the walker prefers transitions into the `indeterminate` (in-progress) status category over terminal ones, so it doesn't accidentally close an issue while trying to move it forward.

**3. Failed transitions are self-healed, not just reported.** A 400 from Jira usually means a required field. The repair layer auto-fills a sensible default (due date 3 days out, placeholder description in ADF format, time estimate) and retries — recovering instead of failing.

## Setup

```bash
git clone https://github.com/<your-handle>/jiragenie.git
cd jiragenie

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env with your Jira URL, email, API token, and OpenAI key
```

Get an Atlassian API token at https://id.atlassian.com/manage-profile/security/api-tokens.

## Usage

```bash
# Create an issue
python cli.py run "create a story called 'Refactor auth module' in project ENG"

# Move an issue through workflow
python cli.py run "move ENG-142 to in progress"

# Move to a non-adjacent state (walker finds a path)
python cli.py run "move ENG-142 to done"

# Add a comment
python cli.py run "comment on ENG-142: blocked on auth team"
```

## Tech stack

- **Python 3.9+**
- **Typer** for the CLI
- **OpenAI** (`gpt-4o-mini`) for intent parsing
- **requests** for Jira REST v3
- **Rich** for terminal output

## Project structure

```
jiragenie/
├── cli.py                # entry point; dispatcher + workflow walker
├── intent_parser.py      # LLM-powered natural language → structured action
├── jira_client.py        # thin REST wrapper around Jira API v3
├── repair_engine.py      # generic retry-with-repair helper
├── metadata.py           # introspects required fields from create/edit meta
├── config.py             # env loading + validation
├── requirements.txt
└── .env.example
```

## Roadmap

- [ ] Subtask creation under a parent issue from a single command
- [ ] Bulk operations (`"move all ENG-1xx to done"`)
- [ ] Pluggable LLM backend (Claude, local models)
- [ ] Persistent intent cache to avoid LLM call on repeat phrasings
- [ ] Eval harness measuring intent-parser accuracy on a labeled set

## License

MIT — see [LICENSE](LICENSE).

---

*Built by [Om Sharma](https://medium.com/@OmsharmaOfficial). I write about real-time AI systems and agentic workflows.*
