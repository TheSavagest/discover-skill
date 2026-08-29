---
name: discover-init
description: Initialize a project discovery run, establish the repository revision and prepare the discovery knowledge workspace.
compatibility: opencode
---

# Discover Init

Initialize a new discovery run.

## Inputs

- `project_root`: Path to the project repository (default: current working directory)
- `mode`: Discovery mode - `full`, `incremental`, or `targeted` (default: `full`)
- `previous_run_id`: Previous run ID for incremental mode

## Outputs

- Creates/updates discovery run record in knowledge base
- Returns `run_id` and `revision`

## Algorithm

1. Determine repository root (walk up from project_root looking for .git)
2. Get current Git revision (`git rev-parse HEAD`)
3. Get current branch (`git branch --show-current`)
4. Check if Git is available
5. Generate run ID via `knowledge.py add-run`
6. Record available sources (repository, git)

## Knowledge Operations

```bash
# Add source for repository
python knowledge.py add-source --data '{
  "type": "repository",
  "uri": "file://<repo_root>",
  "repository": {"path": "<repo_root>", "revision": "<rev>"},
  "access": {"available": true}
}'

# Add source for git
python knowledge.py add-source --data '{
  "type": "git_commit",
  "uri": "git://<repo_root>@<rev>",
  "repository": {"path": "<repo_root>", "revision": "<rev>"},
  "access": {"available": true}
}'

# Add discovery run
python knowledge.py add-run --data '{
  "project": {"repository": "<src_id>", "revision": "<rev>", "branch": "<branch>"},
  "mode": "<mode>",
  "agents": [],
  "sources": {"available": ["repository", "git"], "unavailable": []},
  "statistics": {"entities": 0, "facts": 0, "evidence": 0, "relationships": 0, "questions": 0, "conflicts": 0},
  "status": "in_progress"
}'
```

## Error Handling

- If not a Git repository, continue with `repository` source only
- If Git commands fail, record `git` in unavailable sources