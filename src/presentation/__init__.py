"""
Presentation Layer.

Contains HTTP/API presentation for bounded contexts.

Structure:
- http/contexts/{context}/ - Context-specific presentation
  - container.py - DI container
  - module.py - Handler registrations
  - routes.py - API routes
  - controllers/ - Controllers
  - schemas/ - Request/Response schemas
"""
