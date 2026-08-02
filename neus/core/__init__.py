"""Core package for neus-agi-system."""

try:
	# Preferred: relative import when used as a package
	from .neus_system import NeusSystem
except (ImportError, ModuleNotFoundError):
	# Fallback: absolute import for environments that run the module directly
	from neus_system import NeusSystem

__all__ = ["NeusSystem"]
