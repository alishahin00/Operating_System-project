import tkinter as tk


class GanttFrame:

    def __init__(self, root, title):

        self.frame = tk.LabelFrame(root, text=title)
        self.frame.pack(fill="x", padx=10, pady=5)


        self.canvas = tk.Canvas(
            self.frame,
            height=130,
            bg="white"
        )

        self.h_scroll = tk.Scrollbar(
            self.frame,
            orient="horizontal",
            command=self.canvas.xview
        )

        self.canvas.configure(
            xscrollcommand=self.h_scroll.set
        )

        self.canvas.pack(fill="x", expand=True)
        self.h_scroll.pack(fill="x")


    def draw(self, gantt):

        self.canvas.delete("all")

        if not gantt:
            return

        x = 20
        top = 30
        bottom = 70

        scale = 35

        for process_name, start, end in gantt:

            duration = end - start

            width = duration * scale


            color = "lightblue"

            if process_name == "Idle":
                color = "lightgray"


            self.canvas.create_rectangle(
                x,
                top,
                x + width,
                bottom,
                fill=color,
                outline="black"
            )


            self.canvas.create_text(
                x + width / 2,
                50,
                text=process_name,
                font=("Arial", 10, "bold")
            )


            self.canvas.create_text(
                x,
                85,
                text=str(start),
                font=("Arial", 9)
            )

            x += width


        self.canvas.create_text(
            x,
            85,
            text=str(gantt[-1][2]),
            font=("Arial", 9)
        )


        self.canvas.config(
            scrollregion=(0, 0, x + 50, 120)
        )


    def clear(self):

        self.canvas.delete("all")

        self.canvas.config(
            scrollregion=(0, 0, 0, 0)
        )