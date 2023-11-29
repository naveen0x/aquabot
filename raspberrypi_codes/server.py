import threading
import socket
import json
import serial

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('raspberrypi.local', 5555))
server_socket.settimeout(0.1)

arduino_control_port = '/dev/ttyUSB0'
arduino_sensor_port = '/dev/ttyUSB1'

def control():
    try:
        control_arduino = serial.Serial(arduino_control_port, 9600, timeout=0.5)

        while True:
            try:
                control_data, addr = server_socket.recvfrom(1024)  # Increased buffer size
                control_data = control_data.decode('utf-8')
                control_data = json.loads(control_data)
                left_x_value = control_data['left_x']
                left_y_value = control_data['left_y']
                right_x_value = control_data['right_x']
                right_y_value = control_data['right_y']
                button_l1_value = control_data['button_l1']
                button_l2_value = control_data['button_l2']
                data_to_send = f"{left_x_value},{left_y_value},{right_x_value},{right_y_value},{button_l1_value},{button_l2_value}\n"
                print(data_to_send)
                control_arduino.write(data_to_send.encode())
            except socket.timeout:
                pass
            except Exception as e:
                print(f"Control Socket Error: {e}")

    except serial.SerialException as e:
        print(f"Control Serial Error: {e}")
    except Exception as e:
        print(f"Control Unexpected Error: {e}")
    finally:
        if 'control_arduino' in locals():
            control_arduino.close()

def sensor():
    try:
        sensor_arduino = serial.Serial(arduino_sensor_port, 9600, timeout=0.5)

        while True:
            try:
                sensor_data, addr = server_socket.recvfrom(1024)  # Increased buffer size
                sensor_data = sensor_arduino.readline().decode('utf-8')
                if sensor_data:
                    sensor_data = json.loads(sensor_data)
                    print("Received Sensor Data:", sensor_data)
                    sensor_data = json.dumps(sensor_data).encode('utf-8')
                    server_socket.sendto(sensor_data, addr)

            except serial.SerialException as e:
                print(f"Sensor Serial Error: {e}")
            except Exception as e:
                print(f"Sensor Unexpected Serial Error: {e}")

    except serial.SerialException as e:
        print(f"Sensor Serial ports couldn't be opened: {e}")
    except Exception as e:
        print(f"Sensor Unexpected Error: {e}")
    finally:
        if 'sensor_arduino' in locals():
            sensor_arduino.close()

thread_1 = threading.Thread(target=control)
thread_2 = threading.Thread(target=sensor)
thread_1.daemon = False  # Set as non-daemon
thread_2.daemon = False  # Set as non-daemon
thread_1.start()
thread_2.start()

try:
    thread_1.join()
    thread_2.join()
except KeyboardInterrupt:
    server_socket.close()
