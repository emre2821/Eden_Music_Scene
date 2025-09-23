# Emotion Tag Schema Guide

The emotion tag payload travels between EchoSplit (creation), EchoDJ (curation),
and EchoPlay (listening). The JSON schema lives in
[`emotion_tag_schema.json`](../emotion_tag_schema.json); this guide translates it
into conversational language with examples.

## Field reference

| Field      | Required | Type    | Range / Format         | Notes |
|------------|----------|---------|------------------------|-------|
| `id`       | No       | string  | UUID or custom slug    | Omit to let the service auto-generate a UUID. |
| `track_id` | **Yes**  | string  | Non-empty              | Connects the tag to a specific asset. Mirrors EchoSplit exports. |
| `user_id`  | No       | string  | Non-empty              | Who created the tag. Trimmed automatically. |
| `emotion`  | **Yes**  | string  | Non-empty              | Primary feeling word (e.g. `serenity`, `rage-spark`). |
| `intensity`| No       | number  | 0.0 – 1.0              | Normalized strength. Fractions welcome (`0.42`). |
| `notes`    | No       | string  | Free text              | Optional prose, prompts, or agent commentary. |

### Validation rules applied by `emotion_service.py`

* Unknown fields are rejected.
* `track_id`, `emotion`, `id`, and `user_id` (when provided) must be strings and
  are trimmed of surrounding whitespace.
* `intensity` must be numeric (int/float) and fall within the inclusive
  `[0, 1]` range.
* `notes` accept any string. Leading/trailing whitespace is stripped.

## Example payloads

### Minimal tag

```json
{
  "track_id": "eden-aurora-001",
  "emotion": "wonder"
}
```

### Full tag authored by an agent

```json
{
  "id": "aurora-001-serenity",
  "track_id": "eden-aurora-001",
  "user_id": "dj-voltage",
  "emotion": "serenity",
  "intensity": 0.82,
  "notes": "Play at dawn rituals; calms turbulent heartlines."
}
```

### Invalid examples (and why)

| Payload snippet                                        | Rejection reason                                    |
|--------------------------------------------------------|------------------------------------------------------|
| `{ "track_id": 42, "emotion": "joy" }`               | `track_id` must be a string.                         |
| `{ "track_id": "eden-1", "emotion": "joy", "extra": 1 }` | Unknown field `extra`.                               |
| `{ "track_id": "eden-1", "emotion": "joy", "intensity": 2 }` | `intensity` must be between 0 and 1 inclusive.       |

## Authoring tips

1. Use lowercase `emotion` names for consistency.
2. When modeling compound feelings, hyphenate (`grief-dawn`, `rage-spark`).
3. Pair intensity with `notes` to explain context (“0.3 because it's a gentle
   reprise”).
4. If multiple agents collaborate on a tag, encode the primary author in
   `user_id` and cite collaborators in `notes`.

## Testing your payloads

Send a POST request to the local service after starting `emotion_service.py`:

```bash
curl -X POST http://127.0.0.1:8000/tags \
  -H 'Content-Type: application/json' \
  -d '{
        "track_id": "eden-aurora-001",
        "emotion": "serenity",
        "intensity": 0.6
      }'
```

You should receive a `201` response with a generated `id`. Validate your payload
before automation or ingestion scripts rely on it.
