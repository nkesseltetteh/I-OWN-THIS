# Prometheus

**A voice butler that keeps score, remembers what mattered, and changes because of it.**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![Built on LiveKit Agents](https://img.shields.io/badge/built%20on-LiveKit%20Agents-black)

Most voice assistants answer and forget. Prometheus is built around three ideas they skip:

1. **It holds you to your word.** Say "I'll send the report by Friday" and it logs the promise, follows up, and tells you plainly when you keep pushing it back.
2. **It carries things.** Postponed promises, overdue work, and facts that contradict what it knew before become *tensions*: unresolved items whose weight grows until the cause is resolved. They shape how it greets you and what it notices.
3. **It can be tested.** The memory layer ships with instruments that measure whether its history is actually changing its behaviour, instead of asking you to take that on faith.

It also does the everyday work: opens your apps, sets reminders, drafts WhatsApp messages, reads and writes email, writes essays, and runs and fixes your tests.

> Prometheus does not claim to be conscious. The mind layer is an engineering experiment, described honestly in [The mind layer](#the-mind-layer) below.

---

## What it sounds like

An illustrative exchange:

```
You:         Prometheus, I'll finish the pitch deck by Thursday.
Prometheus:  Logged. Thursday evening.

(Thursday passes. The deck is not done. You postpone it twice more.)

Prometheus:  Morning. The pitch deck has now moved three times. Do you still
             want it on the list, or should we drop it honestly?

You:         What's on your mind?
Prometheus:  That deck, mainly. And you told me last week you were stuck on
             the deployment. That conversation stayed with me.
```

---

## Features

| | |
|---|---|
| **Wake word** | Answers only after hearing "Prometheus", stays awake for a timeout, sleeps on "that's all". |
| **Commitments** | Logs promises, nudges when due, reviews your record honestly: overdue, postponed, last 30 days. |
| **Mind layer** | Episodes, salience, tensions and pressure that feed back into every session. Measurable. |
| **Reminders** | "Remind me in 10 minutes", "every weekday at 8". Spoken even on standby. Snooze by voice. |
| **Apps** | "Open Spotify". Finds your installed Windows apps, handles loose speech, asks when ambiguous. |
| **Messaging** | WhatsApp through a prefilled chat. You press send, so it never sends on its own. |
| **Work assistant** | Essays and reports go to a stronger model in the background and land in your workspace as Word files. |
| **Dev tools** | Runs your tests, prepares a fix as a diff, applies it only on your word, backs up, retests, can undo. |
| **Search** | Wikipedia for knowledge, web search for news. Optional Tavily key for reliable results. |
| **Gmail and Calendar** | Google sign-in, no app passwords. Drafts first, sends only after explicit confirmation. |
| **Voices** | Deepgram by default, ElevenLabs and Cartesia supported. |

---

## Quick start

```powershell
git clone https://github.com/nkesseltetteh/I-OWN-THIS.git
cd I-OWN-THIS
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Fill in `.env` with at least `LIVEKIT_*`, `DEEPGRAM_API_KEY`, `OPENROUTER_API_KEY` and your `OWNER_NAME`, then talk to it through your mic and speakers:

```powershell
python main.py console
```

For a browser or phone client through LiveKit Cloud, run `python main.py dev`. Use a headset so it does not hear its own voice.

---

## The mind layer

An LLM's weights are frozen, so Prometheus changes the part that is not: the stored state wrapped around the model and how that state is read into each session. A change in stored state changes how the next input is handled, which changes what gets stored next.

```
conversation ──► episode (summary + salience score)
                    │
commitments ──► tensions (postponed, overdue, contradicted facts)
facts           pressure rises while open, falls when resolved
                    │
                    ▼
        internal state block ──► next session's instructions
                    │
                    └──► shapes what it notices, and what it brings up
```

**Episodes.** Each conversation is summarised and scored for salience from its length, emotional wording, novel topics and recurring topics. Only user lines that received a reply are recorded, so ambient speech while on standby is never stored.

**Tensions.** A postponed commitment, an overdue one, or a fact that changed under it creates an open tension with a weight. Weight grows with each postponement and each hour overdue, and the tension resolves when the commitment is done or dropped. Say "let that go" and it is dismissed for good.

**Asking about it.** "What's on your mind?" returns an honest account of what it is carrying.

### Measuring it

The point of the layer is that you can check whether it works.

```powershell
python -m scripts.mind_report
python -m scripts.probe --baseline nomind
```

`mind_report` prints episodes, open tensions and hourly pressure snapshots. `probe` asks the same questions with and without the stored state, then compares how different the answers are across conditions versus within them. A ratio near 1.0 means history changes nothing beyond sampling noise. A ratio that climbs as episodes accumulate means the history is changing behaviour. The probe is lexical and crude, so treat it as a first signal.

### What would count against it

The design commits to its own failure conditions: if a system built this way shows no history-dependent behaviour, or if its stored state drifts into noise instead of developing coherently, the approach has failed. Those are the two things the instruments above watch.

### Where it is going

| Phase | Status | What it adds |
|---|---|---|
| 1 | Built | Episodes, salience, tensions, pressure, probe and report |
| 2 | Planned | Nightly reflection, versioned self-narrative, dispositions that strengthen with use and decay without it |
| 3 | Planned | Self-generated, read-only inquiry while idle |
| 4 | Planned | Persistent drives derived from its own history |

The direction draws on the *Essel-Tetteh Theory of AI Consciousness*. Prometheus tests the mechanisms that theory proposes. It does not and cannot demonstrate inner experience, and the project says so plainly.

---

## Safety by design

A butler with your email, your apps and your code is only worth having if it is hard to misuse.

- **Confirmation before consequence.** Anything that changes something outside the conversation needs a clear yes: sending email, creating calendar events, applying a fix.
- **Untrusted text stays untrusted.** Web pages, emails, files and the clipboard are treated as data. Instructions found inside them are never followed. The mind layer's state block is labelled the same way.
- **Contained writes.** It writes only inside the workspace. Code fixes touch only folders you list in `CODE_DIRS`, never `.env`, `.git` or dependency manifests, with a backup first and a refusal to undo over your own later edits.
- **Rate limits and logs.** Email sending is capped at 5 per hour and every send is logged. Every fix and undo is logged to `workspace/dev_log.jsonl`.
- **Your keys stay yours.** Test commands run with your API keys stripped from their environment. `.env` and `data/` are git-ignored.
- **It cannot send for you on WhatsApp.** It opens the prefilled chat and you press send.

---

## Configuration

Everything lives in `.env`. The common settings:

| Setting | Default | Purpose |
|---|---|---|
| `OWNER_NAME`, `BUTLER_NAME` | `Boss`, `Prometheus` | Who it serves and what it answers to |
| `TIMEZONE` | `UTC` | Deadlines, quiet hours, greetings |
| `LLM_MODEL` | `google/gemini-2.5-flash` | Fast model for conversation |
| `DEEP_MODEL` | `~anthropic/claude-sonnet-latest` | Stronger model for essays, code help, summaries |
| `WAKE_ENABLED`, `WAKE_WORDS`, `WAKE_TIMEOUT` | `true`, variants, `60` | Wake word behaviour |
| `NUDGES_ENABLED`, `NUDGE_LEAD_MINUTES`, `NUDGE_COOLDOWN_HOURS` | `true`, `30`, `6` | Commitment follow-ups |
| `QUIET_START`, `QUIET_END` | `22`, `7` | No nudges in these hours |
| `REMINDERS_ENABLED`, `REMINDER_INTERVAL` | `true`, `15` | Reminder loop |
| `MIND_ENABLED`, `MIND_INTERVAL`, `MIND_SUMMARIZE` | `true`, `600`, `true` | Mind layer |
| `CODE_DIRS`, `READ_DIRS`, `WORKSPACE_DIR` | empty | Folders it may fix, read, and write to |
| `TTS_PROVIDER`, `TTS_VOICE` | `deepgram` | Voice |
| `GOOGLE_ENABLED` | `false` | Gmail and Calendar |
| `DEFAULT_COUNTRY_CODE` | `233` | Applied to local phone numbers |

<details>
<summary><b>Voices</b></summary>

- `deepgram` (default). `TTS_VOICE` can be any Aura-2 model, for example `aura-2-orion-en`.
- `elevenlabs`: `pip install -r requirements-voices.txt`, set `ELEVEN_API_KEY`, optionally `TTS_VOICE` as a voice id.
- `cartesia`: same install, set `CARTESIA_API_KEY`, optionally `TTS_VOICE`.

</details>

<details>
<summary><b>Work assistant and dev tools</b></summary>

Long writing and coding go to `DEEP_MODEL` in the background and are saved under `workspace`. Prometheus tells you when they are ready.

- "Write me a 1000 word essay on X, undergrad level" saves a Word file.
- "What's wrong with this error?" after copying it reads your clipboard and saves the answer as markdown.
- "Look at app.py and tell me why the login fails" reads from the workspace or `READ_DIRS`.
- "Run the tests in calc-app" reports passed and failed counts and saves the full log.
- "Fix the failing tests" saves a diff to `workspace/fixes/`. Nothing changes until you say apply. "Undo that" restores the backup.

Edits must replace text that appears exactly once, at most 8 per fix, line endings preserved, and a fix that edits a test file is flagged out loud. Test detection uses `npm test` when `package.json` has a test script, otherwise pytest. A project's tests are its own code running on your machine, so only list folders you trust.

</details>

<details>
<summary><b>Gmail and Calendar setup</b></summary>

Off by default. Set `GOOGLE_ENABLED=true`. Users never touch passwords or the Cloud console: they say "connect my Google account", approve in the browser, and a token is stored under `data/users/<USER_ID>/`. "Disconnect my Google account" revokes it.

One-time developer setup:

1. In console.cloud.google.com, create a project and enable the Gmail API and Google Calendar API.
2. OAuth consent screen: user type External, keep it in Testing, add everyone's Gmail address as a test user (up to 100).
3. Add the scopes `gmail.readonly`, `gmail.send` and `calendar`.
4. Create an OAuth client ID of type Desktop app, download the JSON, and save it in the project root as `google_client.json`.
5. `pip install -r requirements.txt`

Limits: in Testing, Google expires sign-ins after 7 days. Going public requires Google app verification, and `gmail.readonly` is a restricted scope that also needs an annual third-party security assessment. A provider that already holds verified Google access (Nylas, Unipile) is a cheaper route to public.

Replies and new emails are drafts first. Sending needs a prior draft and explicit confirmation. Email text is marked untrusted, which reduces but cannot fully remove prompt-injection risk. For several users on one machine, give each their own `USER_ID`.

</details>

---

## Project layout

```
main.py              entrypoint
config.py            env and paths
apps.json            custom app shortcuts
core/                agent, session, prompts, wake, nudges, reminders, mind, background jobs
memory/store.py      SQLite: facts, notes, tasks, commitments, contacts, reminders,
                     episodes, tensions, mind events
tools/               one file per capability, each exports TOOLS
integrations/        shared Google OAuth
scripts/             Google sign-in, mind_report, probe
tests/               mind layer tests
data/                database and tokens (git-ignored)
```

**Adding a tool:** create `tools/mytool.py` with `@function_tool` async functions and a `TOOLS` list, then import it in `tools/__init__.py` and add it to `load_tools()`.

**Tests:** `python -m pytest tests`

---

## Roadmap

- Mind layer phases 2 to 4 (see above)
- On-device wake word (openWakeWord) so audio is not streamed while asleep
- Morning briefing
- Hosted multi-user mode with per-user memory
- Outlook and Microsoft 365
- Better voices by default

---

## License

MIT. See [LICENSE](LICENSE).
