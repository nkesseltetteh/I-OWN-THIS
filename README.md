# Prometheus

Personal voice butler built on LiveKit Agents.

## Layout

```
main.py              entrypoint
config.py            env + paths (no hardcoded absolute paths)
apps.json            apps the butler is allowed to open
core/                butler.py (agent), session.py (STT/LLM/TTS), prompts.py, wake.py, nudges.py, timeutil.py
memory/store.py      SQLite: facts, notes, tasks
tools/               one file per capability, each exports TOOLS
integrations/        shared Google OAuth (tokens, refresh, revoke)
scripts/             one-off helpers (Google sign-in)
data/                database and tokens (git-ignored)
```

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Fill in `.env`, then talk to it through your mic and speakers:

```powershell
python main.py console
```

For a browser/phone client via LiveKit Cloud: `python main.py dev`.

## Wake word

On by default. Prometheus only answers after hearing "Prometheus" (or a listed variant), then stays awake for `WAKE_TIMEOUT` seconds after each exchange. Say "that's all" or "go to sleep" to put it on standby. Tune it in `.env`:

```
WAKE_ENABLED=true
WAKE_WORDS=prometheus,promethius,prometheous
WAKE_TIMEOUT=60
```

This works on the speech transcript, so audio streams to Deepgram while the program runs. Use a headset so Prometheus does not hear its own voice. Set `WAKE_ENABLED=false` to talk without a wake word.

## Opening apps

"Open Spotify", "open WhatsApp", "open Word". On Windows, Prometheus finds your installed apps by itself (Start menu apps, including Microsoft Store ones), understands loose speech ("what's app", "spotfy"), and asks which one when several match. `apps.json` still works as a list of custom shortcuts, and wins if a name appears in both.

## Messaging

WhatsApp, through a prefilled chat. "Message Kofi that I'm running late" opens WhatsApp to Kofi with the text typed in, and you press send. Prometheus cannot send for you, because WhatsApp offers no safe way to do that for personal accounts.

- "Save Kofi's number, 0244 123 456" stores a contact. Numbers starting with 0 get your `DEFAULT_COUNTRY_CODE` (233 for Ghana). You can also say a number directly.
- If it wrote the message itself, it reads it back and waits for a yes before opening the chat.

## Reminders

"Remind me in 10 minutes to call Ama", "remind me at 3pm to send the report", "remind me every weekday at 8 to stand up".

- Spoken aloud when due, even in quiet hours and even on standby. After it speaks, you can answer without the wake word ("snooze 15 minutes").
- Repeats: daily, weekdays, weekly. "What reminders do I have?" and "cancel the Ama reminder" work too.
- Reminders due while Prometheus was off fire as soon as it starts, marked as late.
- Reminders only speak while Prometheus is running. Settings: `REMINDERS_ENABLED`, `REMINDER_INTERVAL`.
- Reminders are lightweight time triggers. For promises you want to be held accountable for, use commitments below.

## Commitments

Prometheus logs what you promise ("I'll finish the report by Friday"), keeps score, and follows up honestly.

- Say what you plan to do and it records it, with a deadline if you give one.
- At startup it mentions anything overdue or due within a day.
- While running it speaks up when something is due within 30 minutes or overdue, only when you are not mid-conversation, never in quiet hours, and at most once per item every 6 hours.
- Ask "how am I doing on my promises?" for an honest review: overdue items, repeated postponements, and your last 30 days.

Tune it in `.env`: `NUDGES_ENABLED`, `NUDGE_LEAD_MINUTES`, `NUDGE_COOLDOWN_HOURS`, `QUIET_START`, `QUIET_END`. Times use `TIMEZONE`.

## Work assistant

Long writing and coding are delegated to a stronger model in the background, and the result is saved to the `workspace` folder. Prometheus tells you when it is ready.

- "Write me a 1000 word essay on X, undergrad level" saves a Word file.
- "What's wrong with this error?" after copying it reads your clipboard and saves the fix as a markdown file.
- "Look at app.py and tell me why the login fails" reads a file from the workspace or a folder you allowed.
- "Open the essay" opens it in Word. "Copy that to my clipboard" puts text on the clipboard.

`.env` options: `DEEP_MODEL` (default `~anthropic/claude-sonnet-latest`, set a cheaper one if you like), `DEEP_MAX_TOKENS`, `WORKSPACE_DIR`, and `READ_DIRS` (project folders it may read, separated by semicolons).

Safety: it can only write inside the workspace, only read the workspace and `READ_DIRS`, never runs code, and treats file and clipboard text as untrusted.

## Running tests and applying fixes

Point `CODE_DIRS` in `.env` at the folders that hold your projects (semicolon separated). Prometheus can then:

- "Run the tests in calc-app" runs them in the background and reports passed and failed counts. The full log is saved in the workspace.
- "Fix the failing tests" prepares a fix and saves the diff as `workspace/fixes/fix-<id>.md`. Nothing changes yet.
- "Explain it" or "apply it": it applies the fix only after you clearly say so, backs up every file first, reruns the tests, and reports before and after.
- "Undo that" restores the backup. It refuses if you edited the file yourself since, so your own work is never overwritten.

Safeguards: only projects inside `CODE_DIRS` are touched; edits must replace text that appears exactly once; `.env`, `.git`, `node_modules`, `package.json`, `setup.py`, `pyproject.toml` and non-code files are never edited; at most 8 edits per fix; line endings are preserved; test commands run with your API keys removed from their environment; a fix that edits a test file is flagged out loud. Every apply and undo is logged to `workspace/dev_log.jsonl`.

Test detection: `npm test` if `package.json` has a test script, otherwise pytest. A project's tests are its own code running on your machine, so only list folders you trust.

## Search

- `wikipedia_lookup` handles history, science, people and places. It needs no key and returns clean encyclopedia text.
- `web_search` handles news and recent information. By default it uses the free DuckDuckGo scraper with results filtered for relevance, since it can return ads. For reliable results, add a free `TAVILY_API_KEY` (tavily.com) to `.env` and it is used automatically.

## Voices

Set `TTS_PROVIDER` in `.env`:

- `deepgram` (default). `TTS_VOICE` can be any Aura-2 model name, e.g. `aura-2-orion-en`.
- `elevenlabs`: `pip install -r requirements-voices.txt`, set `ELEVEN_API_KEY`, optionally `TTS_VOICE` as an ElevenLabs voice id.
- `cartesia`: same install, set `CARTESIA_API_KEY`, optionally `TTS_VOICE` as a Cartesia voice id.

## Gmail and Calendar (Google sign-in, no app passwords)

Off by default. Set `GOOGLE_ENABLED=true` in `.env` to turn it on.

Users never touch passwords or the Google Cloud console. They say "connect my Google account", approve access in the browser, and a token is saved under `data/users/<USER_ID>/`. Say "disconnect my Google account" to revoke it.

### One-time setup for you (the developer)

1. console.cloud.google.com: create a project, then enable the **Gmail API** and **Google Calendar API**.
2. OAuth consent screen: user type **External**, keep it in **Testing**, and add the Gmail addresses of everyone who will use it as **test users** (up to 100).
3. Add the scopes `gmail.readonly`, `gmail.send` and `calendar`.
4. Credentials: create an **OAuth client ID** of type **Desktop app**, download the JSON, and save it in the project root as `google_client.json`. Ship this file with the app.
5. `pip install -r requirements.txt`

### Limits to know about

- In Testing, Google expires sign-ins after 7 days, so users reconnect weekly.
- Going public means Google app verification. Reading email (`gmail.readonly`) is a restricted scope, which also needs an annual third-party security assessment (CASA). `gmail.send` is sensitive: verification, no assessment. Google's Limited Use policy also governs sending email content to AI providers.
- A cheaper route to public is a provider that already holds verified Google access (Nylas, Unipile and similar), at a monthly cost.

### Safety

- Replies and new emails are drafts first. Sending needs a prior draft and explicit confirmation, is capped at 5 per hour, and every send is logged to `sent_log.jsonl`.
- Email text is marked untrusted before the model sees it. This reduces, but cannot fully remove, prompt-injection risk.

For several users on one machine, give each their own `USER_ID` in `.env`.

## Adding a tool

1. Create `tools/mytool.py` with `@function_tool` async functions and a `TOOLS` list.
2. Import it in `tools/__init__.py` and add it to `load_tools()`.

## Roadmap

- On-device wake word (openWakeWord) so audio is not streamed while asleep
- Reminders and a morning briefing (scheduler)
- Hosted multi-user mode (web OAuth redirect, per-user memory database)
- Outlook / Microsoft 365 support
- Better TTS voice (Cartesia / ElevenLabs)

## Mind layer (phase 1)

Prometheus keeps a persistent internal state that changes how it handles the next conversation.

- Episodes: each conversation is summarised and scored for salience (length, emotional words, novel topics, recurring topics). Only user lines that got a reply are recorded, so ambient speech while on standby is not kept.
- Tensions: unresolved gaps that build pressure over time. Postponed commitments, overdue commitments, and facts that contradict an earlier value. Pressure rises while they stay open and they resolve when the cause does. "Let that go" dismisses one for good.
- The top tensions and most salient recent conversations are injected into the instructions each session. Ask "what's on your mind?" for the spoken version.

```
MIND_ENABLED=true
MIND_INTERVAL=600
MIND_SUMMARIZE=true
```

Measure it:

```powershell
python -m scripts.mind_report
python -m scripts.probe --baseline nomind
```

`probe` asks the same questions with and without the stored state and compares the answers. The ratio of between-condition to within-condition difference should climb above 1.0 as history accumulates. If it stays near 1.0 the state is not changing behaviour. Run the tests with `python -m pytest tests`.
