"""
Entrypoint for `python -m modelrouter`.
Directly dispatches to modelrouter.cli.main().
"""
from modelrouter.cli import main

if __name__ == "__main__":
    main()
