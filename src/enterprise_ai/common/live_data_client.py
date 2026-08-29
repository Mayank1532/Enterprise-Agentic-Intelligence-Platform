"""External live-data provider client."""

from typing import Any, Protocol

import httpx

from enterprise_ai.core.live_data import LiveData


class LiveDataProvider(Protocol):
    """Protocol for external live-data providers."""

    async def fetch(self, query: str) -> LiveData:
        """Fetch and normalize live data."""


class PublicLiveDataProvider:
    """Provider client for the public Open-Meteo API."""

    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    SOURCE_NAME = "Open-Meteo"
    SOURCE_URL = "https://open-meteo.com/"
    TIMEOUT_SECONDS = 10.0

    async def fetch(self, query: str) -> LiveData:
        """Fetch current temperature for a supported location query."""
        location = query.strip()

        if not location:
            raise ValueError("Live data query must not be empty.")

        coordinates = self._resolve_location(location)

        params = {
            "latitude": coordinates["latitude"],
            "longitude": coordinates["longitude"],
            "current": "temperature_2m",
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.TIMEOUT_SECONDS
            ) as client:
                response = await client.get(
                    self.BASE_URL,
                    params=params,
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"Live data provider request failed: {exc}"
            ) from exc

        try:
            payload: Any = response.json()
            temperature = payload["current"]["temperature_2m"]
            unit = payload["current_units"]["temperature_2m"]
        except (ValueError, KeyError, TypeError) as exc:
            raise RuntimeError(
                "Live data provider returned an invalid response."
            ) from exc

        return LiveData.create(
            query=location,
            value=f"{temperature} {unit}",
            source_name=self.SOURCE_NAME,
            source_url=self.SOURCE_URL,
        )

    @staticmethod
    def _resolve_location(query: str) -> dict[str, float]:
        """Resolve the intentionally small Phase 6 location set."""
        locations = {
            "delhi": {
                "latitude": 28.6139,
                "longitude": 77.2090,
            },
            "mumbai": {
                "latitude": 19.0760,
                "longitude": 72.8777,
            },
            "bangalore": {
                "latitude": 12.9716,
                "longitude": 77.5946,
            },
            "bengaluru": {
                "latitude": 12.9716,
                "longitude": 77.5946,
            },
        }

        try:
            return locations[query.lower()]
        except KeyError as exc:
            raise ValueError(
                f"Unsupported live-data location: {query}"
            ) from exc
