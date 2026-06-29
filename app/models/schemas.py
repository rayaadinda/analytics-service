from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class RunClusteringRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    n_clusters: Optional[int] = 3
