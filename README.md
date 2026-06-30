![God Blocker](https://github.com/user-attachments/assets/d59dfa13-8071-4da6-9723-7c04dedea4b1)

# God Blocker

A Ren'Py visual novel featuring a death-game scenario with AI-powered NPCs that respond dynamically in real time.

Built with **Ren'Py 8.5.3**.

## Running

1. Install the [Ren'Py SDK](https://www.renpy.org/latest.html) (8.5.3+)
2. Open the Ren'Py launcher and add this project
3. Click **Launch Project**

## AI Setup

The game uses **OpenRouter** as the primary AI provider and **Google Gemini** as a direct fallback.

### 1. Get API Keys

- **OpenRouter** (primary): [openrouter.ai/keys](https://openrouter.ai/keys)
- **Gemini** (fallback): [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### 2. Configure Keys

Open `game/ai_integration.rpy` and fill in your keys near the top of the file:

```python
OPENROUTER_API_KEYS = [
    "YOUR_OPENROUTER_KEY_HERE",
]

GEMINI_API_KEYS = [
    "YOUR_GEMINI_KEY_HERE",
]
```

Both lists support multiple keys — the system rotates them on rate limits.

### Models

| Provider | Model |
|----------|-------|
| OpenRouter (primary) | `google/gemini-2.5-flash` |
| Gemini direct (fallback) | `gemini-2.5-flash` → `gemini-2.5-flash-lite` |

These can be changed via `GEMINI_MODEL` and `GEMINI_FALLBACK_MODEL` in `ai_integration.rpy`.

### Other config (ai_integration.rpy)

```python
AI_MAX_TOKENS = 800    # max tokens per response
AI_TEMPERATURE = 0.7   # response creativity
```

## NPCs

Defined in `game/ai_npcs.rpy`

## Files

| File | Purpose |
|------|---------|
| `game/ai_integration.rpy` | Core AI logic, API keys, fallback chain |
| `game/ai_npcs.rpy` | NPC personalities and registration |
| `game/ai_group_chat.rpy` | Group scene AI orchestration |
| `game/ai_screens.rpy` | API stats screen, async helpers |

## Troubleshooting

**No response / timeout** — check your internet connection or try a different API key.

**Wrong provider used** — click **API** in the in-game quick menu (top-right HUD) to see which key is active and its status.

**NPC breaks character** — adjust the system prompt for that NPC in `game/ai_npcs.rpy`.

## Notes

- An active internet connection is required for AI responses
- Conversation history resets when the game closes
- API keys are **not included** — you must supply your own
- All AI dialogue is logged to `game/ai_dialogue_log.txt`
