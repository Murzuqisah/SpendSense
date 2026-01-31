#!/usr/bin/env python3
"""
SpendSense Web Application Runner
Simple entry point for running the Flask web server
"""

import sys
import os
from argparse import ArgumentParser

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.web_app import run_app


def main():
    """Main entry point for web application"""
    # Get environment variables for deployment
    env_port = os.environ.get("PORT")
    env_host = os.environ.get("HOST", "127.0.0.1")
    
    parser = ArgumentParser(description="SpendSense Web Application")
    parser.add_argument(
        "--host", default=env_host, help=f"Host to bind to (default: {env_host})"
    )
    parser.add_argument(
        "--port", type=int, default=int(env_port) if env_port else 5000, 
        help="Port to bind to (default: 5000 or $PORT if set)"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument(
        "--prod", action="store_true", help="Production mode (disables debug)"
    )

    args = parser.parse_args()

    # Determine debug mode
    debug = args.debug and not args.prod

    # Run the application
    try:
        run_app(host=args.host, port=args.port, debug=debug)
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error running application: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
