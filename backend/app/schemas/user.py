from pydantic import BaseModel
from typing import Optional


class UpdateCostBasisMethod(BaseModel):
    method: str  # "fifo", "lifo", "hifo", "avg_cost"
