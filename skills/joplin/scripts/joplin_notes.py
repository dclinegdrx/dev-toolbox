#!/usr/bin/env python3
"""Deterministic Joplin Web Clipper API operations for the Joplin skill.

All operations are hard-scoped to the "Agent Notes" notebook and its
sub-notebooks. Notes outside that scope are never read, created, updated,
or deleted.
"""

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
NOTEBOOK = "Agent Notes"
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
        self._folders: list[dict[str, Any]] | None = None

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

    def folders(self, refresh: bool = False) -> list[dict[str, Any]]:
        if self._folders is None or refresh:
            self._folders = self.paged("/folders?fields=id,title,parent_id")
        return self._folders

    def agent_notes_folder(self, create: bool = False) -> dict[str, Any] | None:
        folder = next((item for item in self.folders() if item.get("title") == NOTEBOOK), None)
        if folder or not create:
            return folder
        created = self.request("POST", "/folders", {"title": NOTEBOOK})
        self.folders(refresh=True)
        return created


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


def scoped_folder_ids(client: JoplinClient) -> set[str]:
    """Folder IDs the skill may touch: Agent Notes and its descendants.

    Configured included_folders/excluded_folders may only narrow this scope,
    never widen it.
    """
    root = client.agent_notes_folder()
    if root is None:
        fail(f'Notebook "{NOTEBOOK}" does not exist. Create a note first to create it.')
    folders = client.folders()
    allowed = folder_descendants(folders, {root["id"]})
    by_title = {folder.get("title"): folder.get("id") for folder in folders}
    included = [name for name in (client.cfg.get("included_folders") or []) if name in by_title]
    if included:
        allowed &= folder_descendants(folders, {by_title[name] for name in included})
    excluded = [name for name in (client.cfg.get("excluded_folders") or []) if name in by_title]
    if excluded:
        allowed -= folder_descendants(folders, {by_title[name] for name in excluded})
    if not allowed:
        fail(
            f'Folder filters in ~/.joplinrc exclude the entire "{NOTEBOOK}" notebook. '
            "Adjust included_folders/excluded_folders."
        )
    return allowed


NOTE_FIELDS = "id,title,body,parent_id,created_time,updated_time"


def fetch_scoped_note(client: JoplinClient, note_id: str) -> dict[str, Any]:
    """Fetch a note by ID, refusing anything outside the Agent Notes scope."""
    note = client.request("GET", f"/notes/{urllib.parse.quote(note_id)}?fields={NOTE_FIELDS}")
    if not note:
        fail(f"Note {note_id} not found")
    if note.get("parent_id") not in scoped_folder_ids(client):
        folders = {folder["id"]: folder.get("title", "") for folder in client.folders()}
        location = folders.get(note.get("parent_id"), "unknown notebook")
        fail(
            f'Note {note_id} is in "{location}", outside the "{NOTEBOOK}" notebook. '
            "This skill only operates inside that notebook."
        )
    return note


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


def metadata_block(client: JoplinClient, args: argparse.Namespace, timestamp: str) -> str:
    cfg = client.cfg
    tool = args.tool or cfg.get("default_tool") or cfg.get("default_agent") or detect_tool()
    model = args.model or cfg.get("default_model") or detect_model()
    keywords = ", ".join(parse_keywords(args.keywords))
    if args.note_type not in NOTE_TYPES:
        fail(f"Unsupported note type: {args.note_type}")
    return (
        f"**Created:** {timestamp}\n"
        f"**Tool:** {tool}\n"
        f"**Model:** {model}\n"
        f"**Note Type:** {args.note_type}\n"
        f"**Keywords:** {keywords}"
    )


def split_title(body: str, fallback_title: str) -> tuple[str, str]:
    """Split a note body into its H1 line and everything after it."""
    lines = body.splitlines()
    for index, line in enumerate(lines):
        if line.strip():
            if line.startswith("# "):
                return line.rstrip(), "\n".join(lines[index + 1 :]).strip()
            break
    return f"# {fallback_title}", body.strip()


def command_create(client: JoplinClient, args: argparse.Namespace) -> None:
    folder = client.agent_notes_folder(create=True)
    if folder is None:
        fail(f'Unable to resolve or create the "{NOTEBOOK}" notebook.')
    metadata = metadata_block(client, args, local_timestamp())
    content = read_text(args.body_file)
    body = f"# {args.title}\n\n{metadata}\n\n{content}\n"
    note = client.request("POST", "/notes", {"title": args.title, "body": body, "parent_id": folder["id"]})
    print(json.dumps({"id": note.get("id"), "title": args.title, "notebook": NOTEBOOK}, indent=2))


def command_search(client: JoplinClient, args: argparse.Namespace) -> None:
    allowed = scoped_folder_ids(client)
    query = urllib.parse.quote(args.query)
    notes = client.paged(f"/notes?query={query}&fields={NOTE_FIELDS}")
    folders = {folder["id"]: folder.get("title", "") for folder in client.folders()}
    results = []
    for note in notes:
        if note.get("parent_id") not in allowed:
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


def command_list(client: JoplinClient, args: argparse.Namespace) -> None:
    allowed = scoped_folder_ids(client)
    folders = {folder["id"]: folder.get("title", "") for folder in client.folders()}
    notes = []
    for folder_id in allowed:
        notes.extend(client.paged(f"/folders/{folder_id}/notes?fields={NOTE_FIELDS}"))
    notes.sort(key=lambda note: note.get("updated_time") or 0, reverse=True)
    results = [
        {
            "id": note.get("id"),
            "title": note.get("title"),
            "notebook": folders.get(note.get("parent_id"), ""),
            "updated_time": note.get("updated_time"),
        }
        for note in notes[: args.limit]
    ]
    print(json.dumps(results, indent=2))


def command_get(client: JoplinClient, args: argparse.Namespace) -> None:
    note = fetch_scoped_note(client, args.id)
    folders = {folder["id"]: folder.get("title", "") for folder in client.folders()}
    note["notebook"] = folders.get(note.get("parent_id"), "")
    print(json.dumps(note, indent=2))


def command_update(client: JoplinClient, args: argparse.Namespace) -> None:
    note = fetch_scoped_note(client, args.id)
    content = read_text(args.body_file)
    timestamp = local_timestamp()
    title_line, existing = split_title(note.get("body") or "", note.get("title") or args.title or "Untitled")

    if args.mode == "replace":
        body = f"{title_line}\n\n{content}\n"
    else:
        metadata = metadata_block(client, args, timestamp)
        section_title = args.section_title or f"Update — {timestamp}"
        entry = f"## {section_title}\n\n{metadata}\n\n{content}"
        body = f"{title_line}\n\n{entry}\n" if not existing else f"{title_line}\n\n{entry}\n\n---\n\n{existing}\n"

    payload: dict[str, Any] = {"body": body}
    if args.title:
        payload["title"] = args.title
    client.request("PUT", f"/notes/{urllib.parse.quote(args.id)}", payload)
    print(json.dumps({
        "id": args.id,
        "title": payload.get("title", note.get("title")),
        "notebook": NOTEBOOK,
        "mode": args.mode,
        "updated": True,
    }, indent=2))


def command_delete(client: JoplinClient, args: argparse.Namespace) -> None:
    note = fetch_scoped_note(client, args.id)
    if not args.confirm:
        fail(f'Deletion of "{note.get("title")}" requires --confirm')
    client.request("DELETE", f"/notes/{urllib.parse.quote(args.id)}")
    print(json.dumps({"id": args.id, "title": note.get("title"), "deleted": True}, indent=2))


def add_metadata_arguments(parser: argparse.ArgumentParser, required: bool) -> None:
    parser.add_argument("--note-type", required=required, choices=sorted(NOTE_TYPES))
    parser.add_argument("--keywords", required=required)
    parser.add_argument("--tool")
    parser.add_argument("--model")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help=f'Create a note in the "{NOTEBOOK}" notebook')
    create.add_argument("--title", required=True)
    create.add_argument("--body-file", required=True)
    add_metadata_arguments(create, required=True)
    create.set_defaults(func=command_create)

    search = subparsers.add_parser("search", help=f'Search notes inside "{NOTEBOOK}"')
    search.add_argument("--query", required=True)
    search.add_argument("--limit", type=int, default=5)
    search.set_defaults(func=command_search)

    listing = subparsers.add_parser("list", help=f'List recent notes inside "{NOTEBOOK}"')
    listing.add_argument("--limit", type=int, default=20)
    listing.set_defaults(func=command_list)

    get = subparsers.add_parser("get", help="Get a note by ID")
    get.add_argument("--id", required=True)
    get.set_defaults(func=command_get)

    update = subparsers.add_parser(
        "update",
        help="Prepend a dated journal section to a note (default) or replace its body",
    )
    update.add_argument("--id", required=True)
    update.add_argument("--body-file", required=True)
    update.add_argument("--title", help="Rename the note (rarely needed)")
    update.add_argument(
        "--mode",
        choices=("append-section", "replace"),
        default="append-section",
        help="append-section prepends a new dated section; replace rewrites the whole body",
    )
    update.add_argument("--section-title", help='Section heading; defaults to "Update — <timestamp>"')
    add_metadata_arguments(update, required=False)
    update.set_defaults(func=command_update)

    delete = subparsers.add_parser("delete", help="Delete a note by ID")
    delete.add_argument("--id", required=True)
    delete.add_argument("--confirm", action="store_true")
    delete.set_defaults(func=command_delete)

    return parser


def validate(args: argparse.Namespace) -> None:
    if args.command == "update" and args.mode == "append-section":
        missing = [name for name in ("note_type", "keywords") if not getattr(args, name)]
        if missing:
            fail(
                "append-section updates require --note-type and --keywords for the new section header"
            )


def main() -> None:
    args = build_parser().parse_args()
    validate(args)
    client = JoplinClient(load_config())
    args.func(client, args)


if __name__ == "__main__":
    main()
