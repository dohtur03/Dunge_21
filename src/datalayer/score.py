import json
import pathlib
from typing import List, Tuple


score_dir = pathlib.Path("../../score")
score_dir.mkdir(exist_ok=True)
score_file = score_dir / "score.json"
 
def load_score() -> List[Tuple[str, int]]:
    if score_file.exists() == True:
        try:
            with open(score_file, 'r') as f:
                score_data = json.load(f)
                return [(player, int(score)) for player, score in score_data]
        except:
            pass
    return []

def save_score(player_name: str, score: int) -> None:
    score_list = load_score()
    score_list.append((player_name, score))

    with open(score_file, 'w') as f:
        json.dump(score_list, f, indent=2)

def get_top_score(n: int = 10) -> List[Tuple[str, int]]:
    score = load_score()
    return sorted(score, key=lambda x: x[1], reverse=True)[:n]