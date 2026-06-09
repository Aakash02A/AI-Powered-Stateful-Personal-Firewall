"""
sentinelx_shared — shared package for all SentinelX microservices.
"""
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("sentinelx-shared")
except PackageNotFoundError:
    __version__ = "dev"

__all__ = ["__version__"]
