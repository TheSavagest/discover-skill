---
name: discover-git
description: Discover Git history, branches, tags, file history, churn, change frequency and historical hotspots.
compatibility: opencode
---

# Git Discovery

Use Git commands and deterministic scripts. Do not interpret metrics as quality judgments.

## Inputs

- `run_id`: Current discovery run ID
- `repo_root`: Repository root path
- `since`: Optional date for incremental (default: 12 months ago)
- `max_commits`: Optional limit

## Collect

- Current revision (`git rev-parse HEAD`)
- Branches (`git branch -a`)
- Tags (`git tag`)
- Commit history (`git log --oneline --since="12 months ago"`)
- File history per file (`git log --oneline -- <file>`)
- Renames (`git log --diff-filter=R --name-status`)
- Deletions (`git log --diff-filter=D --name-only`)
- Authors (`git log --format="%an <%ae>"`)
- File churn (commits per file)
- Change frequency (commits per time period)
- Recent changes (last 30/90 days)
- Change hotspots (top N files by churn)

## Deterministic Commands

```bash
# Current revision
git rev-parse HEAD

# Branches
git branch -a --format="%(refname:short)"

# Tags
git tag

# Commit history (last 12 months)
git log --oneline --since="12 months ago" --format="%H|%an|%ae|%ad|%s" --date=iso

# File churn
git log --oneline --since="12 months ago" --name-only --format= | sort | uniq -c | sort -rn

# Authors
git log --oneline --since="12 months ago" --format="%an <%ae>" | sort | uniq -c | sort -rn

# Hotspots (top 20)
git log --oneline --since="12 months ago" --name-only --format= | grep -v "^$" | sort | uniq -c | sort -rn | head -20
```

## Knowledge Operations

```bash
# Git repository entity
python knowledge.py add-entity --data '{
  "type": "git_repository",
  "name": "myapp",
  "canonical_name": "myapp",
  "source": "<repository_src_id>",
  "location": {"path": "<repo_root>", "revision": "<rev>"},
  "metadata": {"remote_url": "https://github.com/org/myapp.git"},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["direct_observation"]},
  "status": "active",
  "discovered_by": {"agent": "git-discovery", "skill": "discover-git", "run": "<run_id>"}
}'

# File churn fact
python knowledge.py add-fact --data '{
  "subject": {"entity": "<OrderService_cs_ent_id>"},
  "predicate": "has_churn",
  "object": {"kind": "value", "value": 87},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["direct_observation", "static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "git-discovery", "skill": "discover-git", "run": "<run_id>"}
}'

# Fact: file has authors
python knowledge.py add-fact --data '{
  "subject": {"entity": "<OrderService_cs_ent_id>"},
  "predicate": "has_authors",
  "object": {"kind": "value", "value": 6},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["direct_observation", "static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "git-discovery", "skill": "discover-git", "run": "<run_id>"}
}'

# Hotspot entity (aggregated)
python knowledge.py add-entity --data '{
  "type": "git_hotspot",
  "name": "OrderService.cs",
  "canonical_name": "src/MyApp.Core/Orders/OrderService.cs",
  "source": "<git_src_id>",
  "location": {"path": "src/MyApp.Core/Orders/OrderService.cs"},
  "metadata": {"churn": 87, "authors": 6, "changes_last_90_days": 21, "bug_fix_commits": 12},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["direct_observation", "static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "git-discovery", "skill": "discover-git", "run": "<run_id>"}
}'
```