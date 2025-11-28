import tkinter as tk
import ttkbootstrap as ttk
import time

class Rumble(ttk.Frame):
    def __init__(self, rumble_frame, configs):
        super().__init__(rumble_frame)
        
        self.rumble_frame = rumble_frame

        self.configs = configs

        self.CANVAS_WIDTH = 240
        self.CANVAS_HEIGHT = 500
        self.BAR_WIDTH = 200
        self.BAR_HEIGHT = 20

        # Relevant things found in configs
        # rumble_mini: bool = False
        # rumble_bars_natural_width: bool = False
        # rumble_show_drop_off: bool = True

        self.COLOURS = {
            "white": "#ffffff",
            "grey": "#808080", 
            "light_grey": "#d3d3d3",
            "yellow": "#ffd700",
            "gold": "#daa520",
            "black": "#000000",
            "bg": "#2b2b2b"
        }

        self._load_rumble_dictionary()
        self.set_start_time()

        self._build_ui()
        self._update_display()


    def set_start_time(self):
        self.start_time = time.monotonic()
        self.set_rumble_active(True)

    def _calc_minutes_passed(self):
        time_passed = time.monotonic() - self.start_time
        minutes_passed = int(time_passed // 60)
        minutes_passed = min(minutes_passed, 15)
        return minutes_passed

    def _find_current_punch_sizes(self, minutes_passed: int):
        return self.rumble_dictionary[minutes_passed]

    def _load_rumble_dictionary(self):
        self.rumble_dictionary = {
            0: {2: [2, 1, 1, 7], 3: [6, 2, 1, 5], 4: [8, 3, 1, 4], 6: [6, 4, 1, 4], 7: [8, 5, 1, 4], 8: [8, 6, 1, 4], 10: [8, 7, 1, 4], 11: [10, 9, 2, 3], 12: [12, 11, 2, 3], 13: [12, 12, 1, 3], 14: [12, 14, 2, 3], 15: [14, 16, 2, 2], 16: [16, 18, 2, 2], 17: [14, 19, 1, 2], 18: [14, 20, 1, 2]}, 
            1: {2: [2, 1, 1, 8], 3: [4, 2, 1, 6], 4: [5, 3, 1, 5], 5: [5, 4, 1, 4], 6: [7, 5, 1, 4], 7: [7, 6, 1, 4], 9: [5, 7, 1, 4], 10: [10, 11, 4, 3], 11: [10, 12, 1, 3], 12: [10, 14, 2, 3], 13: [12, 16, 2, 3], 14: [12, 18, 2, 2], 15: [12, 20, 2, 2]}, 
            2: {2: [0, 1, 1, 9], 3: [6, 3, 2, 4], 5: [6, 5, 2, 4], 6: [6, 6, 1, 4], 8: [8, 9, 3, 3], 9: [8, 11, 2, 3], 10: [9, 14, 3, 3], 11: [10, 16, 2, 2], 12: [10, 18, 2, 2], 13: [10, 20, 2, 2]}, 
            3: {2: [4, 2, 2, 5], 3: [4, 3, 1, 5], 4: [4, 4, 1, 5], 5: [5, 6, 2, 4], 7: [7, 9, 3, 3], 8: [7, 11, 2, 3], 9: [8, 14, 3, 3], 10: [10, 18, 4, 2], 11: [9, 19, 1, 2], 12: [9, 20, 1, 2]}, 
            4: {2: [3, 2, 2, 6], 3: [3, 3, 1, 6], 4: [5, 5, 2, 4], 5: [4, 6, 1, 4], 6: [4, 7, 1, 4], 7: [6, 11, 4, 3], 8: [7, 14, 3, 3], 9: [8, 18, 4, 2], 10: [8, 20, 2, 2]}, 
            5: {2: [4, 3, 3, 4], 3: [3, 4, 1, 5], 4: [4, 6, 2, 4], 5: [4, 7, 1, 4], 6: [6, 11, 4, 3], 7: [6, 14, 3, 3], 8: [7, 18, 4, 2], 9: [7, 20, 2, 2]}, 
            6: {2: [3, 3, 3, 5], 3: [3, 4, 1, 5], 4: [4, 6, 2, 4], 5: [5, 9, 3, 3], 6: [6, 12, 3, 3], 7: [7, 16, 4, 3], 8: [7, 19, 3, 2], 9: [7, 20, 1, 3]}, 
            7: {2: [3, 3, 3, 5], 3: [3, 5, 2, 4], 4: [3, 6, 1, 5], 5: [5, 11, 5, 3], 6: [5, 14, 3, 3], 7: [6, 18, 4, 2], 8: [6, 20, 2, 3]}, 
            8: {2: [2, 3, 3, 6], 3: [3, 5, 2, 5], 4: [3, 7, 2, 4], 5: [5, 12, 5, 3], 6: [6, 16, 4, 3], 7: [6, 20, 4, 2]}, 
            9: {2: [2, 3, 3, 6], 3: [3, 6, 3, 4], 4: [4, 9, 3, 4], 5: [5, 14, 5, 3], 6: [5, 18, 4, 2], 7: [5, 20, 2, 3]},
            10: {2: [2, 4, 4, 5], 3: [2, 6, 2, 5], 4: [4, 11, 5, 3], 5: [5, 16, 5, 3], 6: [5, 20, 4, 2]}, 
            11: {2: [2, 4, 4, 5], 3: [2, 6, 2, 5], 4: [4, 11, 5, 3], 5: [5, 18, 7, 2], 6: [5, 20, 2, 3]}, 
            12: {2: [2, 4, 4, 5], 3: [2, 7, 3, 4], 4: [3, 12, 5, 3], 5: [5, 19, 7, 2], 6: [4, 20, 1, 3]}, 
            13: {2: [2, 5, 5, 5], 3: [2, 7, 2, 5], 4: [4, 14, 7, 3], 5: [4, 20, 6, 2]}, 
            14: {2: [2, 5, 5, 5], 3: [3, 9, 4, 4], 4: [4, 16, 7, 3], 5: [4, 20, 4, 3]}, 
            15: {2: [2, 6, 6, 4], 3: [3, 11, 5, 3], 4: [4, 18, 7, 2], 5: [3, 20, 2, 3]}}
        # Outer key is minutes passed, inner key is charged groups
        # List is ["drop_off", "rows", "difference", "base_width"], drop_off assumes 3 balls per group.
        
        self.rumble_dictionary_text = {0: "15-16", 1: "12-13", 2: "10-11", 3: "8-10", 4: "7-9",  5: "6-8", 6: "6-7", 7: "6-7", 8: "6", 9: "5",
                                       10: "5", 11: "5", 12: "4", 13: "4", 14: "4", 15: "4"}
        # Key is minutes passed, value is groups that will be recommended on simplified mode.

    def _build_ui(self):
                
        self.canvas = tk.Canvas(
            self.rumble_frame, 
            width=self.CANVAS_WIDTH, 
            height=self.CANVAS_HEIGHT, 
            bg=self.COLOURS["bg"],
            highlightthickness=0
        )
        self.canvas.pack(padx=0, pady=0)

    def _update_display(self):
        if not self.rumble_active:
            return
        self.canvas.delete("all")

        if self.configs.rumble_mini:
            self._draw_text_mode()
        else: 
            self._draw_rumble_table()

        self.after(60001, self._update_display)

    
    def set_rumble_active(self, active: bool):
        self.rumble_active = active


    def _draw_text_mode(self):
        minutes_passed = self._calc_minutes_passed()
        recommended_groups = self.rumble_dictionary_text[minutes_passed]
        self.canvas.create_text(
            self.CANVAS_WIDTH // 2, 
            self.CANVAS_HEIGHT // 2,
            text=recommended_groups,
            fill="white",
            font=("Helvetica", 14)
        )

    def _draw_rumble_table(self):
        minutes_passed = self._calc_minutes_passed()
        punch_dictionary = self._find_current_punch_sizes(minutes_passed)

        start_x = 30
        start_y = self.CANVAS_HEIGHT - self.BAR_HEIGHT 

        current_x = start_x
        current_y = start_y

        colourful_state = "yellow"
        greyscale_state = "grey"

        # Sorting keys ensures we stack 1, 2, 3... in order
        for group_num in sorted(punch_dictionary.keys()):
            group_data = punch_dictionary[group_num]
            
            drop_off = group_data[0]
            rows_len = group_data[1]
            difference = group_data[2]
            width_factor = group_data[3]

            # Get the colour of the rectangle
            if 7 < rows_len < 19:
                text_colour = colourful_state
                block_colour = colourful_state
                colourful_state = "yellow" if colourful_state == "gold" else "gold"
            else:
                text_colour = greyscale_state
                block_colour = greyscale_state
                greyscale_state = "grey" if greyscale_state == "light_grey" else "light_grey"

            # Get the height and bottom y of the rectangle
            rect_h = difference * self.BAR_HEIGHT
            current_y -= rect_h

            # Get the width of the rectangle
            if self.configs.rumble_bars_natural_width:
                rect_w = (self.BAR_WIDTH * width_factor / 9)
            else:
                rect_w = (self.BAR_WIDTH)

            # Draw Box
            self.canvas.create_rectangle(
                current_x, 
                current_y, 
                current_x + rect_w, 
                current_y + rect_h,
                fill=self.COLOURS[block_colour],
                outline="black" 
            )

            # Draw Groups
            self.canvas.create_text(
                0,
                current_y,
                text=str(group_num),
                fill=self.COLOURS[block_colour],
                anchor="nw",
                font=("Arial", 10, "bold")
            )

            # Draw dropoff
            if self.configs.rumble_show_drop_off:
                self.canvas.create_text(
                    current_x + 3,
                    current_y,
                    text=str(drop_off),
                    fill=self.COLOURS["black"],
                    anchor="nw",
                    font=("Arial", 8)
                )


if __name__ == "__main__":
    class MockConfig:
        def __init__(self):
            self.rumble_mini = False
            self.rumble_bars_natural_width = True 
            self.rumble_show_drop_off = True

    root = ttk.Window(title="Rumble Frame Test", themename="darkly")
    root.geometry("600x400")

    configs = MockConfig()
    app = Rumble(root, configs)
    
    app.pack(fill="both", expand=True)

    def simulate_game_loop():
        # Artificial time acceleration:
        # Subtract 60 seconds from start_time to make the code think a minute passed
        
        
        # Calculate minutes internally used by your class
        mins = app._calc_minutes_passed()
        print(f"Simulating Minute: {mins}")

        app.canvas.delete("all")
        
        app._update_display()

        app.start_time -= 60 

        # Run this again in 1 second (2000ms)
        root.after(3500, simulate_game_loop)

    # Start the simulation
    root.after(2000, simulate_game_loop)
    
    root.mainloop()