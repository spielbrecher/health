from pydantic import BaseModel  #, validator, root_validator
from typing import Optional

class DataRequest(BaseModel):
    input_city: str