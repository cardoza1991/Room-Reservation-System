import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from PIL import Image, ImageTk

class RoomReservationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Room Reservation System")
        self.root.geometry("1000x800")
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        
        # Configure styles
        self.style.configure("TFrame", background="#f5f5dc")  # Beige background
        self.style.configure("TLabel", background="#f5f5dc", foreground="#4b3832", font=("Georgia", 12))
        self.style.configure("TButton", background="#fff8e1", font=("Georgia", 10), foreground="#4b3832", padding=5)
        self.style.configure("TOptionMenu", background="#fff8e1", font=("Georgia", 10), foreground="#4b3832")
        self.style.configure("TEntry", font=("Georgia", 10))
        self.style.configure("Red.TButton", background="#ffcccc", foreground="#cc0000", font=("Georgia", 10))
        self.style.configure("Selected.TButton", background="#b0c4de", foreground="#4b3832", font=("Georgia", 10))

        # Load icons
        self.icon_reserve = ImageTk.PhotoImage(Image.open("reserve_icon.png").resize((20, 20)))
        self.icon_show = ImageTk.PhotoImage(Image.open("show_icon.png").resize((20, 20)))

        # Sample rooms data
        self.rooms = {
            "Study Room 1": [],
            "Study Room 2": [],
            "Study Room 3": [],
            "Study Room 4": [],
            "Study Room 5": [],
            "Conference Room": [],
            "LRE Room": []
        }

        self.selected_date = None
        self.selected_room = tk.StringVar(self.root)
        self.selected_room.set("Select a room")
        self.selected_time_slots = []
        self.selected_purpose = ""
        self.time_slot_buttons = {}

        self.create_widgets()

    def create_widgets(self):
        tab_control = ttk.Notebook(self.root)
        
        reservation_tab = ttk.Frame(tab_control, padding="10")
        availability_tab = ttk.Frame(tab_control, padding="10")
        
        tab_control.add(reservation_tab, text='Reservations')
        tab_control.add(availability_tab, text='Room Availability')
        
        tab_control.pack(expand=1, fill='both')

        # Header with logo
        header_frame = ttk.Frame(self.root, style="TFrame")
        header_frame.pack(side=tk.TOP, fill=tk.X)
        self.logo = ImageTk.PhotoImage(Image.open("icon.webp").resize((100, 100)))
        logo_label = ttk.Label(header_frame, image=self.logo, style="TLabel")
        logo_label.pack(side=tk.LEFT, padx=10, pady=10)
        ttk.Label(header_frame, text="Room Reservation System", font=("Georgia", 24, 'bold')).pack(side=tk.LEFT, padx=10, pady=10)

        # Reservation Tab
        ttk.Label(reservation_tab, text="Select Room:", font=("Georgia", 14, 'bold')).pack(pady=10)
        self.room_menu = ttk.OptionMenu(reservation_tab, self.selected_room, "Select a room", *self.rooms.keys(), command=self.update_calendar)
        self.room_menu.pack(pady=5)

        ttk.Label(reservation_tab, text="Select Date:", font=("Georgia", 14, 'bold')).pack(pady=10)
        self.calendar = Calendar(reservation_tab, selectmode="day", date_pattern='yyyy-mm-dd', background='blue', foreground='white', headersbackground='gold')
        self.calendar.pack(pady=10)
        self.calendar.bind("<<CalendarSelected>>", self.update_time_slots)

        ttk.Label(reservation_tab, text="Select Time Slot(s):", font=("Georgia", 14, 'bold')).pack(pady=10)
        self.time_slots_frame = ttk.Frame(reservation_tab)
        self.time_slots_frame.pack(pady=5)

        ttk.Label(reservation_tab, text="Purpose:", font=("Georgia", 14, 'bold')).pack(pady=10)
        self.purpose_entry = ttk.Entry(reservation_tab, width=50)
        self.purpose_entry.pack(pady=5)

        ttk.Button(reservation_tab, text="Reserve Room", command=self.reserve_room, image=self.icon_reserve, compound=tk.LEFT).pack(pady=20)

        # Availability Tab
        ttk.Label(availability_tab, text="Room Availability", font=("Georgia", 16, 'bold')).pack(pady=10)
        self.availability_frame = ttk.Frame(availability_tab)
        self.availability_frame.pack(fill='both', expand=True, pady=20)

        self.update_room_availability()

    def generate_time_slots(self):
        time_slots = []
        for hour in range(10, 24):
            for minute in (0, 30):
                time_slots.append(f"{hour % 12 or 12:02d}:{minute:02d} {'AM' if hour < 12 else 'PM'}")
        return time_slots

    def update_time_slots(self, event=None):
        for widget in self.time_slots_frame.winfo_children():
            widget.destroy()
        
        self.selected_date = self.calendar.get_date()
        selected_room = self.selected_room.get()
        if selected_room == "Select a room":
            return
        
        reservations = self.rooms[selected_room]
        reserved_slots = {r["start_time"] for r in reservations if r["date"] == self.selected_date}
        
        time_slots = self.generate_time_slots()
        columns = 6
        self.time_slot_buttons = {}
        for i, time_slot in enumerate(time_slots):
            state = tk.NORMAL
            button_style = "TButton"
            if time_slot in reserved_slots:
                state = tk.DISABLED
                button_style = "Red.TButton"
            button = ttk.Button(self.time_slots_frame, text=time_slot, style=button_style, command=lambda ts=time_slot: self.toggle_time_slot(ts), state=state)
            button.grid(row=i // columns, column=i % columns, padx=5, pady=5)
            self.time_slot_buttons[time_slot] = button

    def toggle_time_slot(self, time_slot):
        if time_slot in self.selected_time_slots:
            self.selected_time_slots.remove(time_slot)
            self.time_slot_buttons[time_slot].config(style="TButton")
            self.time_slot_buttons[time_slot].state(["!disabled"])
        else:
            self.selected_time_slots.append(time_slot)
            self.time_slot_buttons[time_slot].config(style="Selected.TButton")
            self.time_slot_buttons[time_slot].state(["disabled"])

    def update_calendar(self, event=None):
        self.selected_room.set(event)
        self.update_time_slots(event)

    def update_room_availability(self):
        for widget in self.availability_frame.winfo_children():
            widget.destroy()

        for room, reservations in self.rooms.items():
            row_index = list(self.rooms.keys()).index(room)
            room_label = ttk.Label(self.availability_frame, text=room, width=20, anchor="w", font=("Georgia", 12))
            room_label.grid(row=row_index, column=0, padx=5, pady=5)

            availability_label = ttk.Label(self.availability_frame, text="Reserved" if reservations else "Available", foreground="red" if reservations else "green", width=30, anchor="w", font=("Georgia", 12))
            availability_label.grid(row=row_index, column=1)

            show_button = ttk.Button(self.availability_frame, text="Show Reservations", command=lambda r=room: self.show_reservations(r), image=self.icon_show, compound=tk.LEFT)
            show_button.grid(row=row_index, column=2, padx=5, pady=5)

    def show_reservations(self, room):
        reservations = self.rooms[room]
        if not reservations:
            messagebox.showinfo("Reservations", f"No reservations for {room}")
        else:
            reservation_list = "\n".join(f"Date: {r['date']}, Time: {r['start_time']} - {r['end_time']}, Purpose: {r['purpose']}" for r in reservations)
            messagebox.showinfo("Reservations", f"Reservations for {room}:\n{reservation_list}")

    def reserve_room(self):
        self.selected_purpose = self.purpose_entry.get()

        if not self.selected_date or not self.selected_time_slots or not self.selected_purpose:
            messagebox.showerror("Error", "Please select a date, at least one time slot, and enter a purpose.")
            return

        selected_room_name = self.selected_room.get()
        if selected_room_name == "Select a room":
            messagebox.showerror("Error", "Please select a room.")
            return

        reservation = {
            "date": self.selected_date,
            "start_time": min(self.selected_time_slots),
            "end_time": self.calculate_end_time(max(self.selected_time_slots)),
            "purpose": self.selected_purpose
        }

        self.rooms[selected_room_name].append(reservation)
        messagebox.showinfo("Success", f"Room '{selected_room_name}' has been reserved on {self.selected_date} from {reservation['start_time']} to {reservation['end_time']}.")

        self.update_room_availability()

    def calculate_end_time(self, end_time):
        hour, minute, period = int(end_time.split(":")[0]), int(end_time.split(":")[1][:2]), end_time.split()[1]
        if minute == 30:
            minute = 0
            hour = hour + 1 if hour < 12 else 1
        else:
            minute = 30
        return f"{hour:02d}:{minute:02d} {period}"

if __name__ == "__main__":
    root = tk.Tk()
    app = RoomReservationApp(root)
    
    app.style.configure("Red.TButton", background="#ffcccc", foreground="#cc0000", font=("Georgia", 10))
    app.style.configure("Selected.TButton", background="#b0c4de", foreground="#4b3832", font=("Georgia", 10))

    root.mainloop()
