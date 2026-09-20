# CODE-02 Next Plan — From resourse.txt (18 projects → O2 parts)

> **Goal:** Close the last local gap: `espeak` → human voice, `fuzzy hey code02` → real wake, `xdotool X11` → Wayland, `mock browser` → real browser, `hand-rolled 7-phase` → durable graph, while keeping `CODE-02 v5.2.0` `20/20 PASS` `16 tools` local.

> **Constraint:** `v5.2.0-code02` already `brain.db` `~/.code02/brain.db` `affect` `decepticon 17/17` `red_team 10/10`. Don't break it. Each phase is **1 tool + 1 test**, never `>1GB` extra.

---

## Current → Target

| Part | Now (`CODE-02 v5.2.0`) | Target (from `resourse.txt:508`) | Why |
|---|---|---|---|
| Core arch | `OpenJarvis` fork 8 agents | **Leon skill spec** `resourse.txt:7` | Lean `skills` + `memory` + `tool` spec beats 8-agent confusion |
| Brain wiring | `src/openjarvis/agents/ultron.py:1` 382-line loop | **LangGraph StateGraph** `resourse.txt:97` `UNDERSTAND→PLAN→EXECUTE→VERIFY` | Persistence + human approval + streaming |
| Memory | `src/ultron/brain.py:1` SQLite `STM→LTM` custom | **Letta blocks** `resourse.txt:28` | Stateful `Core + Archival` + identity, already cloned `references/letta` |
| STT | `faster-whisper` `tiny 75M`/`base 142M` `voice_pipeline.py:15` | **Keep** vs `whisper.cpp` `resourse.txt:251` | `faster-whisper` faster on `RTX 5050`, benchmark only |
| TTS | `espeak -w` `voice_pipeline.py:50` robotic 54K wav | **Piper** `resourse.txt:299` `en_US-lessac-medium` | Human voice, local, `persona.json:35` already planned |
| Wake | `WAKE_WORDS ["hey code02"]` fuzzy `voice_pipeline.py:72` | **openWakeWord** `resourse.txt:324` `hey code02` `.tflite` | Robust, `Hey I'll install H-top` false trigger `voice_pipeline.py:90` fixed |
| Linux control | `xdotool`/`wmctrl` `window_tool.py:1` `keyboard_tool.py:1` X11 | **ydotool** `resourse.txt:358` Wayland | `Hyprland/Wayland` requires `ydotool`, `xdotool` fails |
| Browser | `computer_use.py:1` mock `navigate` | **Browser Use** `resourse.txt:191` + **open-browser-use** `220` `playwright` CDP | Real `click/type` + existing Firefox session |
| Execution | `code02_system.py:1` `bash` gating | **Open Interpreter** pattern `resourse.txt:132` `approval+docker` | Per-tool `confirm` + `docker` cell |
| Protocol | ad-hoc `voice_roundtrip.py:1` `TTS→STT→wake→brain→TTS` | **Wyoming** `resourse.txt:422` | Clean `Wake→STT→O2→TTS` pipeline |

---

## Phases — 1 tool at a time, local first

### Phase 8.1 — Piper TTS (1 day, 50MB, no VRAM)

**Purpose:** Replace `espeak` robotic with human neural voice, keep `espeak` fallback.

Steps:
1. `uv sync --extra tts` add `piper-tts` `50MB` `en_US-lessac-medium.onnx` to `~/.cache/piper/`, keep `espeak` at `voice_pipeline.py:50` as fallback
2. `voice_pipeline.py:50` `tts_piper(text, wav, voice="en_US-lessac-medium")` → `piper --model en_US-lessac-medium.onnx --output_file wav`, fallback to `tts_espeak` if `piper` not installed
3. `voice_roundtrip.py:1` default `TTS piper` → `wav` `~200K` human vs `espeak 54K`
4. `persona.json:35` `tts_engine piper` now real, `configs/openjarvis/prompts/personas/code02.md` stays

Test:
* `python voice_pipeline.py "Hello CODE-02, system check"` → `piper wav ~200K` `PASS`, `espeak fallback` still `PASS` if `piper` missing
* `python voice_roundtrip.py "hey code02 what is 2 plus 2"` → `Piper TTS 200K → STT base → wake hey code02 → brain → Piper TTS PASS` + `red_team 10/10` + `GET /brain/affect neutral`

**Done when:** `voice_pipeline.py` produces `Piper` human voice `wav` and `espeak` still works as fallback, `voice_roundtrip 2+2` via `Piper` `PASS`.

---

### Phase 8.2 — openWakeWord hey code02 (1 day, 10MB, no VRAM)

**Purpose:** Replace fuzzy string `ultra_like` with model, fix `Hey I'll install H-top` false.

Steps:
1. `uv sync --extra wake` add `openwakeword` `10MB` `hey_code02.tflite` (train via `openwakeword` `colab` from `hey code02` 50 samples, or use `hey_jarvis` pretrained + `code02` threshold 0.5)
2. `voice_pipeline.py:72` `WAKE_WORDS` keep string list, add `detect_wake_oww(wav, threshold=0.5)` → `openWakeWord Model` `hey_code02` score `0.0-1.0`, fallback to `detect_wake` fuzzy if `oww` not installed or no mic
3. `voice_pipeline.py` keep `detect_wake` fuzzy `voice_pipeline.py:90` as fallback for `USE_REAL_STT=0` mock, new `USE_OWW=1` primary
4. `ultron_self_audit.py` logs `wake_model` `openWakeWord vs fuzzy`

Test:
* `python voice_pipeline.py --wake "hey code02 install htop"` → `hey code02 (oww 0.92)` `PASS`, `python voice_pipeline.py --wake "Hey I'll install H-top"` → `False` `PASS` (was `True` fuzzy)
* `USE_OWW=1 python voice_roundtrip.py "hey code02 install htop"` → `TTS piper → STT base → oww wake True 0.92 → brain 3 hits → mock install → Piper TTS PASS` + `red_team 10/10`

**Done when:** `openWakeWord hey_code02` `score>0.5` `PASS`, fuzzy no longer false-triggers `Hey I'll`, fallback still `PASS` without `oww` model.

---

### Phase 8.3 — ydotool Wayland (1 day, 0.5MB, no VRAM)

**Purpose:** Fix `xdotool` X11 failure on `Hyprland/Wayland` `resourse.txt:362`.

Steps:
1. `sudo pacman -S ydotool` (or `apt install ydotool`) + `systemctl --user enable ydotoold` check `ydotool` works `ydotool key 29:1 56:1` smoke
2. `src/openjarvis/tools/keyboard_tool.py:1` + `window_tool.py:1` add `ydotool` path: `has_ydotool = shutil.which("ydotool")`, priority `ydotool` > `xdotool` > `pynput` mock, keep all 3 fallback
3. `keyboard_tool.py` `action type` → `ydotool type --delay 10 "text"` `key` → `ydotool key 29:1`, `window_tool.py` `action focus` → fallback to `hyprctl dispatch focuswindow` if `ydotool` + `xdotool` fail (Hyprland native)
4. `ultron_api.py` `POST /code02/keyboard|window` unchanged, just new engine `ydotool`

Test:
* `ydotool type "hello code02"` via `KeyboardTool().execute(action="type",text="hello")` → `ydotool` `PASS` or mock `PASS` if no `ydotoold`
* `POST /code02/keyboard {"action":"type","text":"hello"}` `PASS` `POST /code02/window {"action":"list"}` `PASS` (via `hyprctl` or mock) + `red_team 10/10` + `GET /brain/affect neutral`

**Done when:** `Hyprland` `ydotool type` `PASS` (or mock `PASS` if `ydotoold` not running), `xdotool` still fallback on X11, `16 tools` → still `16` `GET /health` `PASS`.

---

### Phase 8.4 — Browser Use real (2 days, 200MB playwright, no VRAM)

**Purpose:** Replace `computer_use.py:1` mock `navigate` with `playwright` CDP real `click/type`, keep `allowed_sites` `SSRF` gating.

Steps:
1. `uv sync --extra browser` add `playwright` + `browser-use` `200MB` `playwright install chromium`, keep `computer_use.py` `SSRF` `code02_security` gate as is
2. `src/openjarvis/tools/browser_real.py:1` `BrowserUseToolReal` `@ToolRegistry.register("browser_real")` `playwright` `CDP` `screenshot → a11y tree → act` — borrow `browser-use` pattern `resourse.txt:191` but keep `Ultron` `allowed_sites` check before every `navigate`
3. `open-browser-use` pattern `resourse.txt:220` for existing Firefox: `playwright` `chrome --remote-debugging-port=9222` `connect_over_cdp` to control **real** session (WhatsApp/Gmail logins)
4. `computer_use.py:1` keep mock `create_website` `qa_website` for offline demo, new `browser_real` for `navigate|clic|type` real, both behind `KILL_TOKEN` `confirmation_required ["browser_real"]`

Test:
* `ToolRegistry browser_real` `PASS`, `browser_real navigate https://example.com` → `Playwright title Example Domain` `PASS` (or mock if no `chromium`), `browser_real a11y` `PASS`
* `POST /code02/computer_use {"action":"navigate","url":"https://example.com"}` still `PASS` (mock), new `POST /code02/browser_real {"action":"navigate","url":"https://example.com"}` `PASS` (real)
* `decepticon 17/17` still `PASS` (`allowed_sites` still blocks `example.com` if `github.com` allowlist), `red_team 10/10`

**Done when:** `browser_real` `navigate` `PASS` real `playwright` title, `computer_use` mock still `PASS`, `allowed_sites` `SSRF` still `PASS`.

---

### Phase 8.5 — LangGraph StateGraph (2 days, 50MB, no VRAM)

**Purpose:** Replace `src/openjarvis/agents/ultron.py:1` 382-line loop with durable `UNDERSTAND→PLAN→EXECUTE→VERIFY` `resourse.txt:102`.

Steps:
1. `uv sync --extra graph` add `langgraph` `50MB` `langchain-core`, keep `ToolUsingAgent` stub as compat
2. `src/openjarvis/agents/code02_graph.py:1` `Code02Graph` `StateGraph` `State {input, thalamus, recall, affect, plan, tools, reflect, output}` nodes: `thalamus (intent) → hippocampus (recall) → affect (appraise) → plan (PFC) → execute (tools+code02_security) → reflect (B-Brain) → respond (Broca)` + `MemorySaver` `checkpoints` `SQLite` `~/.code02/graph.db` + `humanApproval` interrupt before `execute` if `HIGH` threat
3. `ultron_api.py:_get_ultron_agent` try `Code02Graph` first, fallback to `UltronAgent` if `langgraph` not installed, both expose `run(input)` same `AgentResult`
4. `brain.py` `working_set` → `MemorySaver` `checkpoint` migration path

Test:
* `Code02Graph run "hey code02 install htop"` → `Thalamus intent install → Plan -> execute code02_system -> reflect -> respond` `PASS` `8 turns` vs `UltronAgent` `PASS` (compat)
* `GET /traces` shows `LangGraph` `checkpoint` `PASS`, `red_team 10/10` + `decepticon 17/17` still `PASS`

**Done when:** `Code02Graph` `PASS` same `AgentResult` as `UltronAgent`, `checkpoints` persist `~/.code02/graph.db`, fallback to `UltronAgent` if `langgraph` missing.

---

### Phase 8.6 — Letta blocks (1 day, 50MB, optional)

**Purpose:** Replace custom `STM→LTM` `Top-K` with `Letta` `Core + Archival` + `MemFS git` `resourse.txt:28` (you already cloned `references/letta` 90M).

Steps:
1. `uv sync --extra letta` sidecar `letta` `50MB` `MCP` `127.0.0.1:8200` (isolated `uv venv`, not `src/ultron`)
2. `src/ultron/brain.py:1` keep SQLite `STM/LTM` primary, add `src/ultron/letta_sidecar.py:1` proxy `POST /brain/letta/remember` → `Letta` `Core blocks: persona, human, project`, `Archival: search`, `MemFS: git commit` — log to `brain.db` `dream_log` same `never_decay`
3. `ultron_api.py` `GET /brain/stats` adds `letta_blocks` count, `POST /brain/consolidate` optionally `letta` `Archival` if `PG` available, else SQLite

Test:
* `Letta remember "PhishGuard"` → `search "cybersecurity project"` → `PhishGuardAI` `PASS` (if `letta` sidecar running, else fallback SQLite `PASS`)
* `red_team 10/10` + `decepticon 17/17` still `PASS`

**Done when:** `Letta` `Core block` `PASS` or fallback SQLite `PASS`, no `50GB` clone, `PG` optional.

---

## Install order (don't install all)

```bash
# 1. Voice human (Piper) + Wake (openWakeWord) — biggest UX win, smallest risk
uv sync --extra tts --extra wake  # piper 50MB + openwakeword 10MB

# 2. Wayland (ydotool) — required for Hyprland
sudo pacman -S ydotool && systemctl --user start ydotoold

# 3. Browser real — 200MB playwright (only if you need real browsing)
uv sync --extra browser && playwright install chromium

# 4. Graph + Letta — only after 1-3 stable
uv sync --extra graph --extra letta  # langgraph 50MB + letta 50MB
```

**Never:** `AGPL` `worldmonitor`/`NEURON657` clone, `langchain` full (use `langgraph` only), `OpenHands` whole (study loop), `500-AI-Agents-Projects` all 22.

---

## Done when (final)

* `voice_roundtrip.py "hey code02 install htop"` → `Piper TTS human ~200K → faster-whisper base → openWakeWord hey code02 0.92 → brain recall → LangGraph Thalamus→Plan→Execute→Reflect → code02_system → Piper TTS PASS` (was `espeak 54K` + fuzzy)
* `curl -X POST localhost:8000/code02/window -d '{"action":"list"}'` → `hyprctl/ydotool PASS` on `Hyprland` (was `xdotool` fail)
* `POST /code02/browser_real {"action":"navigate","url":"https://example.com"}` → `playwright title PASS` (was mock)
* `GET /brain/stats` shows `stm/ltm` + `letta_blocks` + `graph checkpoints`, `red_team 10/10` + `decepticon 17/17` + `kill 4/4` + `e2e CODE-02` still `PASS`
* `GET /health` `tools 16→19` (adds `browser_real` + `graph` + `letta` sidecar), `~/.code02/brain.db` `WAL` `never_decay` preserved, `PII` local, `Astra` still fallback `xhigh`

*Build one phase at a time. Next ~100% local personal computer assistant, not chatbot. Start 8.1 Piper.*
