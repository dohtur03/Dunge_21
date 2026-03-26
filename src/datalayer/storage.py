import os
import json
import datetime

class Storage:
    SLOTS_DIR = "../saves/"

    def __init__(self):
        os.makedirs(self.SLOTS_DIR, exist_ok=True)
        self.slots = self._scan_slots()

    def _scan_slots(self) -> list[str]:
        slots = ["<empty>"] * 10
        for filename in os.listdir(self.SLOTS_DIR):
            if filename.endswith(".json"):
                try:
                    path = os.path.join(self.SLOTS_DIR, filename)
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    slot_idx = data.get("__slot_index__")
                    if isinstance(slot_idx, int) and 0 <= slot_idx <= 9:
                        slots[slot_idx] = f"<{filename[:-5]}>"
                except Exception:
                    continue
        return slots

    def save_slot(self, slot_index: int, game_data: dict) -> bool:
        if not (0 <= slot_index <= 9):
            return False

        try:
            player_name = game_data.get("player_name", "player")
            safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in player_name)
            
            now = datetime.datetime.now().strftime("%H-%M-%S")
            filename = f"{safe_name}_{now}.json"
            filepath = os.path.join(self.SLOTS_DIR, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(game_data, f, ensure_ascii=False, indent=2)

            self.slots[slot_index] = f"<{filename[:-5]}>"
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False

    def load_slot(self, slot_index: int) -> dict | None:
        if not (0 <= slot_index <= 9):
            return None
        for filename in os.listdir(self.SLOTS_DIR):
            if filename.endswith(".json"):
                try:
                    path = os.path.join(self.SLOTS_DIR, filename)
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if data.get("__slot_index__") == slot_index:
                        return data
                except Exception:
                    continue
        return None