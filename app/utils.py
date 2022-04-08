def generate_details_log(task, pids, cpu, memory, start=None):
    task_start_or_end = "start" if start != None else "end"

    return f"Task: {task} ({task_start_or_end}) - PID: {len(pids)} CPU: {cpu}%, RAM (GB): avl: {round(memory.available/1073741824, 2)}, used: {round(memory.used/1073741824, 2)}, {memory.percent}%)"
