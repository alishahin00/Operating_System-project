from collections import deque


def run_round_robin(processes, quantum=2):

    time = 0

    completed = 0

    n = len(processes)

    gantt = []

    ready_queue = deque()

    processes.sort(key=lambda p: p.arrival_time)

    i = 0

    while completed < n:

        # ================= ADD ARRIVED =================
        while i < n and processes[i].arrival_time <= time:

            ready_queue.append(processes[i])

            i += 1

        # ================= CPU IDLE =================
        if not ready_queue:

            gantt.append(("Idle", time, time + 1))

            time += 1

            continue

        # ================= GET PROCESS =================
        current = ready_queue.popleft()

        # ================= RESPONSE TIME =================
        if current.start_time == -1:

            current.start_time = time

        # ================= EXECUTION =================
        execution_time = min(
            quantum,
            current.remaining_time
        )

        start = time

        time += execution_time

        end = time

        current.remaining_time -= execution_time

        # ================= GANTT =================
        gantt.append(
            (f"P{current.pid}", start, end)
        )

        # ================= ADD NEW ARRIVALS =================
        while i < n and processes[i].arrival_time <= time:

            ready_queue.append(processes[i])

            i += 1

        # ================= RE-QUEUE / COMPLETE =================
        if current.remaining_time > 0:

            ready_queue.append(current)

        else:

            current.completion_time = time

            completed += 1

    return gantt