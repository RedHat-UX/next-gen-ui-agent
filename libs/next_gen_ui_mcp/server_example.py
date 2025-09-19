#!/usr/bin/env python3
"""
Next Gen UI MCP Server Example.

This is a simple executable script that directly reuses the logic from __main__.py.
You can run this script directly to start the MCP server with all the same functionality but 'pants' used in this
GitHub repository manages for you the required dependencies.
This is only for purpose of running it locally and testing out with other renderers while still using pants.
For any other purpose, you should use the __main__.py file.

Usage:
    pants run libs/next_gen_ui_mcp/server_example.py --run-args="[options]"
    e.g. pants run libs/next_gen_ui_mcp/server_example.py --run-args="--transport sse --component-system rhds"

All command line options from __main__.py are supported.
"""

if __name__ == "__main__":
    # Import and call the main function from __main__.py
    from next_gen_ui_mcp.__main__ import main

    main()
