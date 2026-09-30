# Code Review Prompts

Place reusable prompts under a language, project, or `shared` directory, then
give them a role-oriented name. This keeps variants discoverable without
treating one project's review rubric as universal.

For example:

```text
prompts/
├── <language-or-project>/
│   └── manager-review.md
└── shared/
    └── follow-up-review.md
```

Prompts should state their required context, distinguish new findings from
existing review feedback, and produce drafts rather than modifying a pull
request. The `shared/` directory is for prompts that apply across repositories;
the [follow-up review](shared/follow-up-review.md) is its first example. See
the [workflow README](../README.md) for the full prompt catalog and usage.
