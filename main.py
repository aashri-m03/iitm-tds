from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import sys
from io import StringIO
import traceback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    code: str

class CodeResponse(BaseModel):
    error: List[int]
    result: str

def execute_python_code(code: str):
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        exec(code)
        output = sys.stdout.getvalue()
        return True, output
    except Exception:
        output = traceback.format_exc()
        return False, output
    finally:
        sys.stdout = old_stdout


def extract_line_from_traceback(tb: str):
    import re
    match = re.search(r'line (\d+)', tb)
    return [int(match.group(1))] if match else []


@app.post("/code-interpreter", response_model=CodeResponse)
def run_code(req: CodeRequest):
    success, output = execute_python_code(req.code)

    if success:
        return {"error": [], "result": output}

    # No AI needed (cheaper + safer)
    lines = extract_line_from_traceback(output)

    return {"error": lines, "result": output}
