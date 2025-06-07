from pydantic import BaseModel
from typing import Optional, List


class BaseAPIModel(BaseModel):
    """
    Base model with a common configuration for API models.
    All API models that need to be serialized between frontend and backend should inherit from this.
    """
    class Config:
        # Allow conversion between camelCase (JavaScript) and snake_case (Python)
        alias_generator = lambda string: ''.join(
            word if i == 0 else word.capitalize() 
            for i, word in enumerate(string.split('_'))
        )
        populate_by_name = True  # Note: validate_by_name is deprecated in newer Pydantic versions
        json_encoders = {
            # Add any custom encoders here if needed
        }

