from presentation.log import *
from domain.inventory import *
from domain.item import *
import random

class Game:
    def __init__(self, stdscr, player_name: str):
        self.stdscr = stdscr
        self.stdscr.keypad(True)
        self.player_name = player_name
        self.player_y = 0
        self.player_x = 0
        self.player_char = "☺"
        self.player_score = 0
        self.player_stage = 1
        self.player_hits = 10
        self.player_max_hits = 20
        self.player_str = 10
        self.player_agility = 10
        self.player_gold = 0
        self.player_exp = 0
        self.player_exp_to_level_up = "?"
        self.player_level = 1

        height, width = stdscr.getmaxyx()
        self.player_pos_init(height, width)

        self.PANEL_HEIGHT = 3
        self.BORDER_TOP = 3

        self.logger = GameLog()

        self.inventory = Inventory(stdscr, player_name, self)

        self.start_time = time.time()
        
        self.current_weapon = None
        self.player_total_str = self.player_str
        self.potion_effects = []

        for category_name in Item.items:
            for i in range(5):
                self.inventory.category_items[category_name][i] = Item(**random.choice(Item.items[category_name]))

    def get_score(self):
        return self.player_score

    def exit_game(self) -> int:
        height, width = self.stdscr.getmaxyx()
        selected = 1
        blink = False

        while True:
            self.stdscr.clear()

            question = "Are you sure you want to leave the game?"
            q_y = height // 2
            q_x = (width - len(question)) // 2
            self.stdscr.addstr(q_y, q_x, question, curses.color_pair(3) | curses.A_BOLD)

            options_local = ["Yes", "No", "Back to menu"]
            pointer = "▶"

            for i, text in enumerate(options_local):
                y = q_y + 2 + i
                line = f"{pointer} {text}" if i == selected else f"  {text}"

                if i == selected:
                    color = curses.color_pair(2 if blink else 3)
                    attr = color | curses.A_BOLD
                else:
                    attr = curses.color_pair(3)

                x = (width - len(line)) // 2
                self.stdscr.addstr(y, x, line, attr)

            self.stdscr.refresh()

            blink = not blink
            self.stdscr.timeout(300)
            key = self.stdscr.getch()

            if key == -1:
                continue
            if key == curses.KEY_UP:
                selected = (selected - 1) % len(options_local)
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % len(options_local)
            elif key in (curses.KEY_ENTER, 10, 13):
                return selected

    def run(self) -> str:
        while True:
            self.update_effects()
            current_time = time.time()
            total_run = int(current_time - self.start_time)
            self.player_score = total_run
            
            if self.player_hits <= 0:
                msg = death_message
                self.logger.show_popup(self.stdscr, msg)
                return "quit_game"
            elif self.player_hits >= self.player_max_hits:
                self.player_hits = self.player_max_hits
            
            if self.logger.needs_popup(current_time):
                msg = get_random_message()
                self.logger.show_popup(self.stdscr, msg)
                self.logger.last_popup = current_time
            
            self.stdscr.timeout(100)
            key = self.stdscr.getch()
            
            if key == ord('q'):
                option = self.exit_game()
                if option == 0:
                    self.stdscr.clear()
                    msg = "Good luck! See you next time!"
                    h, w = self.stdscr.getmaxyx()
                    y = h // 2
                    x = (w - len(msg)) // 2
                    self.stdscr.addstr(y, x, msg, curses.color_pair(3) | curses.A_BOLD)
                    self.stdscr.refresh()
                    self.stdscr.timeout(-1)
                    self.stdscr.getch()
                    return "quit_game"
                if option == 1:
                    continue
                if option == 2:
                    return "back_to_menu"
            elif key == ord('i'):
                selected_category = self.inventory.show()
                if selected_category == None:
                    continue  
                if selected_category != "Back":
                    self.open_category(selected_category)
            elif key == ord('w') or key == curses.KEY_UP:
                self.player_y -= 1
            elif key == ord('s') or key == curses.KEY_DOWN:
                self.player_y += 1
            elif key == ord('a') or key == curses.KEY_LEFT:
                self.player_x -= 1
            elif key == ord('d') or key == curses.KEY_RIGHT:
                self.player_x += 1
            
            self.draw_game()

    def player_pos_init(self, height, width):
        self.player_y = height // 2
        self.player_x = width // 2

    def draw_player(self) -> None:
        self.stdscr.addch(self.player_y, self.player_x, self.player_char, curses.color_pair(7) | curses.A_BOLD)

    def draw_panel(self, height, width) -> None:
        active_buffs = []
        current_time = time.time()
        for effect in self.potion_effects:
            if current_time < effect["end_time"]:
                active_buffs.append(f"{effect['type'].upper()}+{effect['value']}")
        
        if len(list(active_buffs)) != 0:
            buffs_text = " | ".join(active_buffs[:3])
            if len(active_buffs) > 3:
                buffs_text += " + ..."
            status = f"Game started for {self.player_name}! Score: {self.player_score} Active buffs: {buffs_text}"
        else:
            status = f"Game started for {self.player_name}! Score: {self.player_score} No active buffs"

        y_status = 0
        x_status = (width - len(status)) // 2
        self.stdscr.addstr(y_status, x_status, status, curses.color_pair(4) | curses.A_BOLD)

        hint_controls = "<Press 'W', 'A', 'S', 'D' or arrows to move! ('q' to quit, 'i' to open inventory)>"
        y_hint_controls = y_status + 2
        x_hint_controls = (width - len(hint_controls)) // 2
        self.stdscr.addstr(y_hint_controls, x_hint_controls, hint_controls, curses.color_pair(3))

    def draw_field(self, height, width) -> None:
        top_line = "┌" + "─" * (width - 2) + "┐"
        self.stdscr.addstr(self.BORDER_TOP, 0, top_line[:width], curses.color_pair(2) | curses.A_BOLD)

        bot_line = "└" + "─" * (width - 2) + "┘"
        self.stdscr.addstr(height - 2, 0, bot_line[:width], curses.color_pair(2) | curses.A_BOLD)

        for y in range(self.BORDER_TOP + 1, height - 2):
            if 0 < width:
                self.stdscr.addch(y, 0, "│", curses.color_pair(2) | curses.A_BOLD)
            if width > 1:
                self.stdscr.addch(y, width - 1, "│", curses.color_pair(2) | curses.A_BOLD)

    def draw_bottom_panel(self, height, width) -> None:
        if self.current_weapon == None:
                weapon_str_hint = ""
        else:
            weapon_str = self.current_weapon.value
            weapon_str_hint = f"(+{weapon_str})"
        stats = f"Stage: {self.player_stage} Hits: {self.player_hits}/{self.player_max_hits} Str: {self.player_str}{weapon_str_hint} Agi: {self.player_agility} Gold: {self.player_gold} Exp: {self.player_exp}/{self.player_exp_to_level_up} Level: {self.player_level}"
        y_stats = height - 1
        x_stats = max(1, (width - len(stats)) // 2)
        self.stdscr.addstr(y_stats, x_stats, stats[:width], curses.color_pair(3) | curses.A_BOLD)
        
    def draw_game(self) -> None:
        self.stdscr.clear()
            
        height, width = self.stdscr.getmaxyx()
        
        self.player_y = max(self.BORDER_TOP + 1, min(height - 3, self.player_y))
        self.player_x = max(1, min(width - 2, self.player_x))
        
        self.draw_panel(height, width)
        self.draw_field(height, width)
        self.draw_bottom_panel(height, width)
        self.draw_player()

        self.stdscr.refresh()
    
    def open_category(self, category: str) -> None:
        chosen_item = self.inventory.show_category_items(category)
        
        if chosen_item == "Back":
            return
        
        if chosen_item is not None:
            category_name, slot_idx, item = chosen_item
            self.inventory.category_items[category_name][slot_idx] = None
    
    def update_stats(self):
        self.player_total_str = self.player_str + (self.current_weapon.value if self.current_weapon is not None else 0)
    
    def add_potion_effect(self, effect_type, value, duration):
        self.potion_effects.append({
            "type": effect_type,
            "value": value,
            "end_time": time.time() + duration
        })

        if effect_type == "max_hits":
            self.player_max_hits += value
            self.player_hits += value
        elif effect_type == "strength":
            self.player_str += value
        elif effect_type == "agility":
            self.player_agility += value

    def update_effects(self):
        current_time = time.time()
          
        all_effects = self.potion_effects.copy()
        self.potion_effects = []
        
        active_effects = []
        
        for effect in all_effects:
            if current_time < effect["end_time"]:
                self.potion_effects.append(effect)
                active_effects.append(f"{effect['type'].upper()}+{effect['value']}")
        
        max_hp_bonus = 0
        str_bonus = 0
        agi_bonus = 0

        for effect in all_effects:
            if current_time >= effect["end_time"]:
                if effect["type"] == "max_hits":
                    max_hp_bonus += effect["value"]
                    self.logger.show_popup(self.stdscr, f"Effect of MAX HP +{effect['value']} has expired!")
                elif effect["type"] == "strength":
                    str_bonus += effect["value"]
                    self.logger.show_popup(self.stdscr, f"Effect of STR +{effect['value']} has expired!")
                elif effect["type"] == "agility":
                    agi_bonus += effect["value"]
                    self.logger.show_popup(self.stdscr, f"Effect of AGI +{effect['value']} has expired!")

        self.player_max_hits -= max_hp_bonus
        self.player_hits -= max_hp_bonus
        self.player_str -= str_bonus
        self.player_agility -= agi_bonus
    
    def save_game_data_to_dict(self) -> dict:
        return {
            "position": [self.player_y, self.player_x],
            "player_name": self.player_name,
            "inventory": self.inventory.to_dict(),
            "score": self.player_score,
            "stage": self.player_stage,
            "player_hits": self.player_hits,
            "player_max_hits": self.player_max_hits, 
            "player_str": self.player_str, 
            "player_agility": self.player_agility, 
            "player_gold": self.player_gold,
            "player_exp": self.player_exp,
            "player_exp_to_level_up": self.player_exp_to_level_up, 
            "player_level": self.player_level,
            "start_time": self.start_time,
            "current_weapon": self.current_weapon.to_dict() if self.current_weapon else None,
            "player_total_str": self.player_total_str,
            "potion_effects": self.potion_effects
        }
    
    @classmethod
    def from_dict(cls, stdscr, data: dict):
        game = cls.__new__(cls)
        game.stdscr = stdscr
        game.stdscr.keypad(True)

        game.player_char = "☺"
        game.player_hits = data["player_hits"]
        game.player_max_hits = data["player_max_hits"]

        game.player_name = data["player_name"]
        game.player_y, game.player_x = data["position"]
        game.player_score = data["score"]
        game.player_stage = data["stage"]
        game.player_hits = data["player_hits"]
        game.player_max_hits = data["player_max_hits"]
        game.player_str = data["player_str"]
        game.player_agility = data["player_agility"]
        game.player_gold = data["player_gold"]
        game.player_exp = data["player_exp"]
        game.player_exp_to_level_up = data["player_exp_to_level_up"]
        game.player_level = data["player_level"]
        game.start_time = data["start_time"]
        game.player_total_str = data.get("player_total_str", game.player_str)
        game.potion_effects = data.get("potion_effects", [])
    
        game.logger = GameLog()
        game.PANEL_HEIGHT = 3
        game.BORDER_TOP = 3

        inv_data = data.get("inventory", {})
        game.inventory = Inventory.from_dict(stdscr, game.player_name, game, inv_data)
        
        weapon_data = data.get("current_weapon")
        game.current_weapon = None
        
        if weapon_data is not None:
            game.current_weapon = Item.from_dict(weapon_data)
            for i in range(len(game.inventory.category_items["Weapon"])):
                item = game.inventory.category_items["Weapon"][i]
                if item is not None:
                    if (item.name == game.current_weapon.name and
                        item.value == game.current_weapon.value and
                        item.effect_type == game.current_weapon.effect_type):
                        game.inventory.category_items["Weapon"][i] = game.current_weapon
                        break
                        
        game.update_stats()
        return game