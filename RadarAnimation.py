"""
Radar Animation that showcases VCP 12, 212, 35, and 215 scan patterns. Includes options for SAILS or MRLE style scans to be added into the VCP runs.

Authored by Ben McKinney, Student Volunteer at the Fort-Worth/Dallas WFO. 

Last update: 6/27/2025

GitHub Link: https://github.com/Hawklight1/NWSRadarAnimation

"""

import tkinter as tk
import math
from PIL import Image, ImageTk
from copy import deepcopy
import webbrowser
from tkinter import ttk

# Radar settings
WIDTH = 550
HEIGHT = 550
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2
RADIUS = 250

class RadarApp:
    def __init__(self, root):
        self.root = root

        # Frames and UI
        self.radar_frame = tk.Frame(root)
        self.radar_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.vcp_title_label = tk.Label(self.radar_frame, text="VCP", font=("Helvetica", 20, "bold"))
        self.vcp_title_label.pack(pady=(0, 10))

        self.canvas = tk.Canvas(self.radar_frame, width=WIDTH, height=HEIGHT, bg='white')
        self.canvas.pack()

        # Horizontal wrapper for control panel
        self.control_wrapper = tk.Frame(root)
        self.control_wrapper.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        # Left panel: VCP buttons
        self.vcp_panel = tk.Frame(self.control_wrapper)
        self.vcp_panel.pack(side=tk.LEFT, padx=(0, 20), anchor='n')

        tk.Label(self.vcp_panel, text="VCP Patterns", font=("Helvetica", 24, "bold")).pack(pady=(10, 10))
        ttk.Separator(self.vcp_panel, orient='horizontal').pack(fill='x', pady=5)
        self.vcp_buttons = ["VCP 12", "VCP 35", "VCP 212", "VCP 215"]
        for vcp_name in self.vcp_buttons:
            tk.Button(self.vcp_panel, text=vcp_name, font=("Helvetica", 16, "bold"),
                      width=12, command=lambda name=vcp_name: self.set_vcp(name)).pack(pady=10)
        ttk.Separator(self.vcp_panel, orient='horizontal').pack(fill='x', pady=5)

        # Right column (options + logo)
        self.right_controls = tk.Frame(self.control_wrapper)
        self.right_controls.pack(side=tk.LEFT, anchor='n', padx=(0, 10))

        # Inside right_controls: the labeled options panel
        self.option_panel = tk.LabelFrame(self.right_controls, text="Options", font=("Helvetica", 14, "bold"))
        self.option_panel.pack(anchor='n', pady=(110, 200))

        tk.Label(self.option_panel, text="SAILS", font=("Helvetica", 14, "bold")).pack(pady=(10, 0))
        self.sails_var = tk.StringVar(value="None")
        self.sails_dropdown = tk.OptionMenu(self.option_panel, self.sails_var, "None", "SAILS 1", "SAILS 2", "SAILS 3", command=self.sails_selected)
        self.sails_dropdown.pack()

        tk.Label(self.option_panel, text="MRLE", font=("Helvetica", 14, "bold")).pack(pady=(15, 0))
        self.mrle_var = tk.StringVar(value="None")
        self.mrle_dropdown = tk.OptionMenu(self.option_panel, self.mrle_var, "None", "MRLE 2", "MRLE 3", "MRLE 4", command=self.mrle_selected)
        self.mrle_dropdown.pack()

        self.fast_forward = tk.Frame(self.vcp_panel)
        self.fast_forward.pack(pady=15)

        tk.Label(self.fast_forward, text="Speed", font=("Helvetica", 18)).pack(pady=0)
        self.fast_button = tk.Button(self.fast_forward, text="1x", font=("Helvetica", 16, "bold"),
                                     width=12, command=self.speed_multiply)
        self.fast_button.pack(pady=5)
        ttk.Separator(self.vcp_panel, orient='horizontal').pack(fill='x', pady=5)

        self.toggle_button = tk.Button(self.vcp_panel, text="Run", width=12, font=("Helvetica", 16, "bold"),
                                       command=self.toggle_animation, state=tk.DISABLED)
        self.toggle_button.pack(pady=10)

        # Radar logic vars
        self.angle = 90
        self.running = False
        self.vcp_selected = False
        self.speed_multiplier = 1
        self.fast_mode = 1
        self.sweep_progress = 0
        self.pattern_step_index = 0
        self.pattern_sequence = []
        self.sweep_cone = []

        self.label_colors = {
            "Z": "#7394BA",
            "V": "#D39494",
            "Z/V": "#805C92"    # Doesn't actually get used
        }

        self.draw_static_elements()

        # "More Info" hyperlink

        tk.Frame(self.vcp_panel).pack(expand=True, fill='both')

        self.more_info_link = tk.Label(self.vcp_panel, text="More Info", font=("Helvetica", 14, "underline"), fg="blue", cursor="hand2")
        self.more_info_link.pack(pady=(20, 5))
        self.more_info_link.bind("<Button-1>", lambda e: webbrowser.open_new("https://docs.google.com/spreadsheets/d/1gJOoY1DBSZMOYpcr7YDRyP_9xr7K7DVnPmAeFoB9Hfg/edit?gid=0#gid=0"))

        # Spacer to push logo down
        tk.Frame(self.right_controls).pack(expand=True, fill='both')

        # Now add logo under the options panel (but outside the box)
        logo = Image.open("NWS.png").resize((100, 100), Image.LANCZOS)
        self.logo_photo = ImageTk.PhotoImage(logo)

        self.logo_label = tk.Label(self.right_controls, image=self.logo_photo)
        self.logo_label.pack(pady=(10, 5), anchor='s')

    def draw_static_elements(self):
        for r in range(50, RADIUS + 1, 50):
            self.canvas.create_oval(CENTER_X - r, CENTER_Y - r, CENTER_X + r, CENTER_Y + r, outline='grey')
            self.canvas.create_text(CENTER_X + r + 15, CENTER_Y, text=str(r), font=("Helvetica", 10, "bold"))

        self.canvas.create_oval(CENTER_X - 5, CENTER_Y - 5, CENTER_X + 5, CENTER_Y + 5, fill='black', outline='')

        self.z_label = self.canvas.create_text(40, HEIGHT - 20, text="Z", font=("Helvetica", 24))
        self.angle_label = self.canvas.create_text(WIDTH - 40, HEIGHT - 20, text="0.5°", font=("Helvetica", 24))

    def toggle_animation(self):
        if not self.vcp_selected:
            print("Please select a VCP pattern first.")
            return
        if not self.running:
            self.pattern_step_index = 0
            self.advance_pattern_step()
            self.angle = 90
            self.running = True
            self.toggle_button.config(text="Stop")
            self.animate()
        else:
            self.running = False
            self.toggle_button.config(text="Run")

    def animate(self):
        if not self.running:
            return

        self.draw_sweep_cone()

        self.sweep_progress += abs(self.sweep_speed) * 5
        self.angle -= abs(self.sweep_speed) * 5

        if self.angle <= -270:
            self.angle = 90
            self.pattern_step_index += 1
            if self.pattern_step_index >= len(self.pattern_sequence):
                self.pattern_step_index = 0
                self.running = False
                self.toggle_button.config(text="Run")
                return
            self.advance_pattern_step()

        self.root.after(25, self.animate)

    def draw_sweep_cone(self):
        for cone in self.sweep_cone:
            self.canvas.delete(cone)
        self.sweep_cone = []

        angle_rad = math.radians(self.angle)
        half_width = math.radians(self.cone_angle_width / 2)

        if self.current_label == "Z/V":
            pattern = self.pattern_sequence[self.pattern_step_index]
            offset = math.radians(4)

            for mode, color, rng, offset_dir in [("Z", "Z", pattern["range_z"], -1), ("V", "V", pattern["range_v"], 1)]:
                center = angle_rad + offset_dir * offset
                x1 = CENTER_X + rng * math.cos(center - half_width)
                y1 = CENTER_Y - rng * math.sin(center - half_width)
                x2 = CENTER_X + rng * math.cos(center + half_width)
                y2 = CENTER_Y - rng * math.sin(center + half_width)
                self.sweep_cone.append(self.canvas.create_polygon(CENTER_X, CENTER_Y, x1, y1, x2, y2,
                                                                  fill=self.label_colors[color], outline=''))
        else:
            x1 = CENTER_X + self.sweep_radius * math.cos(angle_rad - half_width)
            y1 = CENTER_Y - self.sweep_radius * math.sin(angle_rad - half_width)
            x2 = CENTER_X + self.sweep_radius * math.cos(angle_rad + half_width)
            y2 = CENTER_Y - self.sweep_radius * math.sin(angle_rad + half_width)
            color = self.label_colors.get(self.current_label, "#888888")
            self.sweep_cone.append(self.canvas.create_polygon(CENTER_X, CENTER_Y, x1, y1, x2, y2,
                                                              fill=color, outline=''))

    def advance_pattern_step(self):
        if not self.pattern_sequence:
            print("Pattern sequence is empty!")
            self.running = False
            self.toggle_button.config(text="Run")
            return

        if self.pattern_step_index >= len(self.pattern_sequence):
            self.pattern_step_index = 0

        self.sweep_progress = 0
        self.angle = 90
        pattern = self.pattern_sequence[self.pattern_step_index]

        self.sweep_speed = pattern["speed"] * self.speed_multiplier
        self.cone_angle_width = pattern["cone_width"]
        self.current_label = pattern["label"]

        if self.current_label != "Z/V":
            self.sweep_radius = pattern["range"]
        else:
            self.sweep_radius = max(pattern.get("range_z", 0), pattern.get("range_v", 0))

        self.canvas.itemconfig(self.z_label, text=self.current_label)
        self.canvas.itemconfig(self.angle_label, text=pattern["angle"])

    def speed_multiply(self):
        self.fast_mode = (self.fast_mode % 4) + 1
        self.speed_multiplier = 2 ** (self.fast_mode - 1)
        self.fast_button.config(text=f"{self.speed_multiplier}x")
        if self.pattern_sequence:
            self.advance_pattern_step()

    def sails_selected(self, _):
        if not self.vcp_selected:
            self.sails_var.set("None")
            return

        if self.sails_var.get() != "None":
            self.mrle_var.set("None")
            self.mrle_dropdown.config(state="disabled")
        else:
            # Only re-enable MRLE if current VCP supports it
            if self.selected_vcp in ["VCP 212", "VCP 12"]:
                self.mrle_dropdown.config(state="normal")
        self.running = False
        self.pattern_step_index = 0
        self.angle = 90
        self.build_pattern_sequence()
        self.advance_pattern_step()

    def set_sails(self, value):
        self.sails_var.set(value)
        self.sails_selected(None)

    def mrle_selected(self, _):
        if not self.vcp_selected:
            self.mrle_var.set("None")
            return

        if self.mrle_var.get() != "None":
            self.sails_var.set("None")
            self.sails_dropdown.config(state="disabled")
        else:
            self.sails_dropdown.config(state="normal")
        self.running = False
        self.pattern_step_index = 0
        self.angle = 90
        self.build_pattern_sequence()
        self.advance_pattern_step()
    
    def set_vcp(self, vcp_name):
        self.running = False
        self.vcp_selected = True
        self.toggle_button.config(text="Run", state=tk.NORMAL)
        self.vcp_title_label.config(text=vcp_name)
        self.selected_vcp = vcp_name
        self.sails_var.set("None")
        self.mrle_var.set("None")

        # Enable/disable MRLE dropdown depending on VCP
        if vcp_name in ["VCP 212", "VCP 12"]:
            self.mrle_dropdown.config(state="normal")
        else:
            self.mrle_dropdown.config(state="disabled")
            self.mrle_var.set("None")

        # Adjust SAILS options
        menu = self.sails_dropdown["menu"]
        menu.delete(0, "end")

        if vcp_name == "VCP 35":
            # Only allow "None" and "SAILS 1"
            for option in ["None", "SAILS 1"]:
                menu.add_command(label=option, command=lambda value=option: self.set_sails(value))
        else:
            # Allow full SAILS options
            for option in ["None", "SAILS 1", "SAILS 2", "SAILS 3"]:
                menu.add_command(label=option, command=lambda value=option: self.set_sails(value))

        self.sails_var.set("None")
        self.sails_dropdown.config(state="normal")

        self.build_pattern_sequence()
        self.advance_pattern_step()


        if vcp_name in ["VCP 212", "VCP 12"]:
            self.mrle_dropdown.config(state="normal")
        else:
            self.mrle_dropdown.config(state="disabled")
            self.mrle_var.set("None")

        self.build_pattern_sequence()
        self.advance_pattern_step()

    def build_pattern_sequence(self):
        self.pattern_sequence = []
        patterns = {
            "VCP 212": [
                {"label": "Z", "angle": "0.5°", "speed": -.35, "cone_width": 8, "range": 250},
                {"label": "V", "angle": "0.5°", "speed": -.29, "cone_width": 8, "range": 74},
                {"label": "Z", "angle": "0.9°", "speed": -.35, "cone_width": 8, "range": 250},
                {"label": "V", "angle": "0.9°", "speed": -.29, "cone_width": 8, "range": 74},
                {"label": "Z", "angle": "1.3°", "speed": -.38, "cone_width": 8, "range": 231},
                {"label": "V", "angle": "1.3°", "speed": -.29, "cone_width": 8, "range": 74},
                {"label": "Z/V", "angle": "1.8°", "speed": -.43, "cone_width": 8, "range_z": 208, "range_v": 80},
                {"label": "Z/V", "angle": "2.4°", "speed": -.46, "cone_width": 8, "range_z": 181, "range_v": 80},
                {"label": "Z/V", "angle": "3.1°", "speed": -.46, "cone_width": 8, "range_z": 158, "range_v": 80},
                {"label": "Z/V", "angle": "4.0°", "speed": -.46, "cone_width": 8, "range_z": 134, "range_v": 80},
                {"label": "Z/V", "angle": "5.1°", "speed": -.46, "cone_width": 8, "range_z": 113, "range_v": 80},
                {"label": "Z/V", "angle": "6.4°", "speed": -.46, "cone_width": 8, "range_z": 94, "range_v": 80},
                {"label": "V", "angle": "8.0°", "speed": -.5, "cone_width": 8, "range": 74},
                {"label": "V", "angle": "10.0°", "speed": -.5, "cone_width": 8, "range": 68},
                {"label": "V", "angle": "12.5°", "speed": -.5, "cone_width": 8, "range": 63},
                {"label": "V", "angle": "15.6°", "speed": -.5, "cone_width": 8, "range": 63},
                {"label": "V", "angle": "19.5°", "speed": -.5, "cone_width": 8, "range": 63}
            ],
            "VCP 35": [
                {"label": "Z",   "angle": "0.5°", "speed": -0.08, "cone_width": 8, "range": 250},
                {"label": "V",   "angle": "0.5°", "speed": -0.26, "cone_width": 8, "range": 80},
                {"label": "Z",   "angle": "0.9°", "speed": -0.08, "cone_width": 8, "range": 250},
                {"label": "V",   "angle": "0.9°", "speed": -0.26, "cone_width": 8, "range": 80},
                {"label": "Z",   "angle": "1.3°", "speed": -0.09, "cone_width": 8, "range": 231},
                {"label": "V",   "angle": "1.3°", "speed": -0.26, "cone_width": 8, "range": 80},
                {"label": "Z/V", "angle": "1.8°", "speed": -0.26, "cone_width": 8, "range_z": 208, "range_v": 80},
                {"label": "Z/V", "angle": "2.4°", "speed": -0.30, "cone_width": 8, "range_z": 181, "range_v": 80},
                {"label": "Z/V", "angle": "3.1°", "speed": -0.29, "cone_width": 8, "range_z": 158, "range_v": 80},
                {"label": "Z/V", "angle": "4.0°", "speed": -0.30, "cone_width": 8, "range_z": 134, "range_v": 80},
                {"label": "Z/V", "angle": "5.1°", "speed": -0.30, "cone_width": 8, "range_z": 134, "range_v": 80},
                {"label": "Z/V", "angle": "6.4°", "speed": -0.30, "cone_width": 8, "range_z": 134, "range_v": 80},
            ],
            "VCP 215": [
                {"label": "Z",   "angle": "0.5°",  "speed": -0.19, "cone_width": 8, "range": 250},
                {"label": "V",   "angle": "0.5°",  "speed": -0.29, "cone_width": 8, "range": 74},
                {"label": "Z",   "angle": "0.9°",  "speed": -0.22, "cone_width": 8, "range": 250},
                {"label": "V",   "angle": "0.9°",  "speed": -0.29, "cone_width": 8, "range": 74},
                {"label": "Z",   "angle": "1.3°",  "speed": -0.26, "cone_width": 8, "range": 231},
                {"label": "V",   "angle": "1.3°",  "speed": -0.29, "cone_width": 8, "range": 74},
                {"label": "Z/V", "angle": "1.8°",  "speed": -0.29, "cone_width": 8, "range_z": 208, "range_v": 80},
                {"label": "Z/V", "angle": "2.4°",  "speed": -0.33, "cone_width": 8, "range_z": 181, "range_v": 80},
                {"label": "Z/V", "angle": "3.1°",  "speed": -0.33, "cone_width": 8, "range_z": 158, "range_v": 80},
                {"label": "Z/V", "angle": "4.0°",  "speed": -0.33, "cone_width": 8, "range_z": 134, "range_v": 80},
                {"label": "Z/V", "angle": "5.1°",  "speed": -0.33, "cone_width": 8, "range_z": 134, "range_v": 80},
                {"label": "Z/V", "angle": "6.4°",  "speed": -0.33, "cone_width": 8, "range_z": 134, "range_v": 80},
                {"label": "V",   "angle": "8.0°",  "speed": -0.43, "cone_width": 8, "range": 63},
                {"label": "V",   "angle": "10.0°", "speed": -0.43, "cone_width": 8, "range": 63},
                {"label": "V",   "angle": "12.0°", "speed": -0.43, "cone_width": 8, "range": 63},
                {"label": "V",   "angle": "14.0°", "speed": -0.43, "cone_width": 8, "range": 63},
                {"label": "V",   "angle": "16.7°", "speed": -0.43, "cone_width": 8, "range": 63},
                {"label": "V",   "angle": "19.5°", "speed": -0.43, "cone_width": 8, "range": 63},
            ],
            "VCP 12": [
                {"label": "Z",   "angle": "0.5°",  "speed": -0.35, "cone_width": 8, "range": 250},
                {"label": "V",   "angle": "0.5°",  "speed": -0.40, "cone_width": 8, "range": 80},
                {"label": "Z",   "angle": "0.9°",  "speed": -0.35, "cone_width": 8, "range": 250},
                {"label": "V",   "angle": "0.9°",  "speed": -0.40, "cone_width": 8, "range": 80},
                {"label": "Z",   "angle": "1.3°",  "speed": -0.38, "cone_width": 8, "range": 231},
                {"label": "V",   "angle": "1.3°",  "speed": -0.40, "cone_width": 8, "range": 80},
                {"label": "Z/V", "angle": "1.8°",  "speed": -0.43, "cone_width": 8, "range_z": 208, "range_v": 80},
                {"label": "Z/V", "angle": "2.4°",  "speed": -0.43, "cone_width": 8, "range_z": 181, "range_v": 80},
                {"label": "Z/V", "angle": "3.1°",  "speed": -0.43, "cone_width": 8, "range_z": 158, "range_v": 80},
                {"label": "Z/V", "angle": "4.0°",  "speed": -0.46, "cone_width": 8, "range_z": 134, "range_v": 80},
                {"label": "Z/V", "angle": "5.1°",  "speed": -0.43, "cone_width": 8, "range_z": 134, "range_v": 80},
                {"label": "Z/V", "angle": "6.4°",  "speed": -0.43, "cone_width": 8, "range_z": 134, "range_v": 80},
                {"label": "V",   "angle": "8.0°",  "speed": -0.46, "cone_width": 8, "range": 74},
                {"label": "V",   "angle": "10.0°", "speed": -0.46, "cone_width": 8, "range": 68},
                {"label": "V",   "angle": "12.5°", "speed": -0.46, "cone_width": 8, "range": 63},
                {"label": "V",   "angle": "15.6°", "speed": -0.46, "cone_width": 8, "range": 63},
                {"label": "V",   "angle": "19.5°", "speed": -0.46, "cone_width": 8, "range": 63},
            ]
        }

        pattern = deepcopy(patterns.get(self.selected_vcp, []))
        if not pattern:
            self.pattern_sequence = []
            return

        # Add SAILS - limit options if VCP 35
        sails = self.sails_var.get()
        if sails != "None":
            sails_scans = [
                {"label": "Z", "angle": "0.5°", "speed": -0.5, "cone_width": 8, "range": 250},
                {"label": "V", "angle": "0.5°", "speed": -0.5, "cone_width": 8, "range": 80}
            ]
            insert_points = {
                "SAILS 1": ["3.1°"],
                "SAILS 2": ["1.8°", "6.4°"],
                "SAILS 3": ["1.3°", "4.0°", "8.0°"]
            }

            for angle in insert_points.get(sails, []):
                # Find index of the LAST step that has this angle
                for i in reversed(range(len(pattern))):
                    if pattern[i]["angle"] == angle:
                        # Optional: further refine to match only "V" label if needed
                        if angle == "1.3°" and sails == "SAILS 3" and pattern[i]["label"] == "V":
                            pattern[i + 1:i + 1] = deepcopy(sails_scans)
                            break
                        elif angle != "1.3°" or sails != "SAILS 3":
                            pattern[i + 1:i + 1] = deepcopy(sails_scans)
                            break



        mrle = self.mrle_var.get()
        if mrle != "None" and self.selected_vcp in ["VCP 212", "VCP 12"]:
            count = int(mrle[-1])

            # Base MRLE scans for 0.5 and 0.9 degrees
            mrle_scans = [
                {"label": "Z", "angle": "0.5°", "speed": -0.35, "cone_width": 8, "range": 250},
                {"label": "V", "angle": "0.5°", "speed": -0.40, "cone_width": 8, "range": 80},
                {"label": "Z", "angle": "0.9°", "speed": -0.35, "cone_width": 8, "range": 250},
                {"label": "V", "angle": "0.9°", "speed": -0.40, "cone_width": 8, "range": 80}
            ]

            # Add 1.3° if MRLE 3 or higher
            if count >= 3:
                mrle_scans.append({"label": "Z", "angle": "1.3°", "speed": -0.38, "cone_width": 8, "range": 231})
                mrle_scans.append({"label": "V", "angle": "1.3°", "speed": -0.40, "cone_width": 8, "range": 80})

            # Add single dual-cone 1.8° if MRLE 4
            if count == 4:
                mrle_scans.append({"label": "Z/V", "angle": "1.8°", "speed": -0.43, "cone_width": 8, "range_z": 208, "range_v": 80})

            # Insert after last 5.1°
            insert_points = [i for i, step in enumerate(pattern) if step["angle"] == "5.1°"]
            if insert_points:
                insert_idx = insert_points[-1]
                pattern[insert_idx + 1:insert_idx + 1] = deepcopy(mrle_scans)

        self.pattern_sequence = pattern

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Radar VCP Animation")
    app = RadarApp(root)
    root.mainloop()
