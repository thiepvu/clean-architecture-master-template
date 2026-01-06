"""
DI Containers (Composition Root).

ApplicationContainer wires together:
- InfrastructureContainer (here)
- Context containers (here - Composition Root)

Context containers are defined here (bootstrapper layer) as this is the
Composition Root - the ONLY place allowed to import from all layers
(Domain, Application, Infrastructure) to wire dependencies.

Presentation layer receives pre-wired containers without knowing Infrastructure.
"""

from .application_container import ApplicationContainer
from .contexts import FileManagementContainer, UserManagementContainer
from .infrastructure_container import InfrastructureContainer

__all__ = [
    "ApplicationContainer",
    "InfrastructureContainer",
    "UserManagementContainer",
    "FileManagementContainer",
]
