from collections import deque
from typing import Set, Tuple, Dict, Any


def check_level_passability(
        start_pos: Tuple[int, int],
        exit_pos: Tuple[int, int],
        walkable_cells: Set[Tuple[int, int]],
        keys: Dict[Tuple[int, int], str],
        doors: Dict[Tuple[int, int], str]
) -> bool:
    """
    Модифицированный BFS для проверки валидности генерации уровня.
    walkable_cells - сетка пола комнат и коридоров.
    keys - словарь {координаты: цвет_ключа}.
    doors - словарь {координаты: цвет_двери}.
    """
    collected_keys: Set[str] = set()

    while True:
        queue = deque([start_pos])
        visited = set([start_pos])
        new_key_found = False
        exit_reachable = False

        while queue:
            cy, cx = queue.popleft()

            # Если достигли выхода, уровень 100% проходим!
            if (cy, cx) == exit_pos:
                exit_reachable = True

            # Если наступили на ключ, которого у нас еще нет
            if (cy, cx) in keys and keys[(cy, cx)] not in collected_keys:
                collected_keys.add(keys[(cy, cx)])
                new_key_found = True
                # Прерываем текущий обход, чтобы начать заново с новым ключом
                break

                # Проверяем 4 соседние клетки (Вверх, Вниз, Влево, Вправо)
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ny, nx = cy + dy, cx + dx

                # Если это не пол/коридор или мы тут уже были - пропускаем
                if (ny, nx) not in walkable_cells: continue
                if (ny, nx) in visited: continue

                # Если наткнулись на дверь, проверяем связку ключей
                if (ny, nx) in doors:
                    req_color = doors[(ny, nx)]
                    if req_color not in collected_keys:
                        continue  # Ключа нет, воспринимаем дверь как стену

                visited.add((ny, nx))
                queue.append((ny, nx))

        if exit_reachable:
            return True

        # Если обошли всё, что могли, но новых ключей не нашли - это СОФТЛОК
        if not new_key_found:
            return False