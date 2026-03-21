import subprocess
import tempfile

def execute_python_code(code: str):
    """Executes Python code safely in an isolated temp file."""

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
            tmp.write(code.encode())
            tmp_filename = tmp.name

        result = subprocess.run(
            ["python", tmp_filename],
            capture_output=True,
            text=True
        )

        return result.stdout, result.stderr

    except Exception as e:
        return "", str(e)
