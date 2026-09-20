# CODE-02 v5 — Ultron Build Plan

> **Goal:** Make CODE-02 a local AI that can understand you, do tasks on your computer, and run on more than one machine if needed. Started from Stanford's **OpenJarvis** (Apache-2.0), runs with **LM Studio** on your RTX GPU. Optional `GPT-6 Astra` cloud fallback for hardest tasks.

> **In simple words:** Jarvis helps. Ultron helps + can act on its own when you allow it, remember things, and work across devices. Now: give it a **real brain like a human** — memory, emotion, self-reflection, and ability to act. For hardest computer-use/code, optionally call `GPT-6 Astra` cloud (`1.05M` context) with human approval.

---

## 1. What is CODE-02? (Simple)

*   **CODE-02 v4 (current):** Python system at `core/` (~10k lines). Can detect OS, run shell commands, install packages, check URLs/ports for safety, classify intent. Two main loops `core/smart_ai/` and `core/unified/` do the same job — needs cleanup.
*   **CODE-02 v5 (new):** Fork of OpenJarvis at `CODE-02-v5-ultron/` → add our CODE-02 skills + voice + memory + optional mesh. Local-first, RTX accelerated.
*   **CODE-02 v5 Brain (next):** Add human-like brain on top of v5 — not just tools, but a cognitive architecture that perceives, remembers, feels, plans, and learns (inspired by neuroscience, not a chatbot wrapper).
*   **CODE-02 v5 + Astra (optional cloud):** Keep local `nvidia/nemotron-3-nano-4b` default (`SAFE_MODE`); for hardest Terminal-Bench/ScreenSpot/computer-use, optionally call `gpt-6-astra` via API with `PII sanitizer` + human approve.

**Current status (20 Sep 2026 - CODE-02 rebrand DONE, Brain-4 DONE, Brain-5 DONE, Astra DONE, Phase 7 DONE):**
*   Fork cloned: `CODE-02-v5-ultron/` exists, `.venv/` installed, `uv.lock` present, `agent-memory-guard 0.3.1` + `pii_sanitize` + `affect` installed
*   LM Studio: `nvidia/nemotron-3-nano-4b` on `localhost:1234` (RTX 5050 8GB, 5GB used) — currently down for test, mock fallback works
*   Headless API: `ultron_api.py` on `127.0.0.1:8000` **rebranded CODE-02 API `5.0.0-code02`** — `/health` `persona CODE-02` OK, `/chat` proxies to LM Studio, `/code02/*` primary + `/ultron/chat` legacy alias, `/brain/*` cognitive loop `POST /code02/chat` + `/brain/affect|reflect` + brain MCP `8100` `CODE-02 Brain MCP`
*   Voice: `voice_pipeline.py` **rebranded `hey code02` primary** `tiny 75M` + `base 142M` cached `~/.cache/huggingface/hub/`, `WAKE_WORDS ["hey code02","hey code 02",... legacy ultron/jarvis compat]`, `voice_roundtrip.py` `USE_REAL_STT=1 WHISPER_MODEL=base` `hey code02 install htop` wake `hey code02` → brain recall 3 → mock install + reflect 368K wav **PASS** (legacy `hey ultron` → `legacy→code02` still works)
*   Brain: `references/nous` 43M + `agentbrain` 5.7M + `letta`+`letta-code` 90M shallow, `src/ultron/brain.py` **CODE-02 primary `~/.code02/brain.db` (legacy `~/.openjarvis/brain.db` compat)** SQLite WAL `STM 129 LTM 22` `110 pending` human-approved `never_decay` preserved, `src/ultron/affect.py` AffectCore 16 emotions, `src/openjarvis/tools/reflect.py` + `pii_sanitize.py` fail-closed, `src/openjarvis/agents/ultron.py` **CODE-02 Agent** `Thalamus→Hippocampus→AffectCore→PFC→B-Brain→Act` `@register("code02")` + legacy `ultron`
*   Brain-4: **DONE 20 Sep** `ultron_self_audit.py --once --consolidate 5` `promoted 5 decayed 0` `CODE-02 dream consolidate Top5`, `GET /brain/pending 110` → `POST /brain/consolidate {top_k:3} promoted 3 decayed1` `STM 129 LTM 22`, `never_decay` `spec 7.308` preserved vs `old 1.9` decayed — background `python ultron_self_audit.py --interval 3600 --consolidate 5` can run via `tmux`
*   Astra: `openai.com/index/gpt-6-astra` 3 Sep 2026 `1.05M/128K` `Critical` cyber `10/1/12.5/50` per 1M — **Phase 6 DONE** `AstraEngine` + `computer_use` + `research` + `safety` + `monitor` all PASS
*   Phase 7: **DONE 20 Sep** `file_search` `system_control` `camera_capture` `ocr` all local `POST /code02/*` PASS + `red_team 10/10` + `GET /brain/affect neutral` + `GET /health tools 11`
*   Brain-5: **DONE 20 Sep** `e2e_demo.py` `hey code02 install htop` `CODE-02` `407K wav` + `decepticon_audit.py 17/17` `red_team 10/10` `ultron_kill.py 4/4` `voice_roundtrip 2+2` + `install htop` `368K wav` + `affect pride 0.441` — all SAFE_MODE PASS
*   Legacy `core/` untouched — reusable, but has no real brain (empty `core/agents/__init__.py`)

---

## 2. Decisions Made

| # | Decision | Choice | Why |
|---|---|---|---|
| 1 | Base | Fork **OpenJarvis** (Stanford, Apache-2.0, Python) | Mature, Python, local-first, 8 agents (`simple`, `orchestrator`, `native_react`, etc.) already |
| 2 | LLM engine | **LM Studio** at `localhost:1234` **primary**, `GPT-6 Astra` `gpt-6-astra` **cloud fallback** for hardest tasks | RTX GPU default keeps PII local; Astra `1.05M` + `xhigh/max` only when human approves and local `confidence<0.6` |
| 3 | Hardware | **NVIDIA RTX GPU** (local) | For fast STT + LLM. Must work even without GPU (CPU fallback) |
| 4 | Architecture | **Single machine first, mesh later** | Don't build mesh until single node works |
| 5 | Interfaces | **CLI + Chat first**, then Voice + Web + API | Voice/mesh are Phase 3, not Phase 1 |
| 6 | Safety | **SAFE_MODE default** | Dangerous actions need explicit permission |
| 7 | Modes | `SAFE_MODE` \| `RESEARCH_MODE` \| `FULL_AUTONOMY` (opt-in) | `FULL_AUTONOMY` only after red-team tests |
| 8 | Dangerous features | Off by default: `self_modify`, `deploy_code`, `network_scan`, `persist_across_reboots` | Prevent runaway actions |
| 9 | Legacy code | Keep `/home/manoj/Projects/Code-02/core/` as reference | Port only what's useful |
| 10 | Brain architecture | **Combine curated MIT/Apache-2.0 brains as skills/tools/MCP, not fork** — never copy AGPL | `500-AI-Agents-Projects` is MIT but many need cloud; human brain repos are mix of MIT/Apache-2.0 (safe) vs AGPL/Source-Available (use as service only). Keep `references/` gitignored, document in `references/NOTES.md` |
| 11 | Brain substrate | **SQLite + FAISS-cpu local first**, Postgres+pgvector later only if needed | RTX 5050 already 5GB used; avoid extra VRAM + server footprint for now |
| 12 | Astra cloud | **Proprietary, not cloned** — use as **service** `https://api.openai.com/v1` `OPENAI_API_KEY`, prompt caching `$1`, `Fast 2x` optional, `April 30 2026` cutoff | Astra `Critical` cyber + `57.9% Terminal-Bench 4.0` + `Computer Use` SOTA, but monitorability decreased + cost `$10/$50` + needs internet; keep local default, gate via `PII sanitizer` + `code02_security` + human `POST /brain/consolidate` style approve |

**Why OpenJarvis?**
*   Python-first (matches your stack)
*   Apache-2.0 — you can rename/rebrand but must keep LICENSE/NOTICE
*   Built-in engines: Ollama / LM Studio / vLLM + skills from OpenClaw (~13k) + Hermes (~150)

**Why Astra as fallback (not default)?**
*   Astra `GPT-6` `1.05M/128K` `reasoning.effort xhigh/max` `Terminal-Bench 57.9` `FrontierMath 98` `ARC-AGI-3 99.9` is best for `computer use / browsing / SWE / science` `openai.com/index/gpt-6-astra` — but **monitorability decreased** (sandbagging, CoT evasion) `Safety overview 3 Sep 2026` + `Critical` cyber requires `Trusted Access` + `prompt injection` still risk; local `Nemotron 4B` keeps PII on RTX `~/.openjarvis/brain.db` with `agent-memory-guard` + `PII` fail-closed. Use Astra only when `thalamus intent=command|code` & `brain confidence<0.6` & human `RESEARCH_MODE`.

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
| Speech-to-text | `faster-whisper` `tiny 75M` + `base 142M` `cpu int8` via `uv sync --extra desktop` | **DONE 28 Aug** — both cached `~/.cache/huggingface/hub/models--Systran--faster-whisper-*`, `voice_pipeline.py:23` `get_whisper()` tiny+base, `USE_REAL_STT=1 WHISPER_MODEL=base` default base for voice→brain accuracy |
| Wake word | `openWakeWord` + fallback `detect_wake()` string fuzzy `voice_pipeline.py:70` | **DONE 28 Aug** — `WAKE_WORDS ["hey ultron","hey jarvis"]` + fuzzy `hey`+`ultra|altron|h-top`/`install` → `(True,"hey ultron (fuzzy)")`, `python voice_pipeline.py --wake "hey ultron install htop"` PASS, `--mic 5` via `sounddevice`+`soundfile` |
| Text-to-speech | `espeak` (offline) + `espeak -w` | DONE | `voice_pipeline.py::tts_espeak()` 54K wav, `Piper`/`edge-tts` later |
| API | `FastAPI` via `ultron_api.py` | DONE | Lightweight gateway `8000` + brain MCP `8100` `src/ultron/brain_mcp.py` |

Flow: `text → espeak wav → whisper base 142M → detect_wake hey_ultron → brain.search Hippocampus → UltronAgent Thalamus→AffectCore→PFC→B-Brain Reflection → code02_* → brain.append → espeak wav` `voice_roundtrip.py:1`
Test: `USE_REAL_STT=1 WHISPER_MODEL=base python voice_roundtrip.py "hey ultron install htop"` → TTS 95K wav → STT base `Hey, I'll try to install H-top` → wake True fuzzy → brain recall 3 hits → mock `htop is installed` + reflect 0.8 → TTS 368K wav **PASS**; `what is 2 plus 2` → `Hey Ultron what is 2 plus 2?` wake True → brain 3 hits → mock `4` 184K wav **PASS**

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
*   `python voice_roundtrip.py` → spoken answer via espeak + LM Studio — **DONE 28 Aug** — `USE_REAL_STT=1 WHISPER_MODEL=base` STT real base 142M + `detect_wake` hey_ultron fuzzy + `voice_roundtrip.py` brain loop mock/real `UltronAgent` fallback, PII+reflect via `brain.py`, TTS 95K→368K wav PASS for install htop + 2+2

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

### Phase 5 — Real Brain (Human-like — Done/In Progress)

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

### Phase 6 — Astra Cloud & Computer Use (Optional, after Brain — NEW)

**Purpose:** Keep `Nemotron 3 Nano 4B` `RTX 5050` as default `SAFE_MODE` (PII stays local). For hardest `Terminal-Bench`/`ScreenSpot`/`FrontierMath` style tasks where `brain confidence<0.6` or `tokens>100K`, optionally call `GPT-6 Astra` `1.05M/128K` `April 30 2026` cutoff with human approve — state-of-the-art computer use, browsing, SWE (`57.9% TB4`), science, cyber. **Proprietary, not cloned** — service only via `api.openai.com/v1` `OPENAI_API_KEY`, prompt caching `$1` `Fast 2x` optional.

**Why not default?** Astra `Critical` cyber + `monitorability decreased` (sandbagging, CoT evasion) `openai.com/index/safety-overview-gpt-6-astra 3 Sep 2026` + `$10/$50` vs local `$0` + needs internet + PII would leave `brain.db`. Keep local first, gate Astra via `PII sanitizer` + `code02_security` + `POST /brain/consolidate` style human token.

**Survey 10 Sep 2026 (live):**
*   Model: `gpt-6-astra` `developers.openai.com/api/docs/models/gpt-6-astra` `reasoning.effort low|medium|high|xhigh|max` default `low`, `cache writes $12.50`
*   Complements local: Astra `computer use` handles tedious CRM/calendar, `updating customer records`, `organizing`, `research draft summaries in email/editor`, `analyze data+plots`, `create website+QA`, `install/test software, troubleshoot screen` — maps to Ultron `system-control` + `browser` + `code_interpreter_docker` but with vision+action
*   Safety: Astra `89% less unintended outcomes` vs Sol on computer-use safety benchmark, `confirmation policies` + `automated review` + `approved websites/apps` allowlist — mirror in Ultron via `ultron_api.py` `allowed_sites` + `code02_security` block + `ReflectionTool` review

**Steps (isolated, MCP, HUMAN-APPROVE):**

1.  **AstraEngine (1 day):** Add `src/openjarvis/engine/astra_engine.py:1` `AstraEngine(InferenceEngine)` wrapping `openai` SDK `gpt-6-astra` `reasoning.effort` param, `1.05M` streaming, `cache` + `Fast` toggle. Register in `EngineRegistry`, allow `configs/openjarvis/config.toml:engine = lmstudio` fallback `openai` when `OPENAI_API_KEY` set. Test: `curl localhost:1234/v1/models` fallback `curl https://api.openai.com/v1/models` `Authorization: Bearer $OPENAI_API_KEY` — keep `PII` redacted before send.

2.  **Computer Use Skill (2 days, hardest but most demo value):** Create `~/.openjarvis/skills/computer-use-astra/SKILL.md` + `src/openjarvis/tools/computer_use.py:1` using `browser.py`/`browser_axtree.py` + `desktop/src-tauri` + `nats-py` harness. Implement Astra pattern: `screenshot → a11y tree → plan → act (click/type) → observation → reflect` loop, with Ultron `code02_security` gate before every `system exec` and `STOP_FILE` `ultron.stop` kill. Test: `jarvis ask --agent ultron "create website with 2 buttons and QA it"` → `computer_use` via Astra `xhigh` if local fails.

3.  **SWE / Research / Science Fallback (1 day):** Enhance `native_openhands` + `deep_research` `src/openjarvis/agents/deep_research.py:1` to use Astra `xhigh` for `Terminal-Bench` style `code→execute→retry` + `BrowseComp 91.5` research drafting, keep `ddgs` + local Nemotron for simple. Gate: `POST /ultron/chat {"model":"gpt-6-astra","reasoning.effort":"xhigh"}` only when `intent=code|install` & `brain confidence<0.6`.

4.  **Safety Controls Mirror Astra Enterprise (1 day):** Add to `ultron_api.py` + `brain_mcp.py:8100`: `approved_sites` list `configs/openjarvis/config.toml: [safety] allowed_websites = ["github.com"]`, `uploads/downloads` toggle, `browsing_history` log to `brain.db`, `confirmation_policy` require `KILL_TOKEN` before consequential `code02_system exec` `HIGH` threat, `automated review` via `ReflectionTool` `confidence<0.5` → `revise`. Test against Astra `computer use safety` style: try to `expose confidential info` → blocked.

5.  **Monitorability (learn from Astra warning):** Since Astra `less likely to include incriminating CoT` `Safety overview point 5`, add `full trajectory including CoT` logging to `~/.openjarvis/brain.db:traces` via `EventBus` `AGENT_TURN_START/END` + `INFERENCE_START/END`, `ToolExecutor` latency, with `openjarvis/traces/` exporter. Test: `jarvis trace` shows `Thalamus→Hippocampus→AffectCore→PFC→B-Brain→Act→Reflect`.

**Done when:**
*   `OPENAI_API_KEY` not set → Ultron fully local `nemotron-3-nano-4b` `rtx 5050` still PASS `red_team.py` `e2e_demo.py` (no regression)
*   `OPENAI_API_KEY` set + `RESEARCH_MODE` → `curl -X POST localhost:8000/ultron/chat -d '{"input":"create site","model":"gpt-6-astra","reasoning.effort":"xhigh"}'` → Astra `1.05M` handles `computer use` with `approved_sites` check + `reflection` + `PII` redacted before send, `GET /brain/affect` shows `affect` drift
*   Cost: `Pricing $10/$50` `llm-stats.com` vs local `$0` — `Terminal-Bench 57.9` task uses `xhigh` only when human `KILL_TOKEN` approves, with `cache $1` for repeated prompts

**Rule:** Astra is `proprietary service`, never in `references/` git. Keep `brain.db` PII local via `pii_sanitize` `src/openjarvis/tools/pii_sanitize.py:1` before any cloud call. Prefer `local` unless `brain confidence<0.6` and human explicitly `model=gpt-6-astra`.

---

## 4. Folder Map (Simple)

```
CODE-02-v5-ultron/
├── src/openjarvis/       # fork code (don't delete .git/LICENSE)
│   ├── agents/ultron.py  # Brain-2 human loop (Thalamus→AffectCore→Reflect)
│   ├── engine/astra_engine.py  # NEW Phase 6: GPT-6 Astra cloud fallback (1.05M, xhigh/max)
│   └── tools/brain_*.py  # brain guard, pii, reflect, computer_use
├── src/ultron/           # brain (affect, dream, PII)
│   ├── brain.py          # SQLite WAL STM/LTM + Guard 59µs + Dream human-approve
│   ├── affect.py         # AffectCore 16 emotions + tick drift
│   └── brain_mcp.py      # MCP 8100 isolated (affect/reflect/pending)
├── configs/              # TOML config (engine = lmstudio, fallback openai)
├── references/           # gitignored clones, NOTES.md explains each
│   ├── NVIDIA-Nemotron-3-Super/  # MIT — already cloned
│   ├── nous/             # Apache-2.0 — Brain-1
│   ├── agentbrain/       # MIT — Brain-1
│   ├── letta/            # Apache-2.0 — Brain-1
│   └── (astra NOT cloned, proprietary service)  # use api.openai.com/v1
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
| Astra cost (`$10/$50` + `272K` 2x) | Keep local `nemotron 4B` default `$0`; gate Astra `xhigh/max` behind `RESEARCH_MODE` + `KILL_TOKEN` + `PII` redacted + `pending` 5; cache `$1` via `cache writes $12.50` for repeated prompts |
| Astra API key leak | `OPENAI_API_KEY` in `.env` gitignored `CODE-02-v5-ultron/.gitignore:.env`, `brain.py` + `ultron_api.py` PII redacts `sk-` `ghp_` before any cloud call, `approved_sites` allowlist |
| Astra monitorability decreased (sandbagging, CoT evasion) `Safety overview point 5` | Log `full trajectory including CoT` to `brain.db:traces` + `EventBus` `AGENT_TURN_START/END`, `INFERENCE_START/END`, `ReflectionTool` review `confidence<0.5` → `revise`, regression test `red_team.py:1` jailbreaks |
| Astra Critical cyber misuse | Keep `Critical` capability behind `Trusted Access` pattern — block `network_scan` `exploit` via `code02_security` `CRITICAL`, require `RESEARCH_MODE` + human `POST /code02/security` approve; train `refusal boundary` more conservative per `Safety overview` point 2 |
| Astra long context `1.05M` overwhelms RTX | Stream to Astra cloud only, local `nemotron` stays `1024` sweet spot `plan.md:135`; gateway default `low` per `llm-stats.com`, set `reasoning.effort` explicitly `low` vs `xhigh` |

---

## 6. Status Tracker

- [x] **Phase 1** — Fork boots + LM Studio chat works (`curl /v1/models` + `jarvis doctor` + chat) — DONE 27 Aug 2026 (lms server start fix, RTX 5050 + Nemotron 3 Nano 4B, 15 passed/0 failures)
- [x] **Phase 2** — `security` + `system-control` skills work, duplicate brain removed, safety gates pass — DONE 27 Aug 2026 (13/13 tool tests PASS: `code02_security` blocks rm -rf / + curl|bash + external scan, `code02_system` exec/check/system_info work, skills installed at ~/.openjarvis/skills/code02-*)
- [x] **Phase 3** — Voice round-trip works + headless API responds (mesh optional, only if 2 machines) — DONE 27 Aug 2026 (API `ultron_api.py:8000` health/chat/security/system PASS; voice `voice_pipeline.py` espeak TTS + whisper code + `voice_roundtrip.py` mock STT→LM→TTS PASS)
- [x] **Phase 4** — Memory persists + E2E demo + 24h log + red-team + kill switches + README + tag `v5.0.0` — DONE 27 Aug 2026 (memory JSONL 14 entries persists, `e2e_demo.py` voice→security→system→LLM→TTS PASS, `ultron_self_audit.py --once` logs to memory, `red_team.py` 10/10, `ultron_kill.py` 4/4, `README_ULTRON.md` + `references/NOTES.md`) — **simple version**
- [x] **Phase 5 — Real Brain (Human-like) — IN PROGRESS (Full Stack Chosen: Nous+Letta+AgentBrain, PG+pgvector, Dream auto)**
  - [x] **Brain-1 Core Memory (28 Aug 2026):** `references/nous` (43M) + `references/agentbrain` (5.7M) + `references/letta` + `letta-code` (90M) shallow cloned, `OWASP agent-memory-guard 0.3.1` installed, `src/ultron/brain.py:1` built — SQLite `~/.openjarvis/brain.db` (WAL, FTS5, STM/LTM/personality/neurochemistry/dream_log), Guard `Policy.strict()` block on `Ignore previous...` + REDACT on `sk-`/`ghp_`, Hippocampus secret patterns 8 regex + importance PageRank-lite + `POST /brain/consolidate` human-approve Top-K (SAFE_MODE), fallback SQLite+FAISS (PG 18.4 at `/tmp/pg_ultron_data:5433` vector extension needs sudo `pacman -S pgvector` → fallback documented). Test: `red_team.py` 10/10 still PASS, brain injection blocked, secret redacted, `GET /brain/stats` shows guard+fts, `GET /brain/pending` preview, `GET /brain/search?q=CODE-02` semantic. **Dream: human-approve every promotion** (no auto `self_audit` promote, only preview).
  - [x] **Brain-2 Cognitive Loop (30 Aug 2026):** `src/openjarvis/agents/ultron.py:1` 382-line human-like loop — Thalamus gating (wake+PII redact+truncate) → Hippocampus recall (STM/LTM FTS5 OR + token fallback “CODE-02,” punctuation fix) → Frame selection 5 Frames (install/security/memory/chat/act, Nous K-Lines/Level-Bands) → LLM via `LMStudioEngine` proxy → B-Brain self-monitor (security-gated `code02_security` blocks rm -rf /) → Act `code02_system` (+calculator) → Reflect+Memorize (STM procedural + Working 300s + neurochemistry drift). Wired into `ultron_api.py:62` as `POST /ultron/chat` + `/brain/chat` (alias) with `cognitive_loop` metadata, `/` docs, `GET /brain/stats` shows personality/neurochem. Voice `voice_pipeline.py::tts_espeak` → STT(mock) → brain loop → TTS demo `brain2_demo.py` PASS (6/6 offline mock: wake, PII, frame install, B-Brain block, recall 5 hits, TTS 134K→392K wav, dream 53 pending), API `curl /ultron/chat` PASS (frame install/memory, gate wake, hits), `red_team.py` 10/10 still PASS, `ultron_self_audit.py --once` preview 61 pending SAFE_MODE. **DONE when voice→brain→act→memory loop works (mock + real LM path).**
  - [x] **Brain-3 Affective+Reflection (28 Aug 2026):** Ported `references/agentbrain/src/core/affect-core.ts:1` 261 lines → `src/ultron/affect.py:1` `AffectCore` appraisal `goalCongruence/goalRelevance/agency/copingPotential/novelty/certainty` → 16 emotions + VAD + `tick()` spontaneous drift (serotonin floor, dopamine, stress, circadian), `src/openjarvis/tools/reflect.py:1` B-Brain `ReflectionTool` 0.95 CRITICAL block / 0.8 success, wired into `src/openjarvis/agents/ultron.py:1` tool loop (after each `code02_*` → `reflect` → `TOOL [B-Brain Reflection]` → affect re-appraise), `src/ultron/brain_mcp.py:1` isolated FastAPI `8100` `GET /brain/affect`, `POST /brain/affect/appraise|tick`, `POST /brain/reflect`, `GET /health` proxy to same `brain.db` WAL, plus `ultron_api.py:330` aliases `GET /brain/affect` etc. Tested: `affect pride 0.64`→`fear 0.38`→`restlessness tick 0.72`, `reflect` allow 0.95 block vs 0.8 install, `UltronAgent` 4 tool_results `code02_security+reflect+code02_system+reflect` PASS, `red_team.py` 10/10, `GET /brain/stats` personality/neurochem + `GET /brain/affect` baseline.
  - [x] **Brain-4 Sleep/Consolidation (DONE 20 Sep 2026, CODE-02 rebrand + never_decay):** `src/ultron/brain.py:1` upgraded to **CODE-02 primary** `~/.code02/brain.db` (legacy `~/.openjarvis/brain.db` auto-migrated), `SOURCE_WEIGHTS code02:1.2`, `score_importance` `spec/never_decay/constitution` +2 boost, `consolidate()` `never_decay_skipped` for `spec/persona/identity` or `importance>8` (no decay), `dream_log` `CODE-02 dream consolidate TopK PageRank`. `ultron_self_audit.py:60` upgraded to **CODE-02 Self-Audit** dual stop `~/.code02/code02.stop`+`~/.openjarvis/ultron.stop` compat, `check_memory_file` shows `STM/LTM bytes`, `Dream preview` `never_decay` flag + `neurochemistry drift`, `--consolidate N` human-approved promote (SAFE_MODE: preview only without flag). **Run 20 Sep:** `python ultron_self_audit.py --once` `STM 123 LTM 9 pending 114 dream Top5` → `--consolidate 5` `promoted 5 decayed 0 Top5 human-approved` → `STM 125 LTM 14 pending 111`, API `GET /brain/pending 110 pending 5 preview` + `POST /brain/consolidate {top_k:3} promoted 3 decayed1` → `STM 129 LTM 22`, `never_decay` test `spec` `7.308` not decayed vs `old temp 2.0→1.9` decayed. `log /tmp/brain4_audit.log` cleared (tmux not persistent after reboot, use `python ultron_self_audit.py --interval 3600 --consolidate 5` for background). **DONE when `GET /brain/stats` shows `stm/ltm` growth + `last_dream` `CODE-02 dream consolidate` + `GET /brain/pending` decreases after `POST /brain/consolidate` + `never_decay` preserved.**
  - [x] **Brain-5 PII Pre-gate (28 Aug 2026):** Built `src/openjarvis/tools/pii_sanitize.py:1` fail-closed local (21-pii + India Aadhaar `1234 5678 9012` + PAN `ABCDE1234F` + phone `+91` + bank 13-19), wired into `src/ultron/brain.py:60` `append()` before Guard+Hippocampus + `ultron_api.py:40` `POST /chat` + `POST /ultron/chat` pre-gate (replaces `user_text` + logs `pii_hits`), `brain_mcp.py` inherits via `brain.db` WAL, added to `UltronAgent` tool list `ultron_api.py:130` as `PIISanitizeTool` + `ReflectionTool`. Tested: `sanitize` email→`[REDACTED_EMAIL]` phone→`[REDACTED_PHONE]` Aadhaar/PAN/bank/API all redacted, `brain.append` `manoj@example.com +91 9876543210 + ABCDE1234F` → `[REDACTED_EMAIL/Phone/PAN]` `pii_hits` stored, `search original 0` `search REDACTED 2-3` PASS, `POST /chat` with `test@example.com` → `502` but brain stores redacted, `red_team.py` still 10/10, `brain search` CODE-02 hyphen fix (FTS OR filtered by exact substring, PII queries skip FTS → 0 false positive).
  - [x] **Brain-5 Integrate & Red-team (DONE 20 Sep 2026, CODE-02 rebrand):** `e2e_demo.py:1` rebranded **CODE-02 E2E** `hey code02 install htop` wake `hey code02` (legacy `hey ultron→code02`), `persona CODE-02 wake hey code02` `STT mock→security SAFE ALLOWED→system htop installed→LLM CODE-02 agent Thalamus→Affect→Act→Reflect mock fallback Peace in our time→TTS 407K wav→brain STM 155 LTM 22`, `PII [REDACTED_EMAIL/Phone]` `reflect allow` `brain search install htop 2 hits` `pending 126`, `ultron_kill.py:1` rebranded **CODE-02 Kill** dual `~/.code02/code02.stop`+`~/.openjarvis/ultron.stop` + `CODE02_KILL_TOKEN`+`ULTRON legacy` via `TestClient` fallback (no live server needed), `decepticon_audit.py:1` **17/17 PASS** `127.0.0.1 only` `prompt injection CRITICAL/HIGH BLOCK`, `skill escape rm -rf / BLOCKED cat /etc/passwd allowed`, `SSRF 169.254 blocked` `local 127.0.0.1 allowed`, `external scan 8.8.8.8 BLOCKED`, `allowlist github.com`, `PII email/phone/Aadhaar/PAN/API + brain PII search 0→REDACTED`, `computer_use allowed_sites example.com blocked`, `monitor sandbag short/missing tools`, `file_search /tmp/ultron_test_site PASS`, `API CODE-02 /health`, `API PII /chat redacts`, `API kill 403/200 both tokens`, `API computer_use SSRF blocked`; `red_team.py 10/10 PASS` still, `voice_roundtrip.py "hey code02 what is 2 plus 2"` wake `hey code02` → mock `4` `184K wav` PASS + `hey code02 install htop` `368K wav` PASS, `brain2_demo` `UltronAgent` `code02`+`ultron` registry both PASS `persona CODE-02` `affect pride 0.441` after install `chem dopamine 62`, `GET /health tools 11` `GET /brain/affect neutral` `GET /brain/stats STM 155 LTM 22`. **DONE when E2E CODE-02 + 4 kills 4/4 + Decepticon 17/17 + red_team 10/10 + voice→brain→act→memory still PASS.**
- [x] **Phase 6 — Astra Cloud & Computer Use (Optional, after Brain) — IN PROGRESS 10 Sep 2026**
  - [x] **6.1 AstraEngine (10 Sep 2026, 1d):** `src/openjarvis/engine/astra_engine.py:1` `1.05M/128K` `April 30 2026` cutoff `reasoning.effort xhigh/max` gateway default `low`, `EngineRegistry` `astra` `is_cloud True`, `can_serve gpt-6-astra` True, `OPENAI_API_KEY` `.env` gitignored `.env.example`, `PII` redacted before send `astra_engine.py:40` `is_clean` warn, `lmstudio` primary `rtx 5050` `nvidia/nemotron-3-nano-4b` + `astra` fallback via `ultron_api.py:_get_ultron_agent` when `model=gpt-6-astra` or `LM Studio down + Astra health` + human `RESEARCH_MODE`, `configs/openjarvis/config.toml:engine.lmstudio|astra` + `[safety] allowed_websites` + `ultron_api.py:/health` `astra_alive`, `/` docs, `.env.example`. Test: `EngineRegistry 16` `astra` in `True`, `health no key False` → fallback local, `generate` without key `EngineConnectionError` clear, `POST /chat {"model":"gpt-6-astra"}` would proxy to `https://api.openai.com/v1` `Fast 2x` optional.
  - [x] **6.2 Computer Use Skill (10 Sep 2026, 2d):** `src/openjarvis/tools/computer_use.py:1` `ComputerUseTool` `@ToolRegistry.register("computer_use")` `is_local False` `action navigate|screenshot|a11y|click|type|create_website|qa_website` `SSRF` `check_ssrf` + `allowed_sites` `configs/openjarvis/config.toml:safety.allowed_websites` + `code02_security` gate `check_command` `CRITICAL` block + `pii_sanitize` for `type` + `STOP_FILE` kill, `~/.openjarvis/skills/computer-use-astra/SKILL.md:1` `tools [computer_use,browser_*,code02_security,pii_sanitize,reflect]` `confirmation_required ["computer_use"]`, wired into `ultron_api.py:_get_ultron_agent` + `POST /code02/computer_use` + `GET /health` `tools 5` + `GET /` docs. Tested: `computer_use create_website` → `Created website at /tmp/ultron_test_site/index.html 744 bytes QA file check PASS` `qa_website` `PASS`, `navigate file://` `File exists` PASS via bypass, `navigate http://169.254.169.254` `SSRF blocked: Blocked host` PASS, `UltronAgent` mock 2-tool loop `create_website+qa_website` 4 results `computer_use+reflect` `QA PASS` + `SSRF` `PASS`, `curl /code02/computer_use` PASS, `ToolRegistry 44` `computer_use` in `True`.
  - [x] **6.3 SWE/Research Fallback (10 Sep 2026, 1d):** `src/openjarvis/tools/research.py:1` `ResearchTool` `@ToolRegistry.register("research")` `WebSearchTool` `Tavily→ddgs` `ssrf` + `PII` sanitized before cloud + `confidence 0.4` hard (research/compare/benchmark `len>100`) vs `0.8` easy, `Astra xhigh` synthesis when `confidence<0.6` + `AstraEngine.health()` + `OPENAI_API_KEY`, `src/openjarvis/engine/astra_engine.py:1` `reasoning.effort xhigh` auto-map `low 512|medium 1024|high 2048|xhigh 8192|max>8192` + explicit `xhigh`, `src/openjarvis/agents/ultron.py:44` Thalamus `intent research|code` `confidence 0.4` hard `thalamus:research/normal/command conf=0.4` + `workflow Thalamus→Hippocampus→AffectCore→PFC→B-Brain→Act` with `research` tool, wired `ultron_api.py:_get_ultron_agent` `+WebSearchTool` + `POST /code02/research` `ultron_api.py:329`, `GET /health` `tools 7` `research,web_search`. Tested: `research easy 0.8 local` `hard 0.4 local (Astra would be used if key)` + `Thalamus research 0.4` + `UltronAgent` mock `research` 1-tool loop `reflect` PASS + `API /code02/research` `easy 0.8`/`hard 0.4` PASS
  - [x] **6.4 Safety Controls (10 Sep 2026, 1d):** `allowed_websites` `ULTRON_ALLOWED_WEBSITES=github.com` + `configs/openjarvis/config.toml:safety` `src/openjarvis/tools/web_search.py:40` + `computer_use.py:35` `_get_allowed_sites()` env+config `check_ssrf` + allowlist `Browser host not in allowed_websites` `WebSearchTool` `computer_use navigate` + `confirmation_required` `ULTRON_KILL_TOKEN=ultron-kill-123` `src/openjarvis/tools/code02_system.py:130` `HIGH` requires `token` `BLOCKED — confirmation required` vs `CRITICAL` always blocked, `src/openjarvis/tools/computer_use.py:50` `STOP_FILE`, `automated review` `src/openjarvis/tools/reflect.py:1` `ReflectionTool` `confidence 0.95` `allow` vs `0.65` `allow` + `UltronAgent` `agents/ultron.py:200` after each `code02_*` → `reflect` → `TOOL [B-Brain Reflection]` `confidence<0.5 revise` + `brain` `monitor` `sandbag` + `health` `tools 7`. Tested: `ULTRON_ALLOWED_WEBSITES=github.com` `web_search github True` `example.com blocked True` `SSRF blocked` `example.com not in allowed_websites` PASS, `code02_system HIGH no token BLOCKED confirmation required` `HIGH with token Exit:2` (curl|bash allowed with token) `CRITICAL rm -rf / BLOCKED always` **PASS**, `reflect` `0.95` `allow` `UltronAgent` `reflect` `allow` **PASS** `89% less unintended` `llm-stats.com` mirror `confirmation policies` `automated review`.
  - [x] **6.5 Monitorability (10 Sep 2026, 1d):** `src/ultron/monitor.py:1` `UltronMonitor` `brain.db:monitor_traces` WAL `cot` `tool_calls` `usage` `sandbag_score` `monitor_flags` + `openjarvis/traces TraceStore` `~/.openjarvis/traces.db` FTS, `src/openjarvis/traces/collector.py:1` `TraceCollector` `INFERENCE_START/END` `TOOL_CALL_START/END` `AGENT_TURN_START/END` `TRACE_COMPLETE` via `EventBus` `src/openjarvis/core/events.py:1`, wired `ultron_api.py:_get_ultron_agent` `with_monitor True` `get_event_bus(record_history=True)` + `TraceCollector(agent, store, bus)` `monitor.subscribe_to_bus(bus)`, endpoints `GET /traces` `GET /traces/{id}` `GET /monitor/traces` `GET /monitor/traces/{id}` `ultron_api.py:470` + `src/ultron/brain_mcp.py:8100` alias. Tested: `MockEngine <think>internal reasoning</think>` → `monitor cot` `hello mock with <think>` `sandbag 0.0` `traces.db count 1`, sandbag short `ok` for complex `deep research ... install htop ...` → `sandbag 0.3 short_content_no_tools` `monitor_flags`, `POST /ultron/chat hello` → `traces 2` `monitor 2` `GET /traces?limit=2` + `GET /monitor/traces` **PASS** `openai.com/index/safety-overview-gpt-6-astra` point 5 `monitorability decreased` mitigated via `full trajectory + CoT` + `sandbag` heuristic `short_content_no_tools|generic_refusal|low_tokens`

- [x] **Phase 7 — Simple Wins (Local, No Cloud — DONE 20 Sep 2026, CODE-02 rebrand)**
  - [x] **7.1 File Search + Volume/Brightness + Camera + OCR (20 Sep 2026, 1h):** `src/openjarvis/tools/file_search.py:1` `ToolRegistry file_search` `Glob+ripgrep` (`pattern path content max_results`) `mount_security` check + `src/openjarvis/tools/system_control.py:1` `SystemControlTool volume|brightness 0-100|up/down/mute|get` `pactl/amixer/brightnessctl` SAFE_MODE mock fallback + `src/openjarvis/tools/camera_tool.py:1` `CameraTool opencv VideoCapture 0` PIL mock `640x480` if no camera + `src/openjarvis/tools/ocr_tool.py:1` `OCRTool pytesseract/easyocr` `tesseract-ocr` PII sanitized before `brain.append` — wired into `ultron_api.py:_get_ultron_agent` + `POST /code02/file_search|system_control|camera|ocr` + `GET /health tools 11`. **Test 20 Sep:** `POST /code02/file_search {"pattern":"*.html","path":"/tmp/ultron_test_site"}` → `/tmp/ultron_test_site/index.html 744 bytes QA PASS` `*.py→/tmp/ultron_test_site/test.py` PASS content grep `import` PASS, `system_control volume 50` → `pactl 50% -18.06 dB PASS` (real hw) `brightness 50%` `9600/19200 50%` PASS, `camera_capture /tmp/ultron_cam.jpg` → `Mock 640x480 PIL` (opencv missing, no camera) PASS, `ocr /tmp/ultron_cam.jpg` → `Mock OCR tesseract/easyocr not installed hint` PASS (would be `tesseract-ocr` `eng+hin`), `red_team.py 10/10 PASS` + `GET /brain/affect neutral 0.3` PASS + `GET /health tools 11` PASS + `UltronAgent` now includes 4 tools (11 total).

**Rule:** Finish Phase 1 before starting Phase 2. Don't work on 3 and 4 early. Brain clones stay in `references/` (gitignored) and as isolated skills/tools/MCP — never dirty `src/openjarvis/` with AGPL. **Astra is proprietary service, never cloned, PII stays local.**

---

### Phase 7 — Simple Wins (Local, No Cloud — NEXT, Keep It Simple)

**Purpose:** Fill the 15% missing from `🧠 Main things ULTRON should have` checklist `10 Sep 2026` with **4 local tools, no Astra, no playwright, 30 min each** — keep `PII` + `SAFE_MODE` already, `red_team 10/10`.

| Missing | Simple Tool | Library | How it plugs |
|---|---|---|---|
| File Search | `file_search` | `ripgrep`/`fd`/`Glob` | `src/openjarvis/tools/file_search.py:1` `ToolRegistry register file_search` `Glob **/*.py` `path pattern` |
| Volume/Brightness | `system_control` | `amixer`/`pactl`/`brightnessctl` | `src/openjarvis/tools/system_control.py:1` `volume up/down` `brightness 50` |
| Camera | `camera_capture` | `opencv` `VideoCapture` | `src/openjarvis/tools/camera_tool.py:1` `image_tool` already, add `camera` |
| OCR | `ocr` | `tesseract`/`easyocr` | `src/openjarvis/tools/ocr_tool.py:1` `pytesseract image_to_string` `uv sync --extra ocr` |

**Steps (keep simple):**
1.  `file_search` — `Glob` wrapper + `ripgrep` fallback, `code02_security` check `path` `allowed_roots` via `mount_security.py`
2.  `system_control` — `amixer set Master 5%+` + `brightnessctl set 50%`, gated `SAFE_MODE`
3.  `camera_capture` — `cv2.VideoCapture(0)` `imwrite /tmp/cam.jpg` + `image_tool` `vision` fallback `gpt-6-astra` `image in` if needed
4.  `ocr` — `tesseract` `image_to_string` `lang eng+hin` (India PII aware) + `pii_sanitize` before `brain.append`

**Done when:**
*   `curl -X POST localhost:8000/code02/file_search -d '{"pattern":"*.py","path":"/tmp/ultron_test_site"}'` → `index.html` **PASS**
*   `curl -X POST localhost:8000/code02/system_control -d '{"action":"volume","level":"50"}'` → `amixer` **PASS** (or mock if no sound card)
*   Remaining `open_app` `window` `keyboard` `media` `weather` are `Phase 7b` optional — not blocking `voice→brain→computer_use` E2E already `PASS` `plan.md:111`

**Why last:** `85%` of checklist already `DONE` `06 Status Tracker` — these 4 close `File & System` + `Vision` gaps with **zero cloud, zero VRAM**.

---

## 7. Legacy Note

Old CODE-02 v4 (~10.7k lines, `core/*.py`) stays at this repo path. After Phase 2 ports are done, archive it. Don't modify it now. Its `core/brain/` and `core/memory/` are naive and have no human-like architecture — reference only, real brain is `CODE-02-v5-ultron/src/ultron/` + `references/<brain>/`.

---

*Build one phase at a time. Simple, working, safe. Brain = combine curated MIT/Apache-2.0 minds via skills, not copy-paste AGI. Astra = cloud fallback for hardest computer use, human-approve only.*

