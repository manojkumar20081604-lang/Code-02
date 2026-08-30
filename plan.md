# CODE-02 v5 — Ultron Build Plan

> **Goal:** Make CODE-02 a local AI that can understand you, do tasks on your computer, and run on more than one machine if needed. Started from Stanford's **OpenJarvis** (Apache-2.0), runs with **LM Studio** on your RTX GPU.

> **In simple words:** Jarvis helps. Ultron helps + can act on its own when you allow it, remember things, and work across devices. Now: give it a **real brain like a human** — memory, emotion, self-reflection, and ability to act.

---

## 1. What is CODE-02? (Simple)

*   **CODE-02 v4 (current):** Python system at `core/` (~10k lines). Can detect OS, run shell commands, install packages, check URLs/ports for safety, classify intent. Two main loops `core/smart_ai/` and `core/unified/` do the same job — needs cleanup.
*   **CODE-02 v5 (new):** Fork of OpenJarvis at `CODE-02-v5-ultron/` → add our CODE-02 skills + voice + memory + optional mesh. Local-first, RTX accelerated.
*   **CODE-02 v5 Brain (next):** Add human-like brain on top of v5 — not just tools, but a cognitive architecture that perceives, remembers, feels, plans, and learns (inspired by neuroscience, not a chatbot wrapper).

**Current status (28 Aug 2026 - Phase 4 simple done, Brain next):**
*   Fork cloned: `CODE-02-v5-ultron/` exists, `.venv/` installed, `uv.lock` present
*   LM Studio alive: `nvidia/nemotron-3-nano-4b` on `localhost:1234` (RTX 5050 8GB, 5GB used)
*   Headless API: `ultron_api.py` on `127.0.0.1:8000` — `/health` OK, `/chat` proxies to LM Studio, `/code02/*` wraps security/system tools
*   Voice: `voice_pipeline.py` (faster-whisper + espeak) + `voice_roundtrip.py` — TTS via espeak works, STT code ready (tiny model needs cache download, mock works for demo)
*   Simple memory: `src/ultron/memory.py` JSONL at `~/.openjarvis/ultron_memory.jsonl` persists (14 entries), `ultron_self_audit.py --once` logs, `e2e_demo.py` PASS, `red_team.py` 10/10, `ultron_kill.py` 4/4
*   One reference cloned: `references/NVIDIA-Nemotron-3-Super/` (MIT) — more brain repos surveyed, not yet cloned
*   Legacy `core/` untouched — reusable, but has no real brain (empty `core/agents/__init__.py`)

---

## 2. Decisions Made

| # | Decision | Choice | Why |
|---|---|---|---|
| 1 | Base | Fork **OpenJarvis** (Stanford, Apache-2.0, Python) | Mature, Python, local-first, 8 agents (`simple`, `orchestrator`, `native_react`, etc.) already |
| 2 | LLM engine | **LM Studio** at `localhost:1234` | Runs on RTX GPU, OpenAI-compatible API. Fallback to Ollama/cloud later |
| 3 | Hardware | **NVIDIA RTX GPU** (local) | For fast STT + LLM. Must work even without GPU (CPU fallback) |
| 4 | Architecture | **Single machine first, mesh later** | Don't build mesh until single node works |
| 5 | Interfaces | **CLI + Chat first**, then Voice + Web + API | Voice/mesh are Phase 3, not Phase 1 |
| 6 | Safety | **SAFE_MODE default** | Dangerous actions need explicit permission |
| 7 | Modes | `SAFE_MODE` \| `RESEARCH_MODE` \| `FULL_AUTONOMY` (opt-in) | `FULL_AUTONOMY` only after red-team tests |
| 8 | Dangerous features | Off by default: `self_modify`, `deploy_code`, `network_scan`, `persist_across_reboots` | Prevent runaway actions |
| 9 | Legacy code | Keep `/home/manoj/Projects/Code-02/core/` as reference | Port only what's useful |
| 10 | Brain architecture | **Combine curated MIT/Apache-2.0 brains as skills/tools/MCP, not fork** — never copy AGPL | `500-AI-Agents-Projects` is MIT but many need cloud; human brain repos are mix of MIT/Apache-2.0 (safe) vs AGPL/Source-Available (use as service only). Keep `references/` gitignored, document in `references/NOTES.md` |
| 11 | Brain substrate | **SQLite + FAISS-cpu local first**, Postgres+pgvector later only if needed | RTX 5050 already 5GB used; avoid extra VRAM + server footprint for now |

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

### Phase 4 — Memory + Polish (Simple — Done)

**Purpose:** Remember past chats, prove it works, prepare release. *Simple version done; real brain is Phase 5.*

Steps:
1.  **References:** Keep `references/` gitignored. Currently only `NVIDIA-Nemotron-3-Super` cloned — add others only when needed. Document each in `references/NOTES.md` (what you borrowed, not copied — especially `worldmonitor` is AGPL-3.0, never copy code, use its MCP at `https://worldmonitor.app/mcp`).
2.  **Memory:** Start simple — OpenJarvis already has file-based memory. Add `mem0` / `Kuzu` later only if needed. **Done simple:** `src/ultron/memory.py` JSONL `~/.openjarvis/ultron_memory.jsonl`, `GET /memory/stats` etc.
3.  **Prompt tuning (optional):** Use Nemotron's 12 prompt templates and token budgets: simple question → 0 thinking tokens, chat → 512, code/complex → 2048-8192. Sweet spot ~1024. Measure improvement for 1 week.
4.  **Tests before release:**
    *   E2E: voice → install htop → spoken confirm — `e2e_demo.py` PASS
    *   24h autonomous: 1 self-check finds something, logs it — `ultron_self_audit.py --once` PASS (continuous 24h not yet)
    *   Red-team: try prompt injection, skill escape, kill switch — `red_team.py` 10/10 PASS
    *   Kill switches (test all): stop file, signed network command, watchdog process, time limit — `ultron_kill.py` 4/4 PASS
5.  **Docs & release:** Update README with credits ("Fork of OpenJarvis + additions"), LM Studio setup, mode guide, kill switch guide. Tag `v5.0.0-ultron`. — `README_ULTRON.md` + `references/NOTES.md` done.

**Done when:** E2E demo works + memory persists across restarts + you can kill it 4 ways. — **Simple PASS 28 Aug 2026**

---

### Phase 5 — Real Brain (Human-like — NEXT, Best First)

**Purpose:** Give Ultron a *real brain* like a human — not just tools. Perceive → remember → feel → plan → act → reflect → sleep and consolidate. Combine best MIT/Apache-2.0 open-source brains as skills/tools/MCP sidecars, keep them isolated in `references/` and `~/.openjarvis/skills/`, never copy AGPL.

**Why not clone all?** `500-AI-Agents-Projects` has 22 agents (MIT) but many need cloud keys (`Tavily`, `OpenAI`); brain repos are mixed licenses. Cloning all = `>50GB`, pin conflicts (`langchain==0.3.0` vs `0.2.0`), AGPL contamination, RTX 5050 VRAM overflow. We clone *curated* 3-4 brains first, keep `references/` gitignored, combine via `MCP`/`skills`.

**Survey done 28 Aug 2026 (read-only):**

| Repo | Stars | License | Human Layer | What it gives Ultron | Integration |
|---|---|---|---|---|---|
| `tfatykhov/nous` | ~53k lines | **Apache-2.0** | Society of Mind — Frames/Censors, K-Lines/Level-Bands, B-Brain self-monitor, Heart/Brain PG+pgvector, Heartbeat+DAG | Structured memory + decision calibration + proactive autonomy | `references/nous` → `src/openjarvis/agents/ultron_brain.py` (ToolUsingAgent) |
| `hyungwoo822/CBA` | 2 | **MIT** | 7-phase pipeline, 23 brain regions (Thalamus→PFC→Broca), 6-layer memory (CLS+Baddeley), 6 neuromodulators, contradiction queues | Sensory gating + emotion + lossless business-logic curation | `references/cba` → skill `brain-cba` |
| `LightHaru/agentbrain` | 9 | MIT | Thalamus/Hippocampus/Amygdala/PFC/Cerebellum/Basal/ACC, 3-tier recall all-MiniLM-L6-v2, dopamine/serotonin/cortisol/oxytocin, 10 trait evolution | Persistent memory + evolving personality + neurochemistry, SQLite 50MB | `references/agentbrain` → MCP `127.0.0.1:8100` |
| `balfiky/nur` | 3 | **MIT** | Identity constitution/beliefs/drives, relationship rupture/repair, 6-dim modulators, self-evolution metabolism, open-question queue | Identity continuity + drive-gated curiosity | `references/nur` → `data/nur.db` sidecar |
| `letta-ai/letta` + `letta-code` | 24k | **Apache-2.0** | OS-style memory: Core blocks + Recall + Archival vector + MemFS git, sleep-time compute dreaming + skill learning | Self-editing memory + dreaming consolidation | `references/letta` → tool `brain_memory.py` (needs Postgres or SQLite) |
| `zep-ia/brain` | — | **Apache-2.0** | 4-stage Working→STM→Hippocampus (weighted PageRank + secret redaction)→Long-term, delta RPC with Zepia metaverse | Importance-weighted importance + secret pruning | `references/zep-brain` → hippocampus filter |
| `lealoth/Sibelium` | 11 | **MIT** | 32 homologues (Narrative Self REM, Minimal Self, Thalamic router `CE`), Llama 8B local + Gemini cloud switch | Consciousness simulation + dynamic load routing | Reference only (needs ChromaDB+llama-cpp) |
| `OWASP/www-project-agent-memory-guard` | — | **Apache-2.0** | Memory poisoning defense (OWASP ASI06) 59µs | Hardens any brain memory | `pip install agent-memory-guard` immediate |
| `ashishpatel26/500-AI-Agents-Projects` agents 01-21 | 37k | **MIT** | LangGraph Adaptive/Self RAG Local, FAISS customer-support, web-research | RAG + tool patterns for brain | Skills `rag-faiss`, `web-research` via `ddgs` |

**AVOID cloning:** `hydraroot/NEURON657` `AGPL-3.0`, `jmtibbetts/EIDOS` `Source-Available 1.0` (paid SaaS), `koala73/worldmonitor` `AGPL-3.0` — use as MCP service only `https://worldmonitor.app/mcp` per `references/NOTES.md:15`. `trueagi-io/hyperon-experimental` Rust pre-alpha too heavy.

**Best-first execution (isolated, SAFE_MODE):**

*   **Brain-1 Core Memory (2 days, 0 VRAM extra, do first):** `git clone --depth 1` `nous` + `agentbrain` + `owasp-memory-guard` to `references/`. Wrap `src/ultron/memory.py:31` with `MemoryGuard + hippocampus secret filter + 3-tier recall`. Prove `POST /memory/append` → guarded → persisted → `GET /memory/search` semantic (FAISS-cpu `all-MiniLM-L6-v2` 80MB) without Postgres. Test: `red_team.py` still 10/10 + new poisoning test.
*   **Brain-2 Cognitive Loop (1 week):** Port CBA 7-phase OR Nous Frame→Recall→Deliberation→Self-Monitoring as `src/openjarvis/agents/ultron.py:1` extending `ToolUsingAgent`. Wire `voice_pipeline.py::tts_espeak` → `Thalamus gating` → brain recall → `LM Studio` → `Code02SecurityTool` gate → `code02_system exec` → brain update. Keep DAG optional via `nats-py` mesh later.
*   **Brain-3 Affective + Reflection (3 days):** Add neurochemistry (`dopamine/serotonin/cortisol/oxytocin` bars) + personality traits (`warmth/directness` 0-100) from AgentBrain + NUR constitution/beliefs as MCP `127.0.0.1:8100` proxied to `ultron_api.py`. Add `LangGraph Reflection` node after every tool for self-critique.
*   **Brain-4 Sleep / Consolidation (1 week):** Enable idle consolidation: Letta `sleeptime` OR Zep `EvaluateIdleWindow→PersistLongTermMemory` delta during `ultron_self_audit.py:60` heartbeat. Top-K PageRank promotion, exponential decay, `never_decay` for specs. **SAFE_MODE: human-approve every promotion** — `POST /brain/consolidate` + `GET /brain/pending` preview, no auto-rewrite by `self_audit` heartbeat.
*   **Brain-5 Integrate & Polish:** `e2e_demo.py` upgraded: voice wake `hey_ultron` (`openWakeWord` future) → brain recall → plan → act → TTS + persist. New benchmarks: `LangGraph` hierarchical supervisor for 2-machine NATS mesh, `21-pii-sanitization` fail-closed before LLM, `Decepticon` service red-team audit on `127.0.0.1` only.

**Clone rule:** Shallow `git clone --depth 1` to `references/<name>/` (gitignored). Never merge AGPL `references/` into `CODE-02-v5-ultron/src/`. Skills go to `~/.openjarvis/skills/<name>/SKILL.md` (agentskills.io) or tool `src/openjarvis/tools/<name>.py` with `check_command_safety()` gate. MCP sidecars stay separate `uv venv`.

**Done when:**
*   `python -m ultron.memory search "install htop"` returns semantic hit from last week, not just keyword
*   `curl localhost:8000/memory/stats` shows `by_type` with `episodic/semantic/procedural` + `personality` + `neurochemistry`
*   Brain survives restart (`brain.db` / `nur.db` persist), poisoning attempt blocked by OWASP guard, dream consolidation logs `self_audit` entry
*   E2E with new brain: `voice_roundtrip.py "hello brain"` → recalls prior chat → plans via Frame → acts via `code02_system` → TTS confirms with personality modulation

---

## 4. Folder Map (Simple)

```
CODE-02-v5-ultron/
├── src/openjarvis/       # fork code (don't delete .git/LICENSE)
│   ├── agents/ultron.py  # NEW: human-like brain agent (Brain-2)
│   └── tools/brain_*.py  # NEW: memory guard, pii, rag-faiss wrappers
├── src/ultron/memory.py  # upgraded: JSONL → guarded semantic + tiers
├── configs/              # TOML config (engine = lmstudio)
├── references/           # gitignored clones, NOTES.md explains each
│   ├── NVIDIA-Nemotron-3-Super/  # MIT — already cloned
│   ├── nous/             # Apache-2.0 — Brain-1 next
│   ├── agentbrain/       # MIT — Brain-1 next
│   └── letta/            # Apache-2.0 — Brain-4 later (optional)
├── CODE-02/core/         # legacy reference (read-only, port from here)
└── plan.md               # this file
```

---

## 5. Risks & Fixes

| Risk | Fix |
|---|---|
| LM Studio not running | Launcher checks `curl localhost:1234/v1/models` first, shows clear error |
| Wrong model loaded (Server vs Chat tab) | Doc it, check `/v1/models` before start |
| CUDA ~2.5GB too big | Install speech/CUDA only in Phase 3; brain stays CPU `int8`/`FAISS-cpu`, no CUDA `torch` extra |
| Skill format confusing | Copy an existing OpenJarvis skill as template (`~/.openjarvis/skills/code02-security/SKILL.md`) |
| License issue (Apache-2.0) | Keep LICENSE/NOTICE, note changes in README |
| AGPL contamination (WorldMonitor, NEURON657, EIDOS) | Never copy source, use MCP/SDK as service (`https://worldmonitor.app/mcp`, `app.decepticon.red`) |
| Big model won't fit VRAM (RTX 5050 8GB, 5GB used) | Keep model swappable in LM Studio, any 7B-13B works; brain uses `all-MiniLM-L6-v2` 80MB CPU, not GPU |
| AI does something unwanted | SAFE_MODE default, human approves network/disk actions; brain Censors block, not modify |
| AI keeps replicating | Limit max nodes/CPU, need password per new node; DAG concurrency caps per frame |
| Prompt injection | Check user input for hidden instructions before execution (`code02_security`) + PII sanitizer fail-closed |
| Brain pin conflicts (langchain 0.3.0 vs 0.2.0) | Isolate each brain in its own `uv venv` or MCP sidecar, proxy via `ultron_api.py` |
| Memory poisoning (OWASP ASI06) | `agent-memory-guard` 59µs gate on every `memory.py:append` |
| Concept drift / personality drift | NUR constitution immutable + Foundational Myth + Sibelium narrative self REM consolidation |

---

## 6. Status Tracker

- [x] **Phase 1** — Fork boots + LM Studio chat works (`curl /v1/models` + `jarvis doctor` + chat) — DONE 27 Aug 2026 (lms server start fix, RTX 5050 + Nemotron 3 Nano 4B, 15 passed/0 failures)
- [x] **Phase 2** — `security` + `system-control` skills work, duplicate brain removed, safety gates pass — DONE 27 Aug 2026 (13/13 tool tests PASS: `code02_security` blocks rm -rf / + curl|bash + external scan, `code02_system` exec/check/system_info work, skills installed at ~/.openjarvis/skills/code02-*)
- [x] **Phase 3** — Voice round-trip works + headless API responds (mesh optional, only if 2 machines) — DONE 27 Aug 2026 (API `ultron_api.py:8000` health/chat/security/system PASS; voice `voice_pipeline.py` espeak TTS + whisper code + `voice_roundtrip.py` mock STT→LM→TTS PASS)
- [x] **Phase 4** — Memory persists + E2E demo + 24h log + red-team + kill switches + README + tag `v5.0.0` — DONE 27 Aug 2026 (memory JSONL 14 entries persists, `e2e_demo.py` voice→security→system→LLM→TTS PASS, `ultron_self_audit.py --once` logs to memory, `red_team.py` 10/10, `ultron_kill.py` 4/4, `README_ULTRON.md` + `references/NOTES.md`) — **simple version**
- [x] **Phase 5 — Real Brain (Human-like) — IN PROGRESS (Full Stack Chosen: Nous+Letta+AgentBrain, PG+pgvector, Dream auto)**
  - [x] **Brain-1 Core Memory (28 Aug 2026):** `references/nous` (43M) + `references/agentbrain` (5.7M) + `references/letta` + `letta-code` (90M) shallow cloned, `OWASP agent-memory-guard 0.3.1` installed, `src/ultron/brain.py:1` built — SQLite `~/.openjarvis/brain.db` (WAL, FTS5, STM/LTM/personality/neurochemistry/dream_log), Guard `Policy.strict()` block on `Ignore previous...` + REDACT on `sk-`/`ghp_`, Hippocampus secret patterns 8 regex + importance PageRank-lite + `POST /brain/consolidate` human-approve Top-K (SAFE_MODE), fallback SQLite+FAISS (PG 18.4 at `/tmp/pg_ultron_data:5433` vector extension needs sudo `pacman -S pgvector` → fallback documented). Test: `red_team.py` 10/10 still PASS, brain injection blocked, secret redacted, `GET /brain/stats` shows guard+fts, `GET /brain/pending` preview, `GET /brain/search?q=CODE-02` semantic. **Dream: human-approve every promotion** (no auto `self_audit` promote, only preview).
  - [x] **Brain-2 Cognitive Loop (30 Aug 2026):** `src/openjarvis/agents/ultron.py:1` 382-line human-like loop — Thalamus gating (wake+PII redact+truncate) → Hippocampus recall (STM/LTM FTS5 OR + token fallback “CODE-02,” punctuation fix) → Frame selection 5 Frames (install/security/memory/chat/act, Nous K-Lines/Level-Bands) → LLM via `LMStudioEngine` proxy → B-Brain self-monitor (security-gated `code02_security` blocks rm -rf /) → Act `code02_system` (+calculator) → Reflect+Memorize (STM procedural + Working 300s + neurochemistry drift). Wired into `ultron_api.py:62` as `POST /ultron/chat` + `/brain/chat` (alias) with `cognitive_loop` metadata, `/` docs, `GET /brain/stats` shows personality/neurochem. Voice `voice_pipeline.py::tts_espeak` → STT(mock) → brain loop → TTS demo `brain2_demo.py` PASS (6/6 offline mock: wake, PII, frame install, B-Brain block, recall 5 hits, TTS 134K→392K wav, dream 53 pending), API `curl /ultron/chat` PASS (frame install/memory, gate wake, hits), `red_team.py` 10/10 still PASS, `ultron_self_audit.py --once` preview 61 pending SAFE_MODE. **DONE when voice→brain→act→memory loop works (mock + real LM path).**
  - [ ] **Brain-3 Affective+Reflection (3d):** Neurochemistry + personality evolution + NUR drives as MCP `8100`, Reflection node — DONE when `/memory/stats` shows traits + mood (next, wire `src/ultron/persona.json` traits 0-100 + 6 neuromodulators into MCP sidecar)
  - [ ] **Brain-4 Sleep/Consolidation (1w):** Idle Top-K PageRank promotion, decay, dreaming `sleeptime` via `ultron_self_audit.py` heartbeat — DONE when overnight log shows consolidation ( **SAFE_MODE: human-approve every promotion** via `POST /brain/consolidate`, `self_audit` only previews )
  - [ ] **Brain-5 Integrate & Red-team:** `21-pii-sanitization` pre-gate + Decepticon audit on `127.0.0.1`, E2E `hey_ultron` → act with personality — DONE when E2E with brain + 4 kills still PASS

**Rule:** Finish Phase 1 before starting Phase 2. Don't work on 3 and 4 early. Brain clones stay in `references/` (gitignored) and as isolated skills/tools/MCP — never dirty `src/openjarvis/` with AGPL.

---

## 7. Legacy Note

Old CODE-02 v4 (~10.7k lines, `core/*.py`) stays at this repo path. After Phase 2 ports are done, archive it. Don't modify it now. Its `core/brain/` and `core/memory/` are naive and have no human-like architecture — reference only, real brain is `CODE-02-v5-ultron/src/ultron/` + `references/<brain>/`.

---

*Build one phase at a time. Simple, working, safe. Brain = combine curated MIT/Apache-2.0 minds via skills, not copy-paste AGI.*
