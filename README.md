# AnnIs Lives: Agentic Pico 2W Autonomous Entity

An autonomous, multi-agent system running on the Raspberry Pi Pico 2W. This bot uses a delegation loop to orchestrate specialized subagents for research, coding, UI design, and system auditing.

## Features
- **Agentic Delegation**: Main Agent (Gemini 3.1) can create multi-step plans and delegate to subagents.
- **Specialized Subagents**:
  - **Research Agent** (Gemini 2.5 Flash-Lite + Google Search)
  - **Coding Agent** (Gemini 3.1 Flash-Lite)
  - **UI Specialist** (Gemini 3.1 Flash-Lite)
  - **Creative Voice** (Gemini 2.5 Flash-Lite)
  - **System Auditor** (Gemini 3.1 Flash-Lite)
- **Automatic Memory Archiving**: Summarizes long conversations into "Knowledge Items" when context hits 20 messages.
- **Financial Observability**: 8-decimal precision budget tracking per agent.
- **Pico 2W Optimized**: Custom RAM safeguards, response truncation, and safe-save file operations.

## Setup
1. Rename `secrets_template.py` to `secrets.py`.
2. Add your `GEMINI_API_KEY`, `TELEGRAM_TOKEN`, and `CHAT_ID`.
3. Flash the files to your Pico 2W (MicroPython 1.24+).
4. Run `main.py`.

## Local Testing
Run `python main.py` on your PC to enter **Terminal Mode**. This uses a compatibility shim to simulate the Pico environment.

## License
MIT
