# schemas.py
import micropython

# Centralized tool definitions
TOOLS_SCHEMA = [
    {
        "function_declarations": [
            {
                "name": "research",
                "description": "Delegates complex research tasks to a specialized subagent with Google Search access.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The specific topic or question to research."
                        },
                        "depth": {
                            "type": "string",
                            "description": "Desired depth of information (e.g., 'concise', 'detailed')."
                        },
                        "thinking_level": {
                            "type": "string",
                            "enum": ["minimal", "low", "medium", "high"],
                            "description": "Amount of reasoning power to assign (default: medium)."
                        }
                    },
                    "required": ["topic"]
                }
            },
            {
                "name": "code_skill",
                "description": "Delegates coding, tool improvement, or skill creation tasks to a specialized coding subagent.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": "The coding task to perform (e.g., 'create a math tool', 'improve error handling')."
                        },
                        "context": {
                            "type": "string",
                            "description": "Any additional code context or requirements."
                        },
                        "thinking_level": {
                            "type": "string",
                            "enum": ["minimal", "low", "medium", "high"],
                            "description": "Amount of reasoning power to assign (default: high)."
                        }
                    },
                    "required": ["task"]
                }
            },
            {
                "name": "create_plan",
                "description": "Generates a multi-step execution plan for complex objectives. Use this to initiate autonomous action. DO NOT ask for permission, just create the plan and execute it.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "steps": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "agent": {
                                        "type": "string",
                                        "enum": ["research", "coding", "ui", "creative", "audit"],
                                        "description": "The subagent to use for this step."
                                    },
                                    "task": {
                                        "type": "string",
                                        "description": "Specific instruction for this step."
                                    },
                                    "thinking_level": {
                                        "type": "string",
                                        "enum": ["minimal", "low", "medium", "high"],
                                        "description": "Reasoning power for this step."
                                    }
                                },
                                "required": ["agent", "task"]
                            }
                        }
                    },
                    "required": ["steps"]
                }
            },
            {
                "name": "design_ui",
                "description": "Designs visual layouts for LCD/OLED displays.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "objective": {"type": "string", "description": "What to display (e.g., 'Weather dashboard')."},
                        "thinking_level": {"type": "string", "enum": ["minimal", "low", "medium", "high"]}
                    },
                    "required": ["objective"]
                }
            },
            {
                "name": "write_headline",
                "description": "Generates punchy headlines or notifications.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Text to summarize into a headline."},
                        "style": {"type": "string", "enum": ["punchy", "formal", "funny", "urgent"]}
                    },
                    "required": ["content"]
                }
            },
            {
                "name": "audit_system",
                "description": "Performs a system health and budget audit.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "thinking_level": {"type": "string", "enum": ["minimal", "low", "medium", "high"]}
                    }
                }
            },
            {
                "name": "search_memory",
                "description": "Searches the persistent memory using exact tags.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": ["research", "ideas", "knowledge"],
                            "description": "The memory category to search."
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "A list of tags to search for in the index."
                        }
                    },
                    "required": ["category", "tags"]
                }
            },
            {
                "name": "update_directives",
                "description": "Appends a new persistent behavioral directive to the system (secondary settings).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directive": {
                            "type": "string",
                            "description": "The rule or instruction to add (e.g., 'Give smaller responses')."
                        }
                    },
                    "required": ["directive"]
                }
            },
            {
                "name": "save_skill",
                "description": "Saves a MicroPython script to the 'data/skills/' directory for future use.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Filename (e.g., 'weather_logger.py')."
                        },
                        "code": {
                            "type": "string",
                            "description": "The full MicroPython code content."
                        }
                    },
                    "required": ["name", "code"]
                }
            }
        ]
    }
]

TOOLS_LITE_SCHEMA = [
    {
        "function_declarations": [
            f for f in TOOLS_SCHEMA[0]["function_declarations"]
            if f["name"] in ["create_plan", "research", "code_skill", "audit_system", "design_ui", "write_headline", "save_skill", "update_directives"]
        ]
    }
]

TOOLS_CODING_SCHEMA = [
    {
        "function_declarations": [
            f for f in TOOLS_SCHEMA[0]["function_declarations"]
            if f["name"] in ["save_skill", "update_directives"]
        ]
    }
]

TOOLS_RESEARCH_SCHEMA = [
    {
        "function_declarations": [
            f for f in TOOLS_SCHEMA[0]["function_declarations"]
            if f["name"] in ["search_memory"]
        ]
    }
]
