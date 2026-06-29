from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GeoProviderError(Exception):
    message: str
    status_code: int = 502

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True, slots=True)
class GeoProviderConfigurationError(GeoProviderError):
    status_code: int = 503


@dataclass(frozen=True, slots=True)
class GeoProviderRequestError(GeoProviderError):
    status_code: int = 502


@dataclass(frozen=True, slots=True)
class GeoProviderValidationError(GeoProviderError):
    status_code: int = 400
