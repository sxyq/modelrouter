#!/usr/bin/env python3
"""Use the maintained training page through the existing dashboard entry point."""
if __package__:
    from .build_clean_chart_dashboard import main
else:
    from build_clean_chart_dashboard import main


if __name__ == "__main__":
    main()
