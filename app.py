#!/usr/bin/env python3
"""EasySunSystem - Solar power plant monitoring.

Usage:
    python app.py                  # Normal mode (requires Modbus connection)
    python app.py --simulate       # Simulation mode (no hardware needed)
    python app.py --simulate -p 8080  # Simulation on port 8080
"""
import argparse
import logging

from waitress import serve
from easysun import create_app


def main():
    parser = argparse.ArgumentParser(description="EasySunSystem Monitoring")
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Run in simulation mode (no Modbus connection needed)",
    )
    parser.add_argument(
        "-p", "--port", type=int, default=None, help="Server port (default: 5000)"
    )
    parser.add_argument(
        "--host", type=str, default=None, help="Server host (default: 0.0.0.0)"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    overrides = {}
    if args.simulate:
        overrides["SIMULATION_MODE"] = True
        logging.info("Running in SIMULATION mode")
    if args.port:
        overrides["PORT"] = args.port
    if args.host:
        overrides["HOST"] = args.host

    app = create_app(overrides)

    host = app.config["HOST"]
    port = app.config["PORT"]
    logging.info("Starting EasySunSystem on %s:%d", host, port)
    serve(app, host=host, port=port)


if __name__ == "__main__":
    main()
