from pydantic import BaseModel
from typing import List

class post_data(BaseModel):
    prompt: str = "Hello world"
    temperature: float = 0.7
    top_k: float = 50
    top_p: float = 0.95
    min_length:int = 10
    max_length:int = 50
    do_sample:bool = False