from src.core.run_config import RunConfig
from src.core.run_context import RunContext

__all__ = ["RunContext", "RunConfig", "TestOrchestrator"]


def __getattr__(name: str):
    if name == "TestOrchestrator":
        from src.core.orchestrator import TestOrchestrator

        return TestOrchestrator
    raise AttributeError(name)
