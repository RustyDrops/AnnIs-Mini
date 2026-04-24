import uos as os

def tool_read_file(filepath: str, max_lines: int = 50, start_line: int = 0) -> str:
    """Allows AI to read codebase chunk-by-chunk to save RAM."""
    try:
        with open(filepath, 'r') as f:
            for _ in range(start_line):
                if not f.readline():
                    return "EOF reached before start_line"
            
            lines = []
            for _ in range(max_lines):
                line = f.readline()
                if not line:
                    break
                lines.append(line)
            
            return "".join(lines)
    except Exception as e:
        return f"Error reading file: {e}"

def tool_write_file(filepath: str, content: str, mode: str = "w") -> str:
    """Allows AI to modify code or memory."""
    if filepath.endswith('.py'):
        try:
            compile(content, '<string>', 'exec')
        except SyntaxError as e:
            return f"SyntaxError: {e}"
            
    try:
        with open(filepath, mode) as f:
            f.write(content)
        return "Successfully wrote to file."
    except Exception as e:
        return f"Error writing file: {e}"
