from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class FamilyMember:
    name: str
    age: int
    allergies: List[str] = field(default_factory=list)
    preferences: List[str] = field(default_factory=list)

@dataclass
class FamilyProfile:
    family_id: str
    members: List[FamilyMember]
    dietary_restrictions: List[str] = field(default_factory=list)
    family_size: int = 0
    
    def __post_init__(self):
        if self.family_size == 0:
            self.family_size = len(self.members)
    
    def to_dict(self) -> Dict:
        return {
            'family_id': self.family_id,
            'members': [
                {
                    'name': m.name,
                    'age': m.age,
                    'allergies': m.allergies,
                    'preferences': m.preferences
                } for m in self.members
            ],
            'dietary_restrictions': self.dietary_restrictions,
            'family_size': self.family_size
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'FamilyProfile':
        members = [
            FamilyMember(
                name=m['name'],
                age=m['age'],
                allergies=m.get('allergies', []),
                preferences=m.get('preferences', [])
            ) for m in data.get('members', [])
        ]
        return FamilyProfile(
            family_id=data['family_id'],
            members=members,
            dietary_restrictions=data.get('dietary_restrictions', []),
            family_size=data.get('family_size', len(members))
        )
