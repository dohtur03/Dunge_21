import json
import pathlib
from typing import List, Tuple, Dict, Any

score_dir = pathlib.Path("../../score")
score_dir.mkdir(exist_ok=True)
score_file = score_dir / "score.json"


def load_score() -> List[Tuple[str, Dict[str, Any]]]:
    if score_file.exists():
        try:
            with open(score_file, 'r') as f:
                score_data = json.load(f)
                processed_data = []
                for item in score_data:
                    player = item[0]
                    data = item[1]
                    # Проверка на старые сейвы (где счет был просто числом секунд)
                    if isinstance(data, int):
                        processed_data.append((player, {"treasures": data}))
                    else:
                        processed_data.append((player, data))
                return processed_data
        except Exception:
            pass
    return []


def save_score(player_name: str, stats: Dict[str, Any]) -> None:
    score_list = load_score()
    score_list.append((player_name, stats))

    with open(score_file, 'w') as f:
        json.dump(score_list, f, indent=2)


def get_top_score(n: int = 10) -> List[Tuple[str, Dict[str, Any]]]:
    scores = load_score()
    # ТЗ: сортировка по количеству сокровищ (treasures), по убыванию
    return sorted(scores, key=lambda x: x[1].get("treasures", 0), reverse=True)[:n]