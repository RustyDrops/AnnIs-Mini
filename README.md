# AnnIs Lives: Agentic Pico 2W Autonomous Entity

An autonomous, multi-agent system running on the Raspberry Pi Pico 2W. This bot uses a delegation loop to orchestrate specialized subagents for research, coding, UI design, and system auditing.

## Features
- **Agentic Delegation**: Main Agent (Gemini 3.1) can create multi-step plans and delegate to subagents.
- **Plan Scratchpad**: Efficiently shares pertinent information between plan steps using a transient scratchpad, avoiding context bloat by up to 90%.
- **Dynamic Tool Loading**: Uses a lightweight "Lite" schema for the main loop, dynamically attaching advanced tools only when specialized subagents are activated.
- **Indexed Memory System**: Uses a **Tag-Based Inverted Index** for OOM-safe, instant memory retrieval on flash.
- **Aggressive Context Management**: 
  - **Auto-Summarization**: Compresses history after 12 messages.
  - **Task Boundaries**: Automatically wipes casual chat history when a new Plan starts.
  - **Shorthand Commands**: Use `~cnew` to clear context or `~c <turns>` to keep the last X turns.
- **Specialized Subagents**: Subagents (Research, Coding, etc.) now receive the **Original Goal** and highly-tailored system instructions for better accuracy.
- **Financial Observability**: 8-decimal precision budget tracking per agent ($0.25/day budget). Slimmed system instructions for cheaper conversational turns.

## Setup
1. Rename `secrets_template.py` to `secrets.py`.
2. Add your `GEMINI_API_KEY`, `TELEGRAM_TOKEN`, and `CHAT_ID`.
3. Create the required directory structure:
   - `data/human_queue/`
   - `data/memory/`
4. Flash the files to your Pico 2W (MicroPython 1.24+).
5. Run `main.py`.

## Commands
- `~ping`: Health Check & RAM status.
- `~budget`: Detailed spending breakdown.
- `~cnew`: Clear conversation context.
- `~c <num>`: Keep only the last <num> turns.
- `~reboot`: Restart the Pico.
- `~help`: List all commands.

## License
MIT
