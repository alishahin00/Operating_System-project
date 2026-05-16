def run_srtf(processes):

    time = 0
    completed = 0

    n = len(processes)

    gantt = []

    while completed < n:


        available = [
            p for p in processes
            if p.arrival_time <= time
            and p.remaining_time > 0
        ]


        if not available:

            if gantt and gantt[-1][0] == "Idle":
                gantt[-1] = ("Idle", gantt[-1][1], time + 1)
            else:
                gantt.append(("Idle", time, time + 1))

            time += 1

            continue


        current = min(
            available,
            key=lambda x: (x.remaining_time, x.arrival_time)
        )


        if current.start_time == -1:
            current.start_time = time

        start = time

        # execute for 1 unit
        current.remaining_time -= 1

        time += 1

        end = time


        pid_str = f"P{current.pid}"
        
        if gantt and gantt[-1][0] == pid_str:
            gantt[-1] = (pid_str, gantt[-1][1], end)
        else:
            gantt.append((pid_str, start, end))


        if current.remaining_time == 0:

            current.completion_time = time

            completed += 1

    return gantt