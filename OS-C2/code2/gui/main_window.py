import tkinter as tk
from tkinter import ttk, messagebox
import copy

from models.process import Process
from schedulers.srtf_scheduler import run_srtf
from schedulers.round_robin_scheduler import run_round_robin
from metrics.calculator import calculate_metrics
from gui.gantt_frame import GanttFrame


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Round Robin vs SRTF Scheduler Simulator")
        self.root.geometry("1200x750")

        self.processes = []

        # ================= SCROLL =================
        canvas = tk.Canvas(root)
        scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)

        self.main = tk.Frame(canvas)

        self.main.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.main, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        canvas.bind_all(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        )

        # ================= LAYOUT =================
        left = tk.Frame(self.main)
        left.grid(row=0, column=0, sticky="n")

        right = tk.Frame(self.main)
        right.grid(row=0, column=1, padx=20)

        # ================= INPUT =================
        input_frame = tk.LabelFrame(
            left,
            text="Input Panel",
            padx=10,
            pady=10
        )

        input_frame.pack(pady=10)

        labels = ["Process ID", "Arrival Time", "Burst Time"]

        self.entries = []

        for i, text in enumerate(labels):
            tk.Label(input_frame, text=text).grid(row=i, column=0, pady=5)

            entry = tk.Entry(input_frame)
            entry.grid(row=i, column=1, pady=5)

            self.entries.append(entry)

        # ================= QUANTUM =================
        tk.Label(input_frame, text="Quantum Time").grid(row=3, column=0, pady=5)

        self.quantum_entry = tk.Entry(input_frame)
        self.quantum_entry.grid(row=3, column=1, pady=5)

        # ================= BUTTONS =================
        button_frame = tk.Frame(left)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Add Process",
            width=20,
            command=self.add
        ).pack(pady=5)

        tk.Button(
            button_frame,
            text="Run Simulation",
            width=20,
            command=self.run
        ).pack(pady=5)

        tk.Button(
            button_frame,
            text="Reset",
            width=20,
            command=self.reset
        ).pack(pady=5)

        # ================= RULES =================
        rules = tk.LabelFrame(
            left,
            text="Scheduling Rules",
            padx=10,
            pady=10
        )

        rules.pack(pady=10)

        tk.Label(
            rules,
            justify="left",
            text=
            "Round Robin: Time slicing using quantum\n"
            "Tie-breaking: Earlier arrival time\n"
            "SRTF: Preemptive shortest remaining time"
        ).pack()

        # ================= PROCESS TABLE =================
        table_frame = tk.LabelFrame(right, text="Process Table")
        table_frame.pack(fill="x", pady=10)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("PID", "Arrival", "Burst"),
            show="headings"
        )

        for col in ("PID", "Arrival", "Burst"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.pack(fill="x")

        # ================= RESULTS =================
        result_frame = tk.Frame(right)
        result_frame.pack(fill="both", expand=True)

        # ---------- SRTF ----------
        srtf_container = tk.LabelFrame(
            result_frame,
            text="SRTF Results"
        )

        srtf_container.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        self.srtf_table = ttk.Treeview(
            srtf_container,
            columns=("PID", "WT", "TAT", "RT"),
            show="headings"
        )

        # ---------- RR ----------
        rr_container = tk.LabelFrame(
            result_frame,
            text="Round Robin Results"
        )

        rr_container.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        self.rr_table = ttk.Treeview(
            rr_container,
            columns=("PID", "WT", "TAT", "RT"),
            show="headings"
        )

        for table in [self.srtf_table, self.rr_table]:

            for col in ("PID", "WT", "TAT", "RT"):
                table.heading(col, text=col)
                table.column(col, width=80)

            table.pack(fill="both", expand=True)

        # ================= COMPARISON =================
        comparison_frame = tk.LabelFrame(
            right,
            text="Comparison Summary"
        )

        comparison_frame.pack(fill="x", pady=10)

        self.comp_text = tk.Label(
            comparison_frame,
            text="",
            justify="left"
        )

        self.comp_text.pack()

        # ================= CONCLUSION =================
        conclusion_frame = tk.LabelFrame(
            right,
            text="Final Conclusion"
        )

        conclusion_frame.pack(fill="x", pady=10)

        self.conclusion_text = tk.Label(
            conclusion_frame,
            text="",
            justify="left"
        )

        self.conclusion_text.pack()

        # ================= GANTT =================
        gantt_frame = tk.LabelFrame(
            right,
            text="Gantt Charts"
        )

        gantt_frame.pack(fill="both", expand=True)

        self.gantt_srtf = GanttFrame(gantt_frame, "SRTF")
        self.gantt_rr = GanttFrame(gantt_frame, "Round Robin")

    # =========================================================
    # VALIDATION
    # =========================================================
    def validate(self):

        pid = self.entries[0].get().strip()
        arrival = self.entries[1].get().strip()
        burst = self.entries[2].get().strip()

        if not pid or not arrival or not burst:

            messagebox.showerror(
                "Error",
                "All process fields are required"
            )

            return None

        try:
            pid = int(pid)
            arrival = int(arrival)
            burst = int(burst)
        except ValueError:
            messagebox.showerror(
                "Error",
                "All values must be integers"
            )
            return None

        if pid <= 0:

            messagebox.showerror(
                "Error",
                "Process ID must be > 0"
            )

            return None

        if arrival < 0:

            messagebox.showerror(
                "Error",
                "Arrival Time must be >= 0"
            )

            return None

        if burst <= 0:

            messagebox.showerror(
                "Error",
                "Burst Time must be > 0"
            )

            return None

        quantum_str = self.quantum_entry.get().strip()

        try:

            quantum = int(quantum_str)

        except ValueError:

            messagebox.showerror(
                "Error",
                "All values must be integers"
            )

            return None

        if quantum <= 0:

            messagebox.showerror(
                "Error",
                "Quantum Time must be > 0"
            )

            return None

        for process in self.processes:

            if process.pid == pid:

                messagebox.showerror(
                    "Error",
                    f"Process P{pid} already exists"
                )

                return None

        return pid, arrival, burst

    # =========================================================
    # ADD PROCESS
    # =========================================================
    def add(self):

        data = self.validate()

        if data is None:
            return

        pid, arrival, burst = data

        process = Process(pid, arrival, burst)

        self.processes.append(process)

        self.tree.insert(
            "",
            "end",
            values=(pid, arrival, burst)
        )

        for entry in self.entries:
            entry.delete(0, tk.END)

        messagebox.showinfo(
            "Success",
            f"Process P{pid} added successfully"
        )

    # =========================================================
    # RUN SIMULATION
    # =========================================================
    def run(self):

        if not self.processes:

            messagebox.showerror(
                "Error",
                "No processes added"
            )

            return

        # ---------- QUANTUM ----------
        quantum_str = self.quantum_entry.get().strip()

        try:

            quantum = int(quantum_str)

        except ValueError:

            return

        if quantum <= 0:

            return

        # ---------- COPY ----------
        srtf_processes = copy.deepcopy(self.processes)
        rr_processes = copy.deepcopy(self.processes)

        # ---------- RUN ----------
        gantt_srtf = run_srtf(srtf_processes)

        gantt_rr = run_round_robin(
            rr_processes,
            quantum
        )

        # ---------- METRICS ----------
        avg_srtf = calculate_metrics(srtf_processes)
        avg_rr = calculate_metrics(rr_processes)

        # ---------- SORT ----------
        srtf_processes.sort(key=lambda p: p.pid)
        rr_processes.sort(key=lambda p: p.pid)

        # ---------- CLEAR TABLES ----------
        for table in [self.srtf_table, self.rr_table]:

            for item in table.get_children():
                table.delete(item)

        # ---------- INSERT SRTF ----------
        for process in srtf_processes:

            self.srtf_table.insert(
                "",
                "end",
                values=(
                    process.pid,
                    process.waiting_time,
                    process.turnaround_time,
                    process.response_time
                )
            )

        # ---------- INSERT RR ----------
        for process in rr_processes:

            self.rr_table.insert(
                "",
                "end",
                values=(
                    process.pid,
                    process.waiting_time,
                    process.turnaround_time,
                    process.response_time
                )
            )

        # ================= COMPARISON =================
        self.comp_text.config(
            text=
            f"SRTF Averages:\n"
            f"WT = {avg_srtf[0]:.2f}\n"
            f"TAT = {avg_srtf[1]:.2f}\n"
            f"RT = {avg_srtf[2]:.2f}\n\n"
            f"Round Robin Averages:\n"
            f"WT = {avg_rr[0]:.2f}\n"
            f"TAT = {avg_rr[1]:.2f}\n"
            f"RT = {avg_rr[2]:.2f}"
        )

        # ================= CONCLUSION =================
        conclusion = (
            "SRTF provides better efficiency and lower waiting time.\n"
            "Round Robin provides better fairness and responsiveness."
        )

        self.conclusion_text.config(text=conclusion)

        # ================= GANTT =================
        self.gantt_srtf.clear()
        self.gantt_rr.clear()

        self.gantt_srtf.draw(gantt_srtf)
        self.gantt_rr.draw(gantt_rr)

    # =========================================================
    # RESET
    # =========================================================
    def reset(self):

        self.processes.clear()

        for entry in self.entries:
            entry.delete(0, tk.END)

        self.quantum_entry.delete(0, tk.END)

        for table in [
            self.tree,
            self.srtf_table,
            self.rr_table
        ]:

            for item in table.get_children():
                table.delete(item)

        self.comp_text.config(text="")
        self.conclusion_text.config(text="")

        self.gantt_srtf.clear()
        self.gantt_rr.clear()

        messagebox.showinfo(
            "Reset",
            "All data cleared successfully"
        )


# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":

    root = tk.Tk()

    app = MainWindow(root)

    root.mainloop()