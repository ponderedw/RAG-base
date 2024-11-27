from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DocumentMetadata:
    """Represents additional information about the document that should be stored in the vector database."""

    source_id: str
    source_name: str
    modified_at: datetime
    payload: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Converts the metadata to a vector-database compatible dictionary."""
        return {
            'source_id': self.source_id,
            'source_name': self.source_name,
            'modified_at': self.modified_at.isoformat(),
            'payload': self.payload,
        }
