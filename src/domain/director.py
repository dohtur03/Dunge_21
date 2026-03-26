class GameDirector:
    def __init__(self):
        # Базовый множитель сложности. 1.0 - норма, < 1.0 - легко (игрок страдает), > 1.0 - сложно
        self.difficulty_multiplier = 1.0

        # Метрики текущего этажа для анализа
        self.hp_lost_this_stage = 0
        self.turns_taken_this_stage = 0

    def reset_stage_metrics(self):
        """Сбрасывает счетчики при переходе на новый этаж"""
        self.hp_lost_this_stage = 0
        self.turns_taken_this_stage = 0

    def record_damage_taken(self, amount: int):
        """Фиксирует, что игрок получил урон"""
        self.hp_lost_this_stage += amount

    def record_turn(self):
        """Считает ходы (чем дольше игрок на уровне, тем осторожнее он играет)"""
        self.turns_taken_this_stage += 1

    def evaluate_performance(self, player):
        """Анализирует успехи игрока и меняет сложность ПЕРЕД генерацией следующего уровня"""
        # Если игрок потерял больше 40% от своего макс ХП за уровень — ему тяжело
        if self.hp_lost_this_stage > (player.max_hits * 0.4) or player.hits <= (player.max_hits * 0.3):
            # Снижаем сложность (минимум до 0.5)
            self.difficulty_multiplier = max(0.5, self.difficulty_multiplier - 0.2)

        # Если игрок пролетел уровень, почти не получив урона (меньше 10% макс ХП) — ему слишком легко
        elif self.hp_lost_this_stage <= (player.max_hits * 0.1):
            # Повышаем сложность (максимум до 2.0)
            self.difficulty_multiplier = min(2.0, self.difficulty_multiplier + 0.2)

        # Сбрасываем метрики для следующего этажа
        self.reset_stage_metrics()

    # --- МЕТОДЫ ДЛЯ ГЕНЕРАТОРА УРОВНЕЙ (LEVEL) ---

    def get_enemy_count_modifier(self) -> float:
        """Возвращает множитель количества врагов"""
        return self.difficulty_multiplier

    def get_enemy_stats_buff(self) -> int:
        """Дополнительный бафф к статам врагов (ХП, Сила)"""
        if self.difficulty_multiplier >= 1.5:
            return 2  # Хардкор: враги бьют больнее
        elif self.difficulty_multiplier < 0.8:
            return -1  # Легкотня: враги слабее
        return 0

    def get_item_spawn_chance(self) -> float:
        """Вероятность спавна предметов. Если игроку тяжело — лута больше[cite: 341]."""
        base_chance = 0.4
        if self.difficulty_multiplier < 0.8:
            return base_chance + 0.2  # 60% шанс спавна предметов
        elif self.difficulty_multiplier > 1.2:
            return base_chance - 0.1  # 30% шанс спавна предметов
        return base_chance

    def get_guaranteed_health_drops(self) -> int:
        """Если игрок при смерти, требуем от генератора заспавнить еду (аптечки) [cite: 341]"""
        if self.difficulty_multiplier <= 0.6:
            return 2  # Гарантируем 2 куска еды на уровень
        return 0