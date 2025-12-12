import curses

logo = [
    r"██████╗  ██████╗  ██████╗  ██╗   ██╗ ███████╗",
    r"██╔══██╗██╔═══██╗██╔════╝  ██║   ██║ ██╔════╝",
    r"██████╔╝██║   ██║██║ ████║║██║   ██║ █████╗  ",
    r"██╔══██╗██║   ██║██║   ██║╚██╗   ██╔╝██╔══╝  ",
    r"██║  ██║╚██████╔╝╚██████╔╝ ╚██████╔╝ ███████╗",
    r"╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═══╝   ╚══════╝",
]

big_start = [
    r" ____  _             _     _   _                  ____                       ",
    r"/ ___|| |_ __ _ _ __| |_  | \ | | _____      __  / ___| __ _ _ __ ___   ___  ",
    r"\___ \| __/ _` | '__| __| |  \| |/ _ \ \ /\ / / | |  _ / _` | '_ ` _ \ / _ \ ",
    r" ___) | || (_| | |  | |_  | |\  |  __/\ V  V /  | |_| | (_| | | | | | |  __/ ",
    r"|____/ \__\__,_|_|   \__| |_| \_|\___| \_/\_/    \____|\__,_|_| |_| |_|\___| ",
]

big_load_game = [
    r" _                    _    ____                       ",
    r"| |    ___   __ _  __| |  / ___| __ _ _ __ ___   ___  ",
    r"| |   / _ \ / _` |/ _` | | |  _ / _` | '_ ` _ \ / _ \ ",
    r"| |__| (_) | (_| | (_| | | |_| | (_| | | | | | |  __/ ",
    r"|_____\___/ \__,_|\__,_|  \____|\__,_|_| |_| |_|\___| ",
]

big_settings = [
    r" ____       _   _   _                  ",
    r"/ ___|  ___| |_| |_(_)_ __   __ _ ___  ",
    r"\___ \ / _ \ __| __| | '_ \ / _` / __| ",
    r" ___) |  __/ |_| |_| | | | | (_| \__ \ ",
    r"|____/ \___|\__|\__|_|_| |_|\__, |___/ ",
    r"                            |___/      ",          
]

big_exit = [
    r" _____      _ _   ", 
    r"| ____|_  _(_) |_ ",
    r"|  _| \ \/ / | __|",
    r"| |___ >  <| | |_ ",
    r"|_____/_/\_\_|\__|",
]

big_yes = [
    r"__   __         ",
    r"\ \ / /__  ___  ",
    r" \ V / _ \/ __| ",
    r"  | |  __/\__ \ ",
    r"  |_|\___||___/ ",
]

big_no = [
    r" _   _        ",
    r"| \ | | ___   ",
    r"|  \| |/ _ \  ",
    r"| |\  | (_) | ",
    r"|_| \_|\___/  ",   
]

big_score = [
    r" ____                      ",
    r"/ ___|  ___ ___  _ __ ___  ",
    r"\___ \ / __/ _ \| '__/ _ \ ",
    r" ___) | (_| (_) | | |  __/ ",
    r"|____/ \___\___/|_|  \___| ",
]

big_back_to_game = [
    r" ____             _      _                                      ",
    r"| __ )  __ _  ___| | __ | |_ ___     __ _  __ _ _ __ ___   ___  ",
    r"|  _ \ / _` |/ __| |/ / | __/ _ \   / _` |/ _` | '_ ` _ \ / _ \ ",
    r"| |_) | (_| | (__|   <  | || (_) | | (_| | (_| | | | | | |  __/ ",
    r"|____/ \__,_|\___|_|\_\  \__\___/   \__, |\__,_|_| |_| |_|\___| ",
    r"                                    |___/                       ",
]

options = ["Start new game", "Load game", "Score", "Settings", "Exit"]
how_many_options = len(options)

def draw_logo(stdscr, y_offset: int = 0) -> None:
    height, width = stdscr.getmaxyx()
    logo_width = max(len(line) for line in logo)

    start_y = y_offset
    start_x = (width - logo_width) // 2

    for i, line in enumerate(logo):
        if start_y + i < height:
            stdscr.addstr(start_y + i, start_x, line, curses.color_pair(1))

def get_big_block(menu_index: int, has_active_game: bool, selected: int):
    """Возвращает большой блок по индексу меню"""
    if has_active_game and selected == 0:
        return big_back_to_game
    
    if menu_index == 0: return big_start
    elif menu_index == 1: return big_load_game
    elif menu_index == 2: return big_score
    elif menu_index == 3: return big_settings
    elif menu_index == 4: return big_exit
    return None

def draw_menu_items(stdscr, menu_top: int, total_items: int, selected: int, blink: bool, has_active_game: bool, base_index_offset: int, width: int):
    pointer = "▶"
    for i in range(total_items):
        y = menu_top + i
        text = "Back to game" if has_active_game and i == 0 else options[i - base_index_offset]
        
        if i == selected:
            line_text = f"{pointer} {text}"
            color = curses.color_pair(2 if blink else 3)
            attr = color | curses.A_BOLD
            x = (width - len(line_text)) // 2
            stdscr.addstr(y, x, line_text, attr)
        else:
            line_text = f"  {text}"
            attr = curses.color_pair(3)
            x = (width - len(line_text)) // 2
            stdscr.addstr(y, x, line_text, attr)

def draw_big_block(stdscr, big_block, width: int, height: int):
    if big_block is None: return
    
    logo_height = len(logo)
    big_start_y = 1 + logo_height + 1
    
    for j, line in enumerate(big_block):
        y = big_start_y + j
        if y >= height: break
        x = (width - len(line)) // 2
        stdscr.addstr(y, x, line, curses.color_pair(2) | curses.A_BOLD)

def draw_bottom_panel(stdscr, height: int, width: int):
    version = "ROGUE 1980 (REMAKE) v.1.0"
    made_by = "made by:"
    students = ["flameppe", "sherrelm", "gnarchis", "lorenaji"]
    
    y_students_last = height - 1
    y_made_by = y_students_last - len(students) - 1
    y_version = y_made_by - 1
    
    x_version = (width - len(version)) // 2
    stdscr.addstr(y_version, x_version, version, curses.color_pair(3))
    
    x_made_by = (width - len(made_by)) // 2
    stdscr.addstr(y_made_by, x_made_by, made_by, curses.color_pair(3))
    
    student_pairs = [4, 5, 6, 7]
    for i, name in enumerate(students):
        y = y_made_by + 1 + i
        x = (width - len(name)) // 2
        pair = student_pairs[i % len(student_pairs)]
        attr = curses.color_pair(pair) | curses.A_BOLD
        stdscr.addstr(y, x, name, attr)