---
name: joplin
description: Create, search, update, and delete durable technical and engineering-management notes in Joplin through the Web Clipper REST API. Use when the user asks to capture an AI conversation, technical explanation, debugging investigation, architecture discussion, decision, meeting outcome, implementation plan, product finding, or other reusable knowledge in Joplin, or asks to find, revise, or remove an existing Joplin note. All operations are restricted to the "Agent Notes" notebook. Notes are journals: creates start a note, updates prepend a new dated section with Created, Tool, Model, Note Type, and Keywords metadata.
---

# Joplin Notes

Create durable, self-contained notes in the user's Joplin instance through the Web Clipper REST API. Use the bundled script for deterministic API operations and apply the content-quality rules below when synthesizing notes.

## Notebook scope

This skill operates only inside the notebook named exactly `Agent Notes` and its sub-notebooks.

- Create, read, search, update, and delete are all limited to that scope.
- Never create, modify, or delete a note in any other notebook, even when the user names one. If the user asks for another notebook, explain that this skill is scoped to `Agent Notes` and offer to proceed there.
- Never read or report notes from other notebooks. If a search turns up nothing, the answer is that `Agent Notes` contains no match, not that the note does not exist in Joplin.
- Create `Agent Notes` if it does not exist. Never create other notebooks.
- `scripts/joplin_notes.py` enforces this: there is no notebook argument, and `get`, `update`, and `delete` refuse any note ID outside the scope.

## Note model: notes are journals

A note is a topic or concept that accumulates entries over time.

- The note title is the topic. It stays stable.
- Creating a note starts the journal with its first entry.
- Updating a note prepends a new dated section at the top, directly under the H1 title, each with its own full metadata header. Older entries stay below, unmodified, separated by a `---` rule.
- The note therefore reads newest-first, and every entry carries its own provenance.

## Core workflow

1. Determine the requested operation: create, search, read, update, or delete.
2. For create or update operations, identify the most appropriate note type.
3. Synthesize a durable note or entry rather than copying the conversation verbatim.
4. Use `scripts/joplin_notes.py` for Joplin API operations.
5. Report the resulting note title and notebook. Include the note ID when useful.

## Operation rules

### Create

- Create a new note when the user asks to create or save a note about a new topic. Do not silently update an existing note.
- When the user asks to save something that clearly belongs to an existing `Agent Notes` topic, say so and offer to add it as a new entry on that note instead.
- Include the complete metadata header.
- Choose a clear, specific title that will remain meaningful outside the current conversation and broad enough to accept future entries on the same topic.
- If a highly similar title already exists, still create the requested note and mention the possible duplicate afterward.

### Search and read

- Search only within `Agent Notes`. `included_folders` and `excluded_folders` in `~/.joplinrc` may narrow that scope further, never widen it.
- Return up to five useful matches with title, notebook, updated time, and a short identifying excerpt.
- Use broader or alternate terminology when the first search returns no useful matches.
- Use `list` to show recent notes when the user does not have search terms.

### Update

- Search `Agent Notes` for the note using the user's terms.
- If multiple plausible matches exist, show the candidates and ask the user to choose. If nothing matches, ask whether to create a new note instead of guessing.
- Default to `--mode append-section`: write only the new material to the body file. The script prepends it as a new section with a fresh metadata header and preserves the entire existing body below.
- Do not restate or duplicate content already present in earlier entries. Reference it instead, and state explicitly when the new entry supersedes or contradicts an earlier one.
- Each entry's `Created`, `Tool`, and `Model` reflect that entry's own provenance. Never edit the metadata of earlier entries.
- Choose `Note Type` and `Keywords` for the new entry's content, not for the note as a whole.
- Use `--mode replace` only when the user explicitly asks to rewrite, restructure, or correct the whole note. It discards the journal history below the title, so confirm with the user first.
- Do not silently rewrite confirmed facts as speculation, or speculation as fact.

### Delete

- Identify the best matching note within `Agent Notes` and show its title and notebook.
- Require explicit confirmation before deletion.
- Never delete based only on an ambiguous search result.
- To remove a single journal entry rather than the note, use `--mode replace` on an update after confirming the intended result with the user.

## Note content quality

Create a durable reference note, not a transcript.

The note must:

1. Be understandable without access to the original conversation.
2. Explain the topic for a technically experienced engineering manager who may not be deeply familiar with the specific technology.
3. Preserve enough technical detail to support future implementation, debugging, decision-making, or communication with engineers.
4. Explain why the topic matters to the user's system, team, product, or current work when that context is available.
5. Clearly distinguish confirmed facts, hypotheses, assumptions, decisions, and unresolved questions.
6. Preserve exact technical names, identifiers, commands, errors, APIs, services, events, repositories, configuration values, calculations, and links when useful.
7. Resolve vague references such as “this service,” “the issue,” or “what we discussed” into specific names when the context supports it.
8. Remove conversational filler, repetition, false starts, and irrelevant tangents.
9. Avoid inventing missing facts or silently resolving contradictions.
10. Prefer concise paragraphs, descriptive headings, and focused bullets.
11. Omit empty or unnecessary sections.

Use the full names of important systems, services, projects, vendors, and technologies at least once. Include common abbreviations in parentheses when useful. Write searchable language rather than relying on pronouns or conversation-relative phrasing.

## Note types

Infer the most appropriate type unless the user specifies one:

- `technical-explanation`: explains a concept, system behavior, or technology
- `debugging`: captures a problem, evidence, theories, experiments, and resolution
- `decision`: records a decision, rationale, tradeoffs, and consequences
- `investigation`: captures research, findings, evidence, and unresolved questions
- `architecture`: documents components, interactions, data flow, and constraints
- `meeting-summary`: records material discussion, conclusions, and action items
- `implementation-plan`: captures scope, approach, dependencies, risks, and steps
- `reference`: stores commands, procedures, configuration, or reusable facts

Consult `references/note-patterns.md` for recommended structures. Select the smallest structure that fully captures the material.

## Metadata header

Every note entry carries the same plain metadata block. A newly created note places it immediately after the H1 title:

```markdown
# Note Title

**Created:** 2026-07-31 19:25:00
**Tool:** Cursor
**Model:** gpt-5
**Note Type:** debugging
**Keywords:** kafka, consumer lag, subscriptions processor, dlq, offsets

Initial content.
```

Use this exact order:

1. `Created`
2. `Tool`
3. `Model`
4. `Note Type`
5. `Keywords`

An update prepends a new H2 section with its own identical header, leaving the previous entries untouched below a `---` rule:

```markdown
# Note Title

## Update — 2026-08-04 10:12:00

**Created:** 2026-08-04 10:12:00
**Tool:** Claude Code
**Model:** claude-opus-5
**Note Type:** debugging
**Keywords:** kafka, offsets, catch-up rate, mirrormaker

New material only.

---

**Created:** 2026-07-31 19:25:00
**Tool:** Cursor
**Model:** gpt-5
**Note Type:** debugging
**Keywords:** kafka, consumer lag, subscriptions processor, dlq, offsets

Initial content.
```

There is no `Updated` field. Each entry's `Created` is its own timestamp, so the note's history is the sequence of entry headers.

Metadata rules:

- **Created:** local time as `YYYY-MM-DD HH:MM:SS`, with no timezone suffix.
- **Tool:** the application that created the note, such as Claude Code, Cursor, or OpenCode.
- **Model:** the specific model in use.
- **Note Type:** one lowercase value from the supported note types.
- **Keywords:** 3 to 7 comma-separated lowercase terms, with no trailing punctuation.
- Use detected or configured Tool and Model values verbatim. Never invent a model name.
- Pass `--tool` and `--model` explicitly when you know your own tool and model ID. Environment detection often yields `unknown` for Model because the model variables are usually unset.

### Keyword guidance

- Prefer concrete technical terms, service names, protocols, vendors, projects, and operational concepts.
- Include product or engineering-management terms when relevant, such as `incident`, `decision`, `migration`, `oncall`, `roadmap`, or `sprint`.
- Use terms a colleague would realistically search for.
- Avoid filler terms such as `notes`, `general`, `discussion`, or `information`.
- Cover meaningful subtopics, not only the title. Aim for approximately five keywords when appropriate.

## Tool and model detection

Apply this precedence:

1. Explicit values passed to the script.
2. `default_tool` and `default_model` in `~/.joplinrc`.
3. Backward-compatible `default_agent` for Tool only.
4. Environment detection:
   - Tool: `CLAUDE_CODE_ENTRYPOINT` → `Claude Code`; `CURSOR_TRACE_ID` → `Cursor`; any `OPENCODE_` variable → `OpenCode`.
   - Model: `ANTHROPIC_MODEL`, then `OPENAI_MODEL`, then `CURSOR_MODEL`, then `OPENCODE_MODEL`.
5. Fallback to `unknown`.

## Configuration

Read `~/.joplinrc` as JSON:

```json
{
  "auth_token": "your-api-token-here",
  "api_uri": "http://localhost:41184",
  "default_tool": "Cursor",
  "default_model": "gpt-5",
  "included_folders": [],
  "excluded_folders": []
}
```

- `auth_token` is required.
- `api_uri` defaults to `http://localhost:41184`.
- `default_tool` and `default_model` are optional overrides.
- `default_agent` remains supported as an alias for `default_tool`.
- `included_folders` and `excluded_folders` can only narrow the `Agent Notes` scope, by exact folder name and descendants. They cannot grant access to other notebooks.
- If both folder lists are empty, the scope is all of `Agent Notes`.

## Script usage

Use `scripts/joplin_notes.py`. Run `python scripts/joplin_notes.py --help` for all options.

Examples:

```bash
python scripts/joplin_notes.py create \
  --title "Kafka Consumer Lag Catch-up Estimate" \
  --body-file /tmp/joplin-note.md \
  --note-type debugging \
  --keywords "kafka, consumer lag, offsets, dlq, subscriptions processor"

python scripts/joplin_notes.py search --query "kafka consumer lag"
python scripts/joplin_notes.py list --limit 20
python scripts/joplin_notes.py get --id NOTE_ID

# Journal update: prepends a new dated section with its own metadata header
python scripts/joplin_notes.py update \
  --id NOTE_ID \
  --body-file /tmp/joplin-entry.md \
  --note-type debugging \
  --keywords "kafka, offsets, catch-up rate, mirrormaker"

# Full rewrite, only on explicit user request
python scripts/joplin_notes.py update --id NOTE_ID --mode replace --body-file /tmp/rewritten-note.md

python scripts/joplin_notes.py delete --id NOTE_ID --confirm
```

There is no notebook argument. Every command targets `Agent Notes`.

For `create`, the body file should contain only the note content after the metadata block. The script constructs the H1 title and metadata header.

For `update` in the default `append-section` mode, the body file should contain only the new material, without an H1 or metadata block. The script builds the section heading and metadata header and prepends the section beneath the existing H1 title. `--note-type` and `--keywords` are required in this mode. Pass `--section-title` to override the default `Update — <timestamp>` heading with something more descriptive.

For `update --mode replace`, provide the complete Markdown body without the H1 title; the script preserves the existing title line.

## Error handling

- Missing `~/.joplinrc`: tell the user to create it with `auth_token` and optionally `api_uri`.
- Connection refused or timeout: confirm Joplin is open and Web Clipper is enabled.
- HTTP 401/403: refresh the Web Clipper token.
- HTTP 404: verify the note ID.
- "outside the Agent Notes notebook": the note is out of scope. Do not work around this by editing the script or calling the API directly. Tell the user the note is outside `Agent Notes` and stop.
- Empty search results: retry with broader terminology before reporting no matches.
- Invalid JSON or malformed API response: report the exact failure without exposing the token.
- Never print or store the authorization token in note content or user-visible output.

## Verification checklist

Before considering an operation complete, verify as applicable:

- `~/.joplinrc` exists and contains a valid `auth_token`.
- The Web Clipper API is reachable.
- Every read, create, update, and delete stayed inside `Agent Notes`.
- New notes and new journal entries each contain Created, Tool, Model, Note Type, and 3 to 7 Keywords.
- Updates added a section at the top and left all earlier entries intact.
- `--mode replace` was used only after explicit user confirmation.
- The note is self-contained and uses the appropriate adaptive structure.
- Facts, hypotheses, assumptions, decisions, and open questions are not conflated.
- Update and delete operations target an unambiguous note.
- Delete operations received explicit confirmation.
