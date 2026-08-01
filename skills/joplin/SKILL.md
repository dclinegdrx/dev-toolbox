---
name: joplin
description: Create, search, update, and delete durable technical and engineering-management notes in Joplin through the Web Clipper REST API. Use when the user asks to capture an AI conversation, technical explanation, debugging investigation, architecture discussion, decision, meeting outcome, implementation plan, product finding, or other reusable knowledge in Joplin, or asks to find, revise, or remove an existing Joplin note. New notes default to the "Agent Notes" notebook and include Created, Tool, Model, Note Type, and Keywords metadata.
---

# Joplin Notes

Create durable, self-contained notes in the user's Joplin instance through the Web Clipper REST API. Use the bundled script for deterministic API operations and apply the content-quality rules below when synthesizing notes.

## Core workflow

1. Determine the requested operation: create, search, read, update, or delete.
2. For create or substantial update operations, identify the most appropriate note type.
3. Synthesize a durable note rather than copying the conversation verbatim.
4. Use `scripts/joplin_notes.py` for Joplin API operations.
5. Report the resulting note title and notebook. Include the note ID when useful.

## Operation rules

### Create

- Always create a new note when the user asks to create or save a note. Do not silently update an existing note.
- Default to the notebook named exactly `Agent Notes` unless the user explicitly names another notebook.
- Create `Agent Notes` if it does not exist.
- Do not silently create an explicitly requested custom notebook. If it does not exist, report that and ask whether it should be created.
- Include the complete metadata header.
- Choose a clear, specific title that will remain meaningful outside the current conversation.
- If a highly similar title already exists, still create the requested note and mention the possible duplicate afterward.

### Search and read

- Search the folders allowed by `included_folders` and `excluded_folders` in `~/.joplinrc`.
- Folder filters apply to searches, not to the destination of newly created notes.
- Return up to five useful matches with title, notebook, updated time, and a short identifying excerpt.
- Use broader or alternate terminology when the first search returns no useful matches.

### Update

- Search for the note using the user's terms and folder filters.
- If multiple plausible matches exist, show the candidates and ask the user to choose.
- Preserve `Created`, `Tool`, and `Model` as original provenance.
- Add or refresh `Updated` after a meaningful content change.
- Regenerate `Note Type` or `Keywords` only when the revised content warrants it.
- Do not silently rewrite confirmed facts as speculation, or speculation as fact.

### Delete

- Identify the best matching note and show its title and notebook.
- Require explicit confirmation before deletion.
- Never delete based only on an ambiguous search result.

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

Every newly created note must begin with this plain metadata block immediately after the H1 title:

```markdown
# Note Title

**Created:** 2026-07-31 19:25:00
**Tool:** Cursor
**Model:** gpt-5
**Note Type:** debugging
**Keywords:** kafka, consumer lag, subscriptions processor, dlq, offsets
```

Use this exact order:

1. `Created`
2. `Tool`
3. `Model`
4. `Note Type`
5. `Keywords`

For updated notes, add `Updated` immediately after `Created`:

```markdown
**Created:** 2026-07-31 19:25:00
**Updated:** 2026-08-04 10:12:00
```

Metadata rules:

- **Created/Updated:** local time as `YYYY-MM-DD HH:MM:SS`, with no timezone suffix.
- **Tool:** the application that created the note, such as Claude Code, Cursor, or OpenCode.
- **Model:** the specific model in use.
- **Note Type:** one lowercase value from the supported note types.
- **Keywords:** 3 to 7 comma-separated lowercase terms, with no trailing punctuation.
- Use detected or configured Tool and Model values verbatim. Never invent a model name.

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
- `included_folders` limits searches to exact folder names and descendants.
- `excluded_folders` excludes exact folder names and descendants.
- If both folder lists are empty, search all folders.

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
python scripts/joplin_notes.py get --id NOTE_ID
python scripts/joplin_notes.py update --id NOTE_ID --body-file /tmp/revised-note.md
python scripts/joplin_notes.py delete --id NOTE_ID --confirm
```

For `create`, the body file should contain only the note content after the metadata block. The script constructs the H1 title and metadata header.

For `update`, provide a complete Markdown body. Preserve provenance metadata according to the update rules before sending it.

## Error handling

- Missing `~/.joplinrc`: tell the user to create it with `auth_token` and optionally `api_uri`.
- Connection refused or timeout: confirm Joplin is open and Web Clipper is enabled.
- HTTP 401/403: refresh the Web Clipper token.
- HTTP 404: verify the note ID or notebook.
- Empty search results: retry with broader terminology before reporting no matches.
- Invalid JSON or malformed API response: report the exact failure without exposing the token.
- Never print or store the authorization token in note content or user-visible output.

## Verification checklist

Before considering an operation complete, verify as applicable:

- `~/.joplinrc` exists and contains a valid `auth_token`.
- The Web Clipper API is reachable.
- The destination notebook is correct.
- New notes contain Created, Tool, Model, Note Type, and 3 to 7 Keywords.
- The note is self-contained and uses the appropriate adaptive structure.
- Facts, hypotheses, assumptions, decisions, and open questions are not conflated.
- Search results respect configured folder filters.
- Update and delete operations target an unambiguous note.
- Delete operations received explicit confirmation.
