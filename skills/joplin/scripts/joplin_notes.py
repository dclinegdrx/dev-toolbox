#!/usr/bin/env python3
"""Deterministic Joplin Web Clipper API operations for the Joplin skill."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Any

DEFAULT_API_URI = "http://localhost:41184"
DEFAULT_NOTEBOOK = "Agent Notes"
NOTE_TYPES = {
    "technical-explanation",
    "debugging",
    "decision",
    "investigation",
    "architecture",
    "meeting-summary",
    "implementation-plan",
    "reference",
}


def fail(message: str, exit_code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(exit_code)


def load_config() -> dict[str, Any]:
    path = pathlib.Path.home() / ".joplinrc"
    if not path.exists():
        fail(f"Configuration not found: {path}")
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"Unable to read valid JSON from {path}: {exc}")
    if not cfg.get("auth_token"):
        fail(f"Missing required auth_token in {path}")
    return cfg


def detect_tool() -> str:
    if os.environ.get("CLAUDE_CODE_ENTRYPOINT"):
        return "Claude Code"
    if os.environ.get("CURSOR_TRACE_ID"):
        return "Cursor"
    if any(key.startswith("OPENCODE_") for key in os.environ):
        return "OpenCode"
    return "unknown"


def detect_model() -> str:
    for key in ("ANTHROPIC_MODEL", "OPENAI_MODEL", "CURSOR_MODEL", "OPENCODE_MODEL"):
        value = os.environ.get(key)
        if value:
            return value
    return "unknown"


class JoplinClient:
    def __init__(self, cfg: dict[str, Any]) -> None:
        self.base = str(cfg.get("api_uri", DEFAULT_API_URI)).rstrip("/")
        self.token = str(cfg["auth_token"])
        self.cfg = cfg

    def request(self, method: str, path: str, data: dict[str, Any] | None = None) -> Any:
        separator = "&" if "?" in path else "?"
        url = f"{self.base}{path}{separator}token={urllib.parse.quote(self.token)}"
        payload = json.dumps(data).encode("utf-8") if data is not None else None
        request = urllib.request.Request(
            url,
            data=payload,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            fail(f"Joplin API returned HTTP {exc.code}: {detail}")
        except urllib.error.URLError as exc:
            fail(f"Unable to reach Joplin Web Clipper API at {self.base}: {exc.reason}")
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            fail(f"Joplin API returned invalid JSON: {exc}")

    def paged(self, path: str) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        page = 1
        while True:
            separator = "&" if "?" in path else "?"
            result = self.request("GET", f"{path}{separator}page={page}&limit=100")
            items.extend(result.get("items", []))
            if not result.get("has_more"):
                return items
            page += 1

    def folders(self) -> list[dict[str, Any]]:
        return self.paged("/folders?fields=id,title,parent_id")

    def resolve_folder(self, title: str, create_default: bool = False) -> dict[str, Any] | None:
        folder = next((item for item in self.folders() if item.get("title") == title), None)
        if folder:
            return folder
        if create_default and title == DEFAULT_NOTEBOOK:
            return self.request("POST", "/folders", {"title": title})
        return None


def local_timestamp() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")


def parse_keywords(value: str) -> list[str]:
    keywords = [item.strip().lower() for item in value.split(",") if item.strip()]
    if not 3 <= len(keywords) <= 7:
        fail("Keywords must contain 3 to 7 comma-separated values")
    return keywords


def read_text(path: str) -> str:
    try:
        return pathlib.Path(path).read_text(encoding="utf-8").strip()
    except OSError as exc:
        fail(f"Unable to read {path}: {exc}")


def folder_descendants(folders: list[dict[str, Any]], roots: set[str]) -> set[str]:
    allowed = set(roots)
    changed = True
    while changed:
        changed = False
        for folder in folders:
            if folder.get("parent_id") in allowed and folder.get("id") not in allowed:
                allowed.add(folder["id"])
                changed = True
    return allowed


def allowed_folder_ids(client: JoplinClient) -> set[str] | None:
    folders = client.folders()
    by_title = {folder.get("title"): folder.get("id") for folder in folders}
    included = client.cfg.get("included_folders") or []
    excluded = client.cfg.get("excluded_folders") or []
    all_ids = {folder["id"] for folder in folders}
    if included:
        roots = {by_title[name] for name in included if name in by_title}
        allowed = folder_descendants(folders, roots)
    else:
        allowed = set(all_ids)
    if excluded:
        roots = {by_title[name] for name in excluded if name in by_title}
        allowed -= folder_descendants(folders, roots)
    return allowed


def command_create(client: JoplinClient, args: argparse.Namespace) -> None:
    folder = client.resolve_folder(args.notebook, create_default=True)
    if folder is None:
        fail(f'Notebook "{args.notebook}" does not exist. Create it explicitly before using it.')
    cfg = client.cfg
    tool = args.tool or cfg.get("default_tool") or cfg.get("default_agent") or detect_tool()
    model = args.model or cfg.get("default_model") or detect_model()
    keywords = ", ".join(parse_keywords(args.keywords))
    if args.note_type not in NOTE_TYPES:
        fail(f"Unsupported note type: {args.note_type}")
    content = read_text(args.body_file)
    metadata = (
        f"**Created:** {local_timestamp()}\n"
        f"**Tool:** {tool}\n"
        f"**Model:** {model}\n"
        f"**Note Type:** {args.note_type}\n"
        f"**Keywords:** {keywords}"
    )
    body = f"# {args.title}\n\n{metadata}\n\n{content}\n"
    note = client.request("POST", "/notes", {"title": args.title, "body": body, "parent_id": folder["id"]})
    print(json.dumps({"id": note.get("id"), "title": args.title, "notebook": args.notebook}, indent=2))


def command_search(client: JoplinClient, args: argparse.Namespace) -> None:
    query = urllib.parse.quote(args.query)
    notes = client.paged(f"/notes?query={query}&fields=id,title,body,parent_id,updated_time")
    allowed = allowed_folder_ids(client)
    folders = {folder["id"]: folder.get("title", "") for folder in client.folders()}
    results = []
    for note in notes:
        if allowed is not None and note.get("parent_id") not in allowed:
            continue
        excerpt = " ".join((note.get("body") or "").split())[:240]
        results.append({
            "id": note.get("id"),
            "title": note.get("title"),
            "notebook": folders.get(note.get("parent_id"), ""),
            "updated_time": note.get("updated_time"),
            "excerpt": excerpt,
        })
        if len(results) >= args.limit:
            break
    print(json.dumps(results, indent=2))


def command_get(client: JoplinClient, args: argparse.Namespace) -> None:
    note = client.request("GET", f"/notes/{urllib.parse.quote(args.id)}?fields=id,title,body,parent_id,updated_time")
    print(json.dumps(note, indent=2))


def command_update(client: JoplinClient, args: argparse.Namespace) -> None:
    body = read_text(args.body_file)
    payload: dict[str, Any] = {"body": body}
    if args.title:
        payload["title"] = args.title
    note = client.request("PUT", f"/notes/{urllib.parse.quote(args.id)}", payload)
    print(json.dumps(note or {"id": args.id, "updated": True}, indent=2))


def command_delete(client: JoplinClient, args: argparse.Namespace) -> None:
    if not args.confirm:
        fail("Deletion requires --confirm")
    client.request("DELETE", f"/notes/{urllib.parse.quote(args.id)}")
    print(json.dumps({"id": args.id, "deleted": True}, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="Create a structured Joplin note")
    create.add_argument("--title", required=True)
    create.add_argument("--body-file", required=True)
    create.add_argument("--notebook", default=DEFAULT_NOTEBOOK)
    create.add_argument("--note-type", required=True, choices=sorted(NOTE_TYPES))
    create.add_argument("--keywords", required=True)
    create.add_argument("--tool")
    create.add_argument("--model")
    create.set_defaults(func=command_create)

    search = subparsers.add_parser("search", help="Search notes")
    search.add_argument("--query", required=True)
    search.add_argument("--limit", type=int, default=5)
    search.set_defaults(func=command_search)

    get = subparsers.add_parser("get", help="Get a note by ID")
    get.add_argument("--id", required=True)
    get.set_defaults(func=command_get)

    update = subparsers.add_parser("update", help="Update a note by ID")
    update.add_argument("--id", required=True)
    update.add_argument("--body-file", required=True)
    update.add_argument("--title")
    update.set_defaults(func=command_update)

    delete = subparsers.add_parser("delete", help="Delete a note by ID")
    delete.add_argument("--id", required=True)
    delete.add_argument("--confirm", action="store_true")
    delete.set_defaults(func=command_delete)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    client = JoplinClient(load_config())
    args.func(client, args)


if __name__ == "__main__":
    main()
