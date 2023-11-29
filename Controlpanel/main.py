from datetime import datetime
from PIL import Image, ImageTk
import time
import pyglet
import socket
import subprocess
import json
import tkinter as tk
import cv2
import threading
import api_handles.missiondata as missiondata
import api_handles.mission_initiate as missioninitiate
import api_handles.terminatemission as terminate
import api_handles.data_upload as dataupload


drone_ip = 'raspberrypi.local'
drone_port = 5555
cam1_url = 'http://raspberrypi.local:8082/?action=stream'
cam2_url = 'http://raspberrypi.local:8081/?action=stream'
cap_cam_url = cam1_url


class ControllDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Underwater Drone Controler")
        self.root.attributes("-fullscreen", True)  # Makes the window full-screen
        self.root.overrideredirect(1)  # Hide the title bar

        self.drone_ip = drone_ip
        self.drone_port = drone_port
        self.current_uav_status = False
        self.snapshot_lock = threading.Lock()
        self.snapshot_thread = None
        self.threads_running = True
        self.joystick = None
        self.joystick_present = False
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.client_socket.settimeout(0.1)
        self.togglel1 = False
        self.togglel2 = False

        joysticks = pyglet.input.get_joysticks()
        if joysticks:
            self.joystick = joysticks[0]
            self.joystick.open()
            self.joystick_present = True

        # fake sensor data
        self.sensor_dataset = {
            "temp": 26.80,
            "pressure": 1,
            "ph": 7.45,
            "battery": 13.20,
        }

        self.init_frames()
        self.create_widgets()
        self.handle_joystick_inputs()
        self.start_video_threads()
        self.is_raspberry_pi_online()
        self.update_elapsed_time()
        self.fetch_sensor_data_thread()
        #self.update_sensor_frame(self.sensor_dataset)  # fake sensor data preview

    def init_frames(self):
        top_left = tk.Frame(self.root)
        top_left.grid(row=0, column=0, sticky="nw")
        top_center = tk.Frame(self.root)
        top_center.grid(row=0, column=1, sticky="new")
        top_right = tk.Frame(self.root)
        top_right.grid(row=0, column=2, sticky="ne")
        middle_left = tk.Frame(self.root)
        middle_left.grid(row=1, column=0, columnspan=2, sticky="nsw")
        middle_right = tk.Frame(self.root)
        middle_right.grid(row=1, column=2, sticky="nse")
        middle_right_top = tk.Frame(middle_right)
        middle_right_top.grid(row=0, column=0, sticky="nse")
        middle_right_bottom = tk.Frame(middle_right)
        middle_right_bottom.grid(row=1, column=0, sticky="nse")
        bottom_left = tk.Frame(self.root)
        bottom_left.grid(row=2, column=0, columnspan=2, sticky="sw")
        bottom_right = tk.Frame(self.root)
        bottom_right.grid(row=2, column=2, sticky="se")

        # Configure row and column weights to make the layout expandable
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        for i in range(3):
            self.root.grid_columnconfigure(i, weight=1)

        self.frame_mission = tk.LabelFrame(
            top_left, text="Mission Details", font=("Arial", 14, "bold")
        )
        self.frame_mission.grid(row=0, column=0, padx=10, pady=10, sticky="nsw")

        self.frame_connections = tk.LabelFrame(
            top_center, text="Connectivity", font=("Arial", 14, "bold")
        )
        self.frame_connections.grid(row=0, column=0, padx=10, pady=10, sticky="nsw")

        self.frame_telemetry = tk.LabelFrame(
            top_center, text="Telemetry", font=("Arial", 14, "bold")
        )
        self.frame_telemetry.grid(row=0, column=1, padx=10, pady=10, sticky="nse")

        self.frame_launch_status = tk.Frame(top_right)
        self.frame_launch_status.grid(row=0, column=0, padx=10, pady=10, sticky="nse")

        # border = tk.Frame(middle_left, height=2, background="black")
        # border.grid(row=0, column=0, sticky="ew")

        self.frame_front_webcam = tk.Frame(middle_left)
        self.frame_front_webcam.grid(row=0, column=0, padx=10, pady=10, sticky="nsw")

        self.frame_rear_webcam = tk.Frame(middle_right_top)
        self.frame_rear_webcam.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.frame_sensordata = tk.LabelFrame(
            middle_right_bottom, text="Sensor Data", font=("Arial", 14, "bold")
        )
        self.frame_sensordata.grid(row=0, column=0, padx=10, pady=0)
        self.frame_sensordata1 = tk.Frame(self.frame_sensordata)
        self.frame_sensordata1.grid(row=0, column=0, padx=10, pady=0, sticky="nw")
        self.frame_sensordata2 = tk.Frame(self.frame_sensordata)
        self.frame_sensordata2.grid(row=0, column=1, padx=40, pady=0, sticky="ne")

        self.frame_consolelog = tk.LabelFrame(
            bottom_left, text="Console log", font=("Arial", 14, "bold")
        )
        self.frame_consolelog.grid(row=0, column=0, padx=10, pady=10, sticky="nsw")
        self.frame_terminate = tk.Frame(bottom_right)
        self.frame_terminate.grid(row=0, column=2, padx=10, pady=10, sticky="nse")

    def create_widgets(self):
        self.mission_details()
        self.create_cams()
        self.joystick_status_update()
        self.create_labels()
        self.create_buttons()

    def mission_details(self):
        self.int_con_label = tk.Label(
            self.frame_connections, text=f"Internet Connectivity: NA"
        )
        self.int_con_label.grid(row=0, column=0, padx=10, pady=2, sticky="nw")
        self.sub_con_label = tk.Label(self.frame_connections, text=f"Submarine: NA")
        self.sub_con_label.grid(row=1, column=0, padx=10, pady=2, sticky="nw")

        json_mdata = missiondata.mission()
        mission_name = json_mdata[0]["mission_name"]
        objective = json_mdata[0]["mission_objective"]
        mission_location = json_mdata[0]["mission_location"]
        global start_time
        start_time = json_mdata[0]["start_time"]
        if json_mdata != "error":
            self.int_con_label.config(text=f"Internet Connectivity: Connected")
        else:
            self.int_con_label.config(text=f"Internet Connectivity: Disonnected")

        label1 = tk.Label(self.frame_mission, text=f"Mission Name: {mission_name}")
        label1.grid(row=0, column=0, padx=10, pady=2, sticky="nw")
        label2 = tk.Label(self.frame_mission, text=f"Mission Objective: {objective}")
        label2.grid(row=1, column=0, padx=10, pady=2, sticky="nw")
        label3 = tk.Label(
            self.frame_mission, text=f"Launched Location: {mission_location}"
        )
        label3.grid(row=2, column=0, padx=10, pady=2, sticky="nw")
        label4 = tk.Label(self.frame_mission, text=f"Launched Time: {start_time}")
        label4.grid(row=3, column=0, padx=10, pady=2, sticky="nw")

    def create_labels(self):
        self.elapsed_time = tk.Label(self.frame_mission)
        self.elapsed_time.grid(row=4, column=0, padx=10, pady=2, sticky="nw")

        self.label_launch_status = tk.Label(
            self.frame_launch_status,
            text="IDLE",
            bg="green",
            font=("Arial", 18, "bold"),
        )
        self.label_launch_status.grid(row=0, column=0, padx=20, pady=20, ipadx=20, ipady=20, sticky="nsew")

        self.battery_label = tk.Label(self.frame_telemetry, text="Battery Voltage: NA")
        self.battery_label.grid(row=0, column=0, padx=10, pady=2, sticky="nw")
        self.inttemp_label = tk.Label(self.frame_telemetry, text="System Temp: NA")
        self.inttemp_label.grid(row=1, column=0, padx=10, pady=2, sticky="nw")
        self.l1_label = tk.Label(self.frame_telemetry, text="Front Light: NA")
        self.l1_label.grid(row=2, column=0, padx=10, pady=2, sticky="nw")
        self.l2_label = tk.Label(self.frame_telemetry, text="Rear Light: NA")
        self.l2_label.grid(row=3, column=0, padx=10, pady=2, sticky="nw")

        self.temp_label = tk.Label(self.frame_sensordata1, text="Temperature: NA")
        self.temp_label.grid(row=0, column=0, padx=10, pady=2, sticky="nw")
        self.ph_label = tk.Label(self.frame_sensordata1, text="pH: NA")
        self.ph_label.grid(row=1, column=0, padx=10, pady=2, sticky="nw")
        self.pressure_label = tk.Label(self.frame_sensordata1, text="Pressure: NA")
        self.pressure_label.grid(row=2, column=0, padx=10, pady=2, sticky="nw")
        self.depth_label = tk.Label(self.frame_sensordata1, text="Depth: NA")
        self.depth_label.grid(row=3, column=0, padx=10, pady=2, sticky="nw")
        tk.Label(self.frame_sensordata1, text=" ").grid(row=4, column=0, padx=102, pady=0, sticky="nw")#for make space

        self.log_text = tk.Text(self.frame_consolelog, height=5, width=125)
        self.log_text.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.log_text.config(state=tk.DISABLED)

    def create_buttons(self):
        self.capture_button = tk.Button(
            self.frame_sensordata2,
            text="\nCapture\n\nDataset\n",
            command=self.take_snapshot,
            font=("Arial", 14, "bold"),
        )
        self.capture_button.grid(row=0, column=0, padx=0, pady=10, sticky="nsw")
        self.disarm_button = tk.Button(
            self.frame_terminate, text="Disarm Submarine", command=self.uav_disarm
        )
        self.disarm_button.grid(row=0, column=0, padx=20, pady=10)
        self.terminate_button = tk.Button(
            self.frame_terminate,
            text="Terminate Mission",
            command=self.terminatemission,
        )
        self.terminate_button.grid(row=1, column=0, padx=20, pady=10)

    def create_cams(self):
        self.webcam_label_1 = tk.Label(self.frame_front_webcam)
        self.webcam_label_1.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.webcam_label_2 = tk.Label(self.frame_rear_webcam)
        self.webcam_label_2.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")



    def is_raspberry_pi_online(self):
        try:
            subprocess.check_output(
                ["ping", "-c", "1", self.drone_ip], stderr=subprocess.STDOUT, text=True
            )
            self.sub_con_label.config(text=f"Submarine: Connected")
            return True
        except subprocess.CalledProcessError as e:
            error_output = e.output.lower()
            if "unknown host" in error_output or "unreachable" in error_output:
                self.add_to_log("Submarine: Hostname resolution error")
            self.sub_con_label.config(text=f"Submarine: Offline")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            self.sub_con_label.config(text=f"Submarine: Offline")
            self.add_to_log("Submarine: Offline")
            return False

    def joystick_status_update(self):
        if self.joystick_present:
            label = tk.Label(
                self.frame_connections, text="Joystick Controller: Connected"
            )
            label.grid(row=2, column=0, padx=10, pady=2, sticky="nw")
        else:
            label = tk.Label(
                self.frame_connections, text="Joystick Controller: Not Detected"
            )
            label.grid(row=2, column=0, padx=10, pady=2, sticky="nw")

    def uav_status(self):
        if self.current_uav_status:
            self.add_to_log("System initiating..")
            self.add_to_log("Control system initiated!")
            self.label_launch_status.config(text="ARMED", bg="red")
            self.add_to_log("Armed")
        else:
            self.label_launch_status.config(text="IDLE", bg="green")
            self.add_to_log("Disarmed")

    def uav_disarm(self):
        if self.current_uav_status == True:
            self.current_uav_status = False
            self.uav_status()
        else:
            self.add_to_log("Not Armed yet!")

    def terminatemission(self):
        print(terminate.terminate(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.current_uav_status = False
        self.kill_threads()
        self.client_socket.close()
        self.root.destroy()
        print("exitting")
        root1.deiconify()

    def kill_threads(self):
        self.threads_running = False

    def add_to_log(self, data):
        new_data = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {data}"
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, new_data + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)

    def update_elapsed_time(self):
        start_datetime = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        current_datetime = datetime.now()
        elapsed_time = current_datetime - start_datetime
        elapsed_time_str = str(elapsed_time).split(".")[0]
        self.elapsed_time.config(text=f"Elapsed Time: {elapsed_time_str}")
        self.elapsed_time.after(1000, self.update_elapsed_time)

    def update_sensor_frame(self, sensor_data):
        self.temp_label.config(text=f"Temperature: {sensor_data['temp']} °C")
        self.ph_label.config(text=f"pH: {sensor_data['ph']}pH")
        self.pressure_label.config(text=f"Pressure: {sensor_data['pressure']-17}mBar")
        self.depth_label.config(text=f"Depth: {(sensor_data['pressure']-1017)/100}m")

        self.battery_label.config(text=f"Battery Voltage: {sensor_data['battery']-1:.2f}V")
        self.inttemp_label.config(text=f"System Temp: {sensor_data['in_temp']} °C")



    def handle_joystick_inputs(self):
        if self.joystick_present:
            left_x = round(self.joystick.x, 3)
            left_y = round(self.joystick.y, 3)
            right_x = round(self.joystick.z, 3)
            right_y = round(self.joystick.rz, 3)
            button_l1 = self.joystick.buttons[0]
            button_l2 = self.joystick.buttons[2]
            button_left = self.joystick.buttons[4]
            button_right = self.joystick.buttons[5]

            # Arm / Disarm
            if button_left and button_right:
                time.sleep(0.4)
                if not self.current_uav_status and not self.is_raspberry_pi_online():
                    self.add_to_log("Cannot Arm: UAV offline")
                else:
                    self.current_uav_status = not self.current_uav_status
                    self.uav_status()  # Change Arm status

            # Take Data Snapshot
            if not button_left and button_right:
                self.take_snapshot()

            # send control data
            if self.current_uav_status:
                self.send_data_to_pi(
                    left_x, left_y, right_x, right_y, button_l1, button_l2
                )
            else:
                self.send_data_to_pi(
                    0.00, 0.00, 0.00, 0.00, False, False
                )

        self.root.after(
            100, self.handle_joystick_inputs
        )  # Update every 100 milliseconds

    def send_data_to_pi(self, left_x, left_y, right_x, right_y, button_l1, button_l2):
        if button_l1 == True:
            self.togglel1 = not self.togglel1
            time.sleep(0.3)
        if button_l2 == True:
            self.togglel2 = not self.togglel2
            time.sleep(0.3)

        if self.togglel1:
            self.l1_label.config(text=f"Front Light: ON")
        else:
            self.l1_label.config(text=f"Front Light: OFF")
        if self.togglel2:
            self.l2_label.config(text=f"Rear Light: ON")
        else:
            self.l2_label.config(text=f"Rear Light: OFF")


        joystick_data = {
            "left_x": left_x,
            "left_y": left_y,
            "right_x": right_x,
            "right_y": right_y,
            "button_l1": self.togglel1,
            "button_l2": self.togglel2,
        }

        try:
            send_message = json.dumps(joystick_data).encode("utf-8")
            self.client_socket.sendto(send_message, (drone_ip, drone_port))
        except Exception as e:
            print(f"Error sending control data: {e}")

    def fetch_sensor_data(self):
        while self.threads_running:
            try:
                sensor_data, _ = self.client_socket.recvfrom(1024)
                sensor_data = sensor_data.decode("utf-8")
                sensor_data = json.loads(sensor_data)
                self.sensor_dataset = sensor_data
                self.update_sensor_frame(sensor_data)
            except socket.timeout:
                print("Sensor data reciving timeout")
            except Exception as e:
                print(f"Error: {e}")

    def capture_and_send(self):
        self.add_to_log("Data capturing.")
        cap = cv2.VideoCapture(cap_cam_url)
        ret, frame = cap.read()
        self.add_to_log("Data preparing..")
        if ret:
            _, buffer = cv2.imencode(".jpg", frame)
            img_str = buffer.tobytes()
            temp = self.sensor_dataset["temp"]
            pressure = self.sensor_dataset["pressure"]
            ph = self.sensor_dataset["ph"]
            c_time = datetime.now()
            self.add_to_log("Data uploading...")
            response = dataupload.upload(temp, pressure, ph, c_time, img_str)

            if response == 200:
                self.add_to_log("Data uploaded to the cloud successfully.")
            else:
                self.add_to_log("Failed to upload data to the cloud.")

    def take_snapshot(self):
        with self.snapshot_lock:
            if self.snapshot_thread is None or not self.snapshot_thread.is_alive():
                self.snapshot_thread = threading.Thread(
                    target=self.capture_and_send
                )
                self.snapshot_thread.start()

    def start_video_threads(self):
        self.thread1 = threading.Thread(
            target=self.get_video_feed, args=(cam1_url, self.webcam_label_1, 900, 600)
        )
        self.thread1.daemon = True
        self.thread1.start()
        
        self.thread2 = threading.Thread(
            target=self.get_video_feed, args=(cam2_url, self.webcam_label_2, 400, 300)
        )
        self.thread2.daemon = True
        self.thread2.start()

    def fetch_sensor_data_thread(self):
        sensor_thread = threading.Thread(target=self.fetch_sensor_data)
        sensor_thread.daemon = True
        sensor_thread.start()

    def get_video_feed(self, cam_id, label, hx, wy):

        def update_label(img_tk):
            if self.threads_running:
                label.imgtk = img_tk
                label.configure(image=img_tk)
                label.image = img_tk
                label.update_idletasks()

        def cam_feed_error():
            err_image_path = "Controlpanel/src/video_error.jpg"
            err_image = Image.open(err_image_path)
            err_image = err_image.resize((hx, wy))
            img = ImageTk.PhotoImage(err_image)
            self.root.after(100, update_label, img)

        cap = cv2.VideoCapture(cam_id)

        if not cap.isOpened():
            self.add_to_log(f"Unable to open video feed {cam_id}")

        while self.threads_running:
            try:
                ret, frame = cap.read()
                if ret:
                    frame = cv2.resize(frame, (hx, wy))
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame)
                    img_tk = ImageTk.PhotoImage(image=img)

                    if not self.threads_running:
                        break

                    # Use the main thread to update the tkinter element
                    self.root.after(10, update_label, img_tk)

                else:
                    #cam_feed_error()  # show error image
                    cap.release()
                    self.add_to_log(
                        f"{cam_id} Stream ended prematurely. Attempting to reconnect..."
                    )
                    cap = cv2.VideoCapture(cam_id)  # trying to reconnect
                    continue

            except cv2.error as e:
                print(f"OpenCV error apooo: {e}")

            except Exception as e:
                if not self.threads_running:
                    break
                print(f"Cam id: {cam_id} Error occurred: {e}")
                break

        cap.release()


##############################

def centerscreen(window_width, window_height, window):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_position = int((screen_width - window_width) / 2)
    y_position = int((screen_height - window_height) / 2)
    window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

def start_main_app():
    root = tk.Toplevel()
    root.title("Aqua Bot")
    app = ControllDashboard(root)

def create_startup_gui():
    global root1
    root1 = tk.Tk()
    root1.title("Control Dashboard")
    centerscreen(600, 400, root1)
    label_title = tk.Label(root1, text="Control Dashboard", font=("Arial", 28))
    label_title.pack(pady=20)

    def create_mission(name, objective, location, window, miwindow):
        response = missioninitiate.initiate(
            name, objective, location, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        print(response)
        if response == 200:
            miwindow.destroy()
            window.iconify()
            check_data_availability()

    def input_form():
        mission_input_window = tk.Toplevel(root1)
        centerscreen(300, 300, mission_input_window)
        mission_input_window.title("Mission Input")
        # Create frames for better organization
        frame_name = tk.Frame(mission_input_window)
        frame_name.pack(pady=10)
        frame_objective = tk.Frame(mission_input_window)
        frame_objective.pack(pady=10)
        frame_location = tk.Frame(mission_input_window)
        frame_location.pack(pady=10)
        # Mission Name
        label_name = tk.Label(frame_name, text="Mission Name:")
        label_name.pack(anchor="w")
        entry_name = tk.Entry(frame_name)
        entry_name.pack(
            side=tk.RIGHT,
        )
        # Mission Objective
        label_objective = tk.Label(frame_objective, text="Mission Objective:")
        label_objective.pack(anchor="w")
        entry_objective = tk.Entry(frame_objective)
        entry_objective.pack(side=tk.RIGHT)
        # Location
        label_location = tk.Label(frame_location, text="Location:")
        label_location.pack(anchor="w")
        entry_location = tk.Entry(frame_location)
        entry_location.pack(side=tk.RIGHT)
        # Submit and Cancel buttons
        button_frame = tk.Frame(mission_input_window)
        button_frame.pack(pady=20)
        submit_button = tk.Button(
            button_frame,
            text="Submit",
            command=lambda: create_mission(
                entry_name.get(),
                entry_objective.get(),
                entry_location.get(),
                root1,
                mission_input_window,
            ),
        )
        submit_button.pack(side=tk.LEFT, padx=5)
        cancel_button = tk.Button(
            button_frame, text="Cancel", command=mission_input_window.destroy
        )
        cancel_button.pack(side=tk.LEFT, padx=5)

    def check_data_availability():
        json_data = missiondata.mission()
        end_time = json_data[0]["end_time"]
        print("Mission:", end_time)
        if end_time == "ONGOING":
            print("Opening Launch Window")
            start_main_app()
            root1.iconify()

    json_data = missiondata.mission()
    if json_data == "int-error":  # internet conn check
        print("int conn error..")
        int_error_title = tk.Label(
            root1,
            text="Please connect your device to Internet\nand restart the application to preceed!",
            font=("Arial", 16),
        )
        int_error_title.pack(pady=20)
    else:
        open_input_form_button = tk.Button(
            root1,
            text="Launch a Mission",
            font=("Arial", 16),
            width=20,
            height=2,
            command=input_form,
        )
        open_input_form_button.pack(pady=20)
        check_data_availability()
    # tk.Button(root1, text="Exit", font=('Arial', 16),width=20,height=2).pack(pady=20)

    root1.mainloop()

if __name__ == "__main__":
    create_startup_gui()
