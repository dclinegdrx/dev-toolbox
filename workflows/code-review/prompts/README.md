# Code Review Prompts

Place reusable prompts under a language or project directory, then give them a
role-oriented name. This keeps variants discoverable without treating one
project's review rubric as universal.

For example:

```text
prompts/
├── go/
│   └── manager-review.md
└── <language-or-project>/
    └── <review-role>.md
```

Prompts should state their required context, distinguish new findings from
existing review feedback, and produce drafts rather than modifying a pull
request. See the [Go manager review](go/manager-review.md) and the
[workflow README](../README.md) for usage.
