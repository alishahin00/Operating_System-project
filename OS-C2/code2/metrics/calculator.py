def calculate_metrics(processes):
    total_waiting = 0
    total_turnaround = 0
    total_response = 0

    for p in processes:
        # Turnaround Time = Completion - Arrival
        p.turnaround_time = p.completion_time - p.arrival_time

        # Waiting Time = Turnaround - Burst
        p.waiting_time = p.turnaround_time - p.burst_time

        # Response Time = First start - Arrival
        if p.start_time != -1:
            p.response_time = p.start_time - p.arrival_time
        else:
            p.response_time = 0

        total_waiting += p.waiting_time
        total_turnaround += p.turnaround_time
        total_response += p.response_time

    n = len(processes)

    avg_waiting = total_waiting / n
    avg_turnaround = total_turnaround / n
    avg_response = total_response / n

    return avg_waiting, avg_turnaround, avg_response