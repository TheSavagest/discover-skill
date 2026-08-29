#!/usr/bin/env python3
"""
Knowledge Layer CLI for Project Discovery System

Provides deterministic storage, querying, and management of discovery artifacts.
All agents/skills MUST use this CLI - no direct file manipulation.
"""

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import yaml

try:
    from jsonschema import validate, ValidationError
except ImportError:
    print("Error: jsonschema not installed. Run: pip install jsonschema pyyaml", file=sys.stderr)
    sys.exit(1)


class KnowledgeBase:
    def __init__(self, root: Path):
        self.root = root
        self.current = root / "current"
        self.history = root / "history"
        self.schemas = root / "schemas"
        self.cache = root.parent / "cache"

        # Ensure directories exist
        for d in [self.current, self.history, self.schemas, self.cache]:
            d.mkdir(parents=True, exist_ok=True)

        # Load schemas
        self._schemas = {}
        self._load_schemas()

        # Load vocabulary
        self._vocab = self._load_vocabulary()

        # Current state files (append-only YAML lines)
        self._files = {
            "entities": self.current / "entities.yaml",
            "facts": self.current / "facts.yaml",
            "evidence": self.current / "evidence.yaml",
            "sources": self.current / "sources.yaml",
            "relationships": self.current / "relationships.yaml",
            "questions": self.current / "questions.yaml",
            "conflicts": self.current / "conflicts.yaml",
            "runs": self.current / "runs.yaml",
        }

    def _load_schemas(self):
        for schema_file in self.schemas.glob("*.yaml"):
            name = schema_file.stem
            with open(schema_file, "r", encoding="utf-8") as f:
                self._schemas[name] = yaml.safe_load(f)

    def _load_vocabulary(self) -> Dict:
        vocab_file = self.schemas / "vocabulary.yaml"
        if vocab_file.exists():
            with open(vocab_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {}

    def _validate(self, obj_type: str, data: Dict) -> List[str]:
        """Validate against schema, return list of errors (empty if valid)"""
        schema = self._schemas.get(obj_type)
        if not schema:
            return [f"No schema for type: {obj_type}"]
        try:
            validate(instance=data, schema=schema)
            return []
        except ValidationError as e:
            return [f"{e.json_path}: {e.message}"]

    def _append_yaml(self, file: Path, obj: Dict):
        """Append a single YAML document to file"""
        with open(file, "a", encoding="utf-8") as f:
            yaml.dump(obj, f, allow_unicode=True, sort_keys=False)
            f.write("\n---\n")

    def _read_all(self, file: Path) -> List[Dict]:
        """Read all YAML documents from file"""
        if not file.exists():
            return []
        with open(file, "r", encoding="utf-8") as f:
            return list(yaml.safe_load_all(f))

    def _find_by_id(self, file: Path, id: str) -> Optional[Dict]:
        for obj in self._read_all(file):
            if obj.get("id") == id:
                return obj
        return None

    def _write_all(self, file: Path, objects: List[Dict]):
        """Overwrite file with all objects"""
        with open(file, "w", encoding="utf-8") as f:
            for obj in objects:
                yaml.dump(obj, f, allow_unicode=True, sort_keys=False)
                f.write("\n---\n")

    # --- ID Generation ---
    def _next_id(self, prefix: str, file: Path) -> str:
        existing = set()
        for obj in self._read_all(file):
            eid = obj.get("id", "")
            if eid.startswith(prefix):
                try:
                    num = int(eid.split("-")[1])
                    existing.add(num)
                except (IndexError, ValueError):
                    pass
        next_num = max(existing) + 1 if existing else 1
        return f"{prefix}-{next_num:06d}"

    # --- Public API ---
    def add_source(self, data: Dict) -> str:
        errors = self._validate("source", data)
        if errors:
            raise ValueError(f"Invalid source: {errors}")
        sid = data.get("id") or self._next_id("SRC", self._files["sources"])
        data["id"] = sid
        if "timestamps" not in data:
            data["timestamps"] = {}
        data["timestamps"]["observed_at"] = datetime.now(timezone.utc).isoformat()
        self._append_yaml(self._files["sources"], data)
        return sid

    def add_entity(self, data: Dict) -> str:
        errors = self._validate("entity", data)
        if errors:
            raise ValueError(f"Invalid entity: {errors}")
        eid = data.get("id") or self._next_id("ENT", self._files["entities"])
        data["id"] = eid
        if "timestamps" not in data:
            data["timestamps"] = {}
        data["timestamps"]["discovered_at"] = datetime.now(timezone.utc).isoformat()
        self._append_yaml(self._files["entities"], data)
        return eid

    def add_evidence(self, data: Dict) -> str:
        errors = self._validate("evidence", data)
        if errors:
            raise ValueError(f"Invalid evidence: {errors}")
        eid = data.get("id") or self._next_id("EVD", self._files["evidence"])
        data["id"] = eid
        self._append_yaml(self._files["evidence"], data)
        return eid

    def add_fact(self, data: Dict) -> str:
        errors = self._validate("fact", data)
        if errors:
            raise ValueError(f"Invalid fact: {errors}")
        fid = data.get("id") or self._next_id("FACT", self._files["facts"])
        data["id"] = fid
        if "timestamps" not in data:
            data["timestamps"] = {}
        data["timestamps"]["observed_at"] = datetime.now(timezone.utc).isoformat()
        self._append_yaml(self._files["facts"], data)
        return fid

    def add_relationship(self, data: Dict) -> str:
        errors = self._validate("relationship", data)
        if errors:
            raise ValueError(f"Invalid relationship: {errors}")
        rid = data.get("id") or self._next_id("REL", self._files["relationships"])
        data["id"] = rid
        if "timestamps" not in data:
            data["timestamps"] = {}
        data["timestamps"]["created_at"] = datetime.now(timezone.utc).isoformat()
        self._append_yaml(self._files["relationships"], data)
        return rid

    def add_question(self, data: Dict) -> str:
        errors = self._validate("question", data)
        if errors:
            raise ValueError(f"Invalid question: {errors}")
        qid = data.get("id") or self._next_id("Q", self._files["questions"])
        data["id"] = qid
        if "timestamps" not in data:
            data["timestamps"] = {}
        data["timestamps"]["created_at"] = datetime.now(timezone.utc).isoformat()
        self._append_yaml(self._files["questions"], data)
        return qid

    def add_conflict(self, data: Dict) -> str:
        errors = self._validate("conflict", data)
        if errors:
            raise ValueError(f"Invalid conflict: {errors}")
        cid = data.get("id") or self._next_id("CON", self._files["conflicts"])
        data["id"] = cid
        if "timestamps" not in data:
            data["timestamps"] = {}
        data["timestamps"]["created_at"] = datetime.now(timezone.utc).isoformat()
        self._append_yaml(self._files["conflicts"], data)
        return cid

    def add_run(self, data: Dict) -> str:
        errors = self._validate("discovery_run", data)
        if errors:
            raise ValueError(f"Invalid run: {errors}")
        rid = data.get("id") or self._next_id("RUN", self._files["runs"])
        data["id"] = rid
        self._append_yaml(self._files["runs"], data)
        return rid

    # --- Query ---
    def query_entities(self, **filters) -> List[Dict]:
        return self._filter_objects(self._files["entities"], filters)

    def query_facts(self, **filters) -> List[Dict]:
        return self._filter_objects(self._files["facts"], filters)

    def query_evidence(self, **filters) -> List[Dict]:
        return self._filter_objects(self._files["evidence"], filters)

    def query_sources(self, **filters) -> List[Dict]:
        return self._filter_objects(self._files["sources"], filters)

    def query_relationships(self, **filters) -> List[Dict]:
        return self._filter_objects(self._files["relationships"], filters)

    def query_questions(self, **filters) -> List[Dict]:
        return self._filter_objects(self._files["questions"], filters)

    def query_conflicts(self, **filters) -> List[Dict]:
        return self._filter_objects(self._files["conflicts"], filters)

    def query_runs(self, **filters) -> List[Dict]:
        return self._filter_objects(self._files["runs"], filters)

    def _filter_objects(self, file: Path, filters: Dict) -> List[Dict]:
        results = []
        for obj in self._read_all(file):
            match = True
            for key, value in filters.items():
                if key not in obj:
                    match = False
                    break
                if isinstance(value, list):
                    if obj[key] not in value:
                        match = False
                        break
                elif obj[key] != value:
                    match = False
                    break
            if match:
                results.append(obj)
        return results

    def get_by_id(self, obj_type: str, id: str) -> Optional[Dict]:
        file = self._files.get(obj_type + "s") or self._files.get(obj_type)
        if not file:
            return None
        return self._find_by_id(file, id)

    # --- Merge/Deduplicate ---
    def merge_entities(self, primary_id: str, duplicate_ids: List[str]) -> Dict:
        """Merge duplicate entities into primary, update all references"""
        primary = self.get_by_id("entity", primary_id)
        if not primary:
            raise ValueError(f"Primary entity {primary_id} not found")

        duplicates = []
        for did in duplicate_ids:
            dup = self.get_by_id("entity", did)
            if not dup:
                raise ValueError(f"Duplicate entity {did} not found")
            duplicates.append(dup)

        # Merge evidence
        all_evidence = set(primary.get("evidence", []))
        for d in duplicates:
            all_evidence.update(d.get("evidence", []))
        primary["evidence"] = list(all_evidence)

        # Merge metadata
        for d in duplicates:
            for k, v in d.get("metadata", {}).items():
                if k not in primary.get("metadata", {}):
                    primary.setdefault("metadata", {})[k] = v

        # Update primary
        entities = self._read_all(self._files["entities"])
        entities = [e for e in entities if e["id"] not in duplicate_ids]
        for i, e in enumerate(entities):
            if e["id"] == primary_id:
                entities[i] = primary
                break
        self._write_all(self._files["entities"], entities)

        # Update references in facts
        self._replace_refs("facts", "subject.entity", duplicate_ids, primary_id)
        self._replace_refs("facts", "object.entity", duplicate_ids, primary_id)
        self._replace_refs("relationships", "from", duplicate_ids, primary_id)
        self._replace_refs("relationships", "to", duplicate_ids, primary_id)
        self._replace_refs("questions", "context.entities", duplicate_ids, primary_id)
        self._replace_refs("conflicts", "subject", duplicate_ids, primary_id)

        return primary

    def _replace_refs(self, file_key: str, field: str, old_ids: List[str], new_id: str):
        file = self._files[file_key]
        objects = self._read_all(file)
        changed = False
        for obj in objects:
            # Navigate nested field (e.g., "subject.entity")
            parts = field.split(".")
            target = obj
            for p in parts[:-1]:
                target = target.get(p, {})
            if isinstance(target, dict) and parts[-1] in target:
                if target[parts[-1]] in old_ids:
                    target[parts[-1]] = new_id
                    changed = True
            elif isinstance(target, list):
                for i, v in enumerate(target):
                    if v in old_ids:
                        target[i] = new_id
                        changed = True
        if changed:
            self._write_all(file, objects)

    # --- Snapshot ---
    def snapshot(self, run_id: str) -> Path:
        """Create a snapshot of current state for a run"""
        run_dir = self.history / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        for key, file in self._files.items():
            if file.exists():
                objects = self._read_all(file)
                out_file = run_dir / f"{key}.yaml"
                self._write_all(out_file, objects)

        return run_dir

    # --- Validation ---
    def validate_all(self) -> Dict[str, List[str]]:
        """Validate all objects in current state"""
        errors = {}
        for obj_type, file in self._files.items():
            if not file.exists():
                continue
            type_name = obj_type.rstrip("s")
            type_errors = []
            for obj in self._read_all(file):
                errs = self._validate(type_name, obj)
                if errs:
                    type_errors.append(f"{obj.get('id', 'unknown')}: {errs}")
            if type_errors:
                errors[obj_type] = type_errors
        return errors

    # --- Stale Detection ---
    def mark_stale(self, obj_type: str, id: str) -> bool:
        file = self._files.get(obj_type + "s") or self._files.get(obj_type)
        if not file:
            return False
        objects = self._read_all(file)
        for obj in objects:
            if obj["id"] == id:
                obj["status"] = "stale"
                self._write_all(file, objects)
                return True
        return False

    # --- Rollback ---
    def rollback(self, run_id: str) -> bool:
        """Restore state from a historical run"""
        run_dir = self.history / run_id
        if not run_dir.exists():
            return False

        for key, file in self._files.items():
            snap_file = run_dir / f"{key}.yaml"
            if snap_file.exists():
                objects = self._read_all(snap_file)
                self._write_all(file, objects)
        return True


def main():
    parser = argparse.ArgumentParser(description="Knowledge Layer CLI")
    parser.add_argument("--kb", default=".ai/knowledge", help="Knowledge base root")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # Add commands
    for obj_type in ["source", "entity", "evidence", "fact", "relationship", "question", "conflict", "run"]:
        p = sub.add_parser(f"add-{obj_type}", help=f"Add {obj_type}")
        p.add_argument("--data", required=True, help="JSON or YAML data")
        p.add_argument("--file", help="Read data from file")

    # Query commands
    for obj_type in ["entities", "facts", "evidence", "sources", "relationships", "questions", "conflicts", "runs"]:
        p = sub.add_parser(f"query-{obj_type}", help=f"Query {obj_type}")
        p.add_argument("--filter", action="append", default=[], help="key=value filter")
        p.add_argument("--id", help="Query by ID")

    # Merge
    p = sub.add_parser("merge-entities", help="Merge duplicate entities")
    p.add_argument("--primary", required=True)
    p.add_argument("--duplicates", required=True, nargs="+")

    # Snapshot
    p = sub.add_parser("snapshot", help="Create snapshot for run")
    p.add_argument("--run-id", required=True)

    # Validate
    sub.add_parser("validate", help="Validate all objects")

    # Stale
    p = sub.add_parser("mark-stale", help="Mark object as stale")
    p.add_argument("--type", required=True, choices=["entity", "fact", "relationship", "question", "conflict"])
    p.add_argument("--id", required=True)

    # Rollback
    p = sub.add_parser("rollback", help="Rollback to previous run")
    p.add_argument("--run-id", required=True)

    # Stats
    sub.add_parser("stats", help="Show knowledge base statistics")

    args = parser.parse_args()

    kb = KnowledgeBase(Path(args.kb).resolve())

    try:
        if args.cmd.startswith("add-"):
            obj_type = args.cmd[4:]
            data = {}
            if args.file:
                with open(args.file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
            else:
                data = yaml.safe_load(args.data)
            method = getattr(kb, f"add_{obj_type}")
            oid = method(data)
            print(oid)

        elif args.cmd.startswith("query-"):
            obj_type = args.cmd[6:]
            filters = {}
            for f in args.filter:
                k, v = f.split("=", 1)
                # Try to parse as JSON for complex values
                try:
                    v = json.loads(v)
                except json.JSONDecodeError:
                    pass
                filters[k] = v
            if args.id:
                filters["id"] = args.id
            method = getattr(kb, f"query_{obj_type}")
            results = method(**filters)
            print(yaml.dump_all(results, allow_unicode=True, sort_keys=False))

        elif args.cmd == "merge-entities":
            result = kb.merge_entities(args.primary, args.duplicates)
            print(f"Merged into {result['id']}")

        elif args.cmd == "snapshot":
            path = kb.snapshot(args.run_id)
            print(f"Snapshot created at {path}")

        elif args.cmd == "validate":
            errors = kb.validate_all()
            if errors:
                print("VALIDATION ERRORS:", file=sys.stderr)
                for obj_type, errs in errors.items():
                    print(f"\n{obj_type}:", file=sys.stderr)
                    for e in errs:
                        print(f"  - {e}", file=sys.stderr)
                sys.exit(1)
            else:
                print("All objects valid")

        elif args.cmd == "mark-stale":
            ok = kb.mark_stale(args.type, args.id)
            print("OK" if ok else "NOT FOUND")

        elif args.cmd == "rollback":
            ok = kb.rollback(args.run_id)
            print("OK" if ok else "RUN NOT FOUND")

        elif args.cmd == "stats":
            for obj_type, file in kb._files.items():
                count = len(kb._read_all(file))
                print(f"{obj_type}: {count}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()