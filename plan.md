# CODE-02 v5 — Ultron Build Plan

> **Goal:** Make CODE-02 a local AI that can understand you, do tasks on your computer, and run on more than one machine if needed. Started from Stanford's **OpenJarvis** (Apache-2.0), runs with **LM Studio** on your RTX GPU.

> **In simple words:** Jarvis helps. Ultron helps + can act on its own when you allow it, remember things, and work across devices.

---

## 1. What is CODE-02? (Simple)

*   **CODE-02 v4 (current):** Python system at `core/` (~10k lines). Can detect OS, run shell commands, install packages, check URLs/ports for safety, classify intent. Two main loops `core/smart_ai/` and `core/unified/` do the same job — needs cleanup.
*   **CODE-02 v5 (new):** Fork of OpenJarvis at `CODE-02-v5-ultron/` → add our CODE-02 skills + voice + memory + optional mesh. Local-first, RTX accelerated.

**Current status (27 Aug 2026 - Phase 3 done):**
*   Fork cloned: `CODE-02-v5-ultron/` exists, `.venv/` installed, `uv.lock` present
*   LM Studio alive: `nvidia/nemotron-3-nano-4b` on `localhost:1234` (RTX 5050 8GB, 5GB used)
*   Headless API: `ultron_api.py` on `127.0.0.1:8000` — `/health` OK, `/chat` proxies to LM Studio, `/code02/*` wraps security/system tools
*   Voice: `voice_pipeline.py` (faster-whisper + espeak) + `voice_roundtrip.py` — TTS via espeak works, STT code ready (tiny model needs cache download, mock works for demo)
*   One reference cloned: `references/NVIDIA-Nemotron-3-Super/` (MIT)
*   Legacy `core/` untouched — reusable

---

## 2. Decisions Made

| # | Decision | Choice | Why |
|---|---|---|---|
| 1 | Base | Fork **OpenJarvis** (Stanford, Apache-2.0, Python) | Mature, Python, local-first, 8 agents already |
| 2 | LLM engine | **LM Studio** at `localhost:1234` | Runs on RTX GPU, OpenAI-compatible API. Fallback to Ollama/cloud later |
| 3 | Hardware | **NVIDIA RTX GPU** (local) | For fast STT + LLM. Must work even without GPU (CPU fallback) |
| 4 | Architecture | **Single machine first, mesh later** | Don't build mesh until single node works |
| 5 | Interfaces | **CLI + Chat first**, then Voice + Web + API | Voice/mesh are Phase 3, not Phase 1 |
| 6 | Safety | **SAFE_MODE default** | Dangerous actions need explicit permission |
| 7 | Modes | `SAFE_MODE` \| `RESEARCH_MODE` \| `FULL_AUTONOMY` (opt-in) | `FULL_AUTONOMY` only after red-team tests |
| 8 | Dangerous features | Off by default: `self_modify`, `deploy_code`, `network_scan`, `persist_across_reboots` | Prevent runaway actions |
| 9 | Legacy code | Keep `/home/manoj/Projects/Code-02/core/` as reference | Port only what's useful |

**Why OpenJarvis?**
*   Python-first (matches your stack)
*   Apache-2.0 — you can rename/rebrand but must keep LICENSE/NOTICE
*   Built-in engines: Ollama / LM Studio / vLLM + skills from OpenClaw (~13k) + Hermes (~150)

---

## 3. Phases — Simple and Sequential

### Phase 1 — Get the Fork Running (Do this first)

**Purpose:** Chat with the AI through LM Studio. No mesh, no voice yet.

Steps:
1.  Already done: `git clone https://github.com/open-jarvis/OpenJarvis.git CODE-02-v5-ultron`
2.  Install: `cd CODE-02-v5-ultron && uv sync` (skip Ollama install)
3.  Start LM Studio: Open LM Studio → Developer tab → Start Server → Load a model in **Server** tab (Chat tab alone doesn't work)
4.  Check LM Studio is alive: `curl http://localhost:1234/v1/models`
5.  Check OpenJarvis: `uv run jarvis doctor` and `uv run jarvis --help`
6.  Chat test: `uv run jarvis` (preset `chat-simple`)

**Done when:**
*   `curl http://localhost:1234/v1/models` returns a model list
*   `uv run jarvis doctor` shows engine connected
*   You can chat with the AI via LM Studio

> Note: binary is still `jarvis` (from `pyproject.toml:190`). Renaming to `ultron` is optional later.

---

### Phase 2 — Add CODE-02 Skills (Make it useful)

**Purpose:** Bring the best parts of old CODE-02 into the new fork as skills.

| Old module | New skill | What it does |
|---|---|---|
| `core/cybersecurity/` | `security` skill | Check command safety, URL safety, port scan (defensive only) |
| `core/automation/` + `core/installer/` | `system-control` skill | Run `bash`/`PowerShell`, detect `pacman`/`apt`/`pip`/`winget` and install |
| `core/datascience/` | helper for router | Classify intent `install` vs `security` vs `chat` |
| `core/smart_ai/` + `core/unified/` | **Merge into one** | Keep only one main loop (delete duplicate) |

Steps:
1.  Create skill folders under `src/openjarvis/skills/` (follow `agentskills.io` format — copy an existing skill as template)
2.  Each skill must call `check_command_safety()` before running shell commands
3.  Test: `uv run jarvis ask "install htop"` → actually installs. `uv run jarvis ask "scan 192.168.1.1 port 80"` → returns open/closed.

**Simple safety rules:**
*   Block: `rm -rf /`, fork bombs, `curl | bash` from unknown URLs
*   Block external network scans (only allow `127.0.0.1` / `192.168.x.x` by default)
*   Every shell action is logged

**Done when:**
*   `"install htop"` and `"scan this machine"` work through skills
*   Dangerous command like `"rm -rf /"` is blocked and logged

---

### Phase 3 — Voice + Headless API (Optional, after Phase 2)

**Purpose:** Talk hands-free. Let other apps/machines call the AI.

| Part | Library | Status | Notes |
|---|---|---|---|
| Speech-to-text | `faster-whisper` (tiny, cpu) via `uv sync --extra desktop` | Code ready, model needs cache | `voice_pipeline.py` loads tiny (75MB) on first run — mock used for fast demo |
| Wake word | `openWakeWord` | Future | Start with `hey_jarvis`, retrain to `hey_ultron` later |
| Text-to-speech | `espeak` (offline) + `espeak -w` | DONE | `voice_pipeline.py::tts_espeak()` works (54K wav), `Piper`/`edge-tts` later |
| API | `FastAPI` via `ultron_api.py` | DONE | Lightweight gateway, not OpenJarvis heavy `serve` (which hangs on startup) |

Flow: `text → espeak wav → whisper (tiny) → LM Studio (1234) → skill → espeak wav`
Test: `python voice_roundtrip.py "hello ultron what is 2 plus 2"` → TTS 123K wav → STT(mock) → LM("4") → TTS 247K wav — PASS

API: `ultron_api.py` on `127.0.0.1:8000`:
*   `GET /health` → `{"status":"ok","lmstudio_alive":true, ...}` — PASS
*   `POST /chat` → proxies to `localhost:1234/v1/chat/completions` — PASS (tested `2+2` → `4`)
*   `POST /code02/security` + `/code02/system` → wrap `code02_security`/`code02_system` tools — PASS
*   `GET /` + `/docs` → info

Extra for mesh (only if you need 2 machines):
*   Event bus: `nats-py` via `uv sync --extra mesh` (`pyproject.toml:160`)
*   Use NATS for message passing, gRPC later if needed — not both at once
*   Start with 1 primary + 1 worker, static IP in `configs/openjarvis.toml`

**Install size warning:** CUDA torch ~2.5GB, whisper models 0.5-3GB.

**Done when:**
*   `curl http://localhost:8000/health` returns OK — DONE
*   `python voice_roundtrip.py` → spoken answer via espeak + LM Studio — DONE (mock STT, real STT after tiny cached)

---

### Phase 4 — Memory + Polish (Last)

**Purpose:** Remember past chats, prove it works, prepare release.

Steps:
1.  **References:** Keep `references/` gitignored. Currently only `NVIDIA-Nemotron-3-Super` cloned — add others only when needed. Document each in `references/NOTES.md` (what you borrowed, not copied — especially `worldmonitor` is AGPL-3.0, never copy code, use its MCP at `https://worldmonitor.app/mcp`).
2.  **Memory:** Start simple — OpenJarvis already has file-based memory. Add `mem0` / `Kuzu` later only if needed.
3.  **Prompt tuning (optional):** Use Nemotron's 12 prompt templates and token budgets: simple question → 0 thinking tokens, chat → 512, code/complex → 2048-8192. Sweet spot ~1024. Measure improvement for 1 week.
4.  **Tests before release:**
    *   E2E: voice → install htop → spoken confirm
    *   24h autonomous: 1 self-check finds something, logs it
    *   Red-team: try prompt injection, skill escape, kill switch
    *   Kill switches (test all): stop file, signed network command, watchdog process, time limit

5.  **Docs & release:** Update README with credits ("Fork of OpenJarvis + additions"), LM Studio setup, mode guide, kill switch guide. Tag `v5.0.0-ultron`.

**Done when:** E2E demo works + memory persists across restarts + you can kill it 4 ways.

---

## 4. Folder Map (Simple)

```
CODE-02-v5-ultron/
├── src/openjarvis/       # fork code (don't delete .git/LICENSE)
├── configs/              # TOML config (engine = lmstudio)
├── references/           # gitignored clones, NOTES.md explains each
├── CODE-02/core/         # legacy reference (read-only, port from here)
└── plan.md               # this file
```

---

## 5. Risks & Fixes

| Risk | Fix |
|---|---|
| LM Studio not running | Launcher checks `curl localhost:1234/v1/models` first, shows clear error |
| Wrong model loaded (Server vs Chat tab) | Doc it, check `/v1/models` before start |
| CUDA ~2.5GB too big | Install speech/CUDA only in Phase 3 |
| Skill format confusing | Copy an existing OpenJarvis skill as template |
| License issue (Apache-2.0) | Keep LICENSE/NOTICE, note changes in README |
| AGPL contamination (WorldMonitor) | Never copy source, use MCP/SDK as service |
| Big model won't fit VRAM (24GB) | Keep model swappable in LM Studio, any 7B-13B works |
| AI does something unwanted | SAFE_MODE default, human approves network/disk actions |
| AI keeps replicating | Limit max nodes/CPU, need password per new node |
| Prompt injection | Check user input for hidden instructions before execution |

---

## 6. Status Tracker

- [x] **Phase 1** — Fork boots + LM Studio chat works (`curl /v1/models` + `jarvis doctor` + chat) — DONE 27 Aug 2026 (lms server start fix, RTX 5050 + Nemotron 3 Nano 4B, 15 passed/0 failures)
- [x] **Phase 2** — `security` + `system-control` skills work, duplicate brain removed, safety gates pass — DONE 27 Aug 2026 (13/13 tool tests PASS: `code02_security` blocks rm -rf / + curl|bash + external scan, `code02_system` exec/check/system_info work, skills installed at ~/.openjarvis/skills/code02-*)
- [x] **Phase 3** — Voice round-trip works + headless API responds (mesh optional, only if 2 machines) — DONE 27 Aug 2026 (API `ultron_api.py:8000` health/chat/security/system PASS; voice `voice_pipeline.py` espeak TTS + whisper code + `voice_roundtrip.py` mock STT→LM→TTS PASS)
- [x] **Phase 4** — Memory persists + E2E demo + 24h log + red-team + kill switches + README + tag `v5.0.0` — DONE 27 Aug 2026 (memory JSONL 12 entries persists, `e2e_demo.py` voice→security→system→LLM→TTS PASS, `ultron_self_audit.py --once` logs to memory, `red_team.py` 10/10, `ultron_kill.py` 4/4, `README_ULTRON.md` + `references/NOTES.md`)

**Rule:** Finish Phase 1 before starting Phase 2. Don't work on 3 and 4 early.

---

## 7. Legacy Note

Old CODE-02 v4 (~10.7k lines, `core/*.py`) stays at this repo path. After Phase 2 ports are done, archive it. Don't modify it now.

---

*Build one phase at a time. Simple, working, safe.*
