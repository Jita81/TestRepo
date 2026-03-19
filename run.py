#!/usr/bin/env python3
"""Start the Context Engineering Platform web server."""

import os
import sys
from pathlib import Path


def main() -> None:
    Path("data").mkdir(exist_ok=True)
    Path("templates").mkdir(exist_ok=True)

    try:
        import uvicorn
    except ImportError:
        print("Install dependencies: pip install -r requirements.txt", file=sys.stderr)
        sys.exit(1)

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    print(f"Context Engineering Platform → http://{host}:{port}/context")
    print(f"OpenAPI → http://{host}:{port}/docs")
    uvicorn.run("main:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
