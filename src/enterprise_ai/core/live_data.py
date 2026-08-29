"""Provider-neutral live data representation."""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class LiveData(BaseModel):
    """Normalized live data returned by an external provider."""

    model_config = ConfigDict(frozen=True)

    query: str = Field(min_length=1)
    value: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    source_url: HttpUrl
    retrieved_at: datetime

    @property
    def source_type(self) -> str:
        """Return the canonical evidence source classification."""
        return "live_external"

    @property
    def is_fresh(self) -> bool:
        """Return whether the timestamp is timezone-aware."""
        return self.retrieved_at.tzinfo is not None

    @classmethod
    def create(
        cls,
        *,
        query: str,
        value: str,
        source_name: str,
        source_url: str,
    ) -> "LiveData":
        """Create live data with the current UTC retrieval time."""
        return cls(
            query=query,
            value=value,
            source_name=source_name,
            source_url=source_url,
            retrieved_at=datetime.now(UTC),
        )

