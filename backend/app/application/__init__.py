"""Application layer — use cases that orchestrate the domain via its ports.

Depends on the domain only. Knows nothing about FastAPI, SQLAlchemy or Redis; it
receives port implementations by constructor injection (wired in app/api/deps.py).
"""
