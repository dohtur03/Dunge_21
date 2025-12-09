from domain.map.room import Room


class Corridor:
    def __init__(self, points: list[tuple[int, int]]):
        """
        points — список клеток (x, y), по которым проходит коридор.
        """
        self.points = points

    @classmethod
    def between(cls, first_room: Room, second_room: Room) -> "Corridor":
        points: list[tuple[int, int]] = []

        fr_left, fr_right, fr_top, fr_bottom = first_room.left, first_room.right - 1, first_room.top, first_room.bottom - 1
        sr_left, sr_right, sr_top, sr_bottom = second_room.left, second_room.right - 1, second_room.top, second_room.bottom - 1


        overlap_left = max(fr_left, sr_left)
        overlap_right = min(fr_right, sr_right)

        if overlap_left <= overlap_right:
            x = (overlap_left + overlap_right) // 2

            if fr_top < sr_top:
                start_y = fr_bottom + 1      # сразу под нижней стеной A
                end_y = sr_top - 1        # сразу над верхней стеной B
            else:
                start_y = sr_bottom + 1
                end_y = fr_top - 1

            for y in range(start_y, end_y + 1):
                points.append((x, y))

            return cls(points)

        overlap_top = max(fr_top, sr_top)
        overlap_bottom = min(fr_bottom, sr_bottom)

        if overlap_top <= overlap_bottom:
            y = (overlap_top + overlap_bottom) // 2

            if fr_left < sr_left:
                start_x = fr_right + 1      # сразу справа от стены A
                end_x = sr_left - 1        # сразу слева от стены B
            else:
                start_x = sr_right + 1
                end_x = fr_left - 1

            for x in range(start_x, end_x + 1):
                points.append((x, y))

            return cls(points)

        return cls(points)