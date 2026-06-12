from typing import Dict, Type
from core.experiment import Experiment

_REGISTRY: Dict[str, Type[Experiment]] = {}

def register(name: str, cls: Type[Experiment]) -> None:
    _REGISTRY[name] = cls

def get(name: str) -> Type[Experiment]:
    if name not in _REGISTRY:
        raise ValueError(f"Unbekanntes Experiment: {name}")
    return _REGISTRY[name]

def list_all() -> Dict[str, Type[Experiment]]:
    return _REGISTRY
