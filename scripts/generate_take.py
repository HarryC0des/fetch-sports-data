#!/usr/bin/env python3
"""
CLI Script: Generate AI-Powered Sports Takes

Usage:
    python -m scripts.generate_take
"""
from src.ai_generator import generate_take

if __name__ == "__main__":
    print("[INFO] Starting take generation...")
    generate_take()
    print("[INFO] Generation complete.")
