"""API layer — HTTP/WebSocket transport. Contains NO business logic.

Routers validate input (Pydantic), resolve dependencies (DI) and delegate to
application services, then map results back to response schemas.
"""
