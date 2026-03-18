"""CLI for fambudget."""
import sys, json, argparse
from .core import Fambudget

def main():
    parser = argparse.ArgumentParser(description="FamBudget — Family Budget Optimizer. AI-powered household budget optimization and savings recommendations.")
    parser.add_argument("command", nargs="?", default="status", choices=["status", "run", "info"])
    parser.add_argument("--input", "-i", default="")
    args = parser.parse_args()
    instance = Fambudget()
    if args.command == "status":
        print(json.dumps(instance.get_stats(), indent=2))
    elif args.command == "run":
        print(json.dumps(instance.process(input=args.input or "test"), indent=2, default=str))
    elif args.command == "info":
        print(f"fambudget v0.1.0 — FamBudget — Family Budget Optimizer. AI-powered household budget optimization and savings recommendations.")

if __name__ == "__main__":
    main()
