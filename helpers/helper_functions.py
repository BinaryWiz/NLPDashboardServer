from typing import List

def chunk_list(l: List, size: int) -> List[List]:
    new_list = []
    for idx in range(0, len(l), size):
        new_list.append(l[idx: idx + size])
    
    return new_list