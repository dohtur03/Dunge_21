- main.py забирает параметры из json файла в папке data файлом loader.py 
и обрабатывает поведение врагов файлом /objects/enemies.<br>
- Показывает статы монстров и обрабатывает один цикл атаки зомби на 10 hp и ответной атаки зомби на random 5 +- 2.<br><br>
### Параметры игрока и монстров, минимальные и максимальные параметры от 1 до 21 уровня.<br>
<img width="828" height="411" alt="image" src="https://github.com/user-attachments/assets/a38f6bcc-8e16-4c01-8701-21f86b9a391b" /><br>

Для каждого уровня N:<br>
    • hp = начальное + (N - 1) * рост_здоровья<br>
    • dxt = начальное + (N - 1) * рост_ловкости<br>
    • str = начальное + (N - 1) * рост_силы<br>
    • agr = растет от минимального к максимальному постепенно<br>

def stat_increase(start, end, level, max_level=21):<br>
    return start + (end - start) * (level - 1) / (max_level - 1)<br>

zombie_hp = stat_increase(15, 45, level)<br>
zombie_dxt = stat_increase(5, 10, level)<br>
zombie_str = stat_increase(7, 12, level)<br>
zombie_agr = stat_increase(0.6, 0.8, level)<br>
