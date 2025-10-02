"""
Unified internship data model and schema definitions.
"""
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd


@dataclass
class Internship:
    """
    Unified schema for internship data across all sources.
    """
    title: str
    organization: str
    country: str
    location: str
    type: str = "Internship"
    eligibility_criteria: str = ""
    target_audience: str = ""  # UG/PG/PhD
    start_date: str = ""
    duration: str = ""
    application_deadline: str = ""
    application_link: str = ""
    mode: str = ""  # Onsite/Remote/Hybrid
    stipend: str = ""
    salary: str = ""
    visa_support: str = ""
    tags: List[str] = None
    source: str = ""
    scraped_timestamp: str = ""
    description: str = ""
    skills_required: List[str] = None
    perks: List[str] = None
    company_size: str = ""
    industry: str = ""

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.skills_required is None:
            self.skills_required = []
        if self.perks is None:
            self.perks = []
        if not self.scraped_timestamp:
            self.scraped_timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV export."""
        data = asdict(self)
        # Convert lists to comma-separated strings for CSV
        data['tags'] = ', '.join(self.tags) if self.tags else ''
        data['skills_required'] = ', '.join(self.skills_required) if self.skills_required else ''
        data['perks'] = ', '.join(self.perks) if self.perks else ''
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Internship':
        """Create Internship from dictionary."""
        # Convert comma-separated strings back to lists
        if 'tags' in data and isinstance(data['tags'], str):
            data['tags'] = [tag.strip() for tag in data['tags'].split(',') if tag.strip()]
        if 'skills_required' in data and isinstance(data['skills_required'], str):
            data['skills_required'] = [skill.strip() for skill in data['skills_required'].split(',') if skill.strip()]
        if 'perks' in data and isinstance(data['perks'], str):
            data['perks'] = [perk.strip() for perk in data['perks'].split(',') if perk.strip()]
        return cls(**data)


class InternshipSchema:
    """Schema definition for CSV columns."""

    COLUMNS = [
        'title', 'organization', 'country', 'location', 'type',
        'eligibility_criteria', 'target_audience', 'start_date', 'duration',
        'application_deadline', 'application_link', 'mode', 'stipend', 'salary',
        'visa_support', 'tags', 'source', 'scraped_timestamp', 'description',
        'skills_required', 'perks', 'company_size', 'industry'
    ]

    @classmethod
    def get_empty_dataframe(cls) -> pd.DataFrame:
        """Get empty DataFrame with correct schema."""
        return pd.DataFrame(columns=cls.COLUMNS)

    @classmethod
    def validate_dataframe(cls, df: pd.DataFrame) -> bool:
        """Validate DataFrame has correct schema."""
        return all(col in df.columns for col in cls.COLUMNS)


def deduplicate_internships(internships: List[Internship]) -> List[Internship]:
    """
    Remove duplicate internships based on title, organization, and location.
    """
    seen = set()
    unique_internships = []

    for internship in internships:
        # Create a key for deduplication
        key = (
            internship.title.lower().strip(),
            internship.organization.lower().strip(),
            internship.location.lower().strip()
        )

        if key not in seen:
            seen.add(key)
            unique_internships.append(internship)

    return unique_internships
