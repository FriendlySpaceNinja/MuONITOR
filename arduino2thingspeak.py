import serial
import requests
import json
import time

ser1 = serial.Serial('/dev/tty.usbserial-14110', 9600)
ser2 = serial.Serial('/dev/tty.usbserial-14120', 9600)
ser3 = serial.Serial('/dev/tty.usbserial-14130', 9600)
ser4 = serial.Serial('/dev/tty.usbserial-14140', 9600)

# ThingSpeak API settings
channel_id = "###"
write_api_key = "###"
thingspeak_url = f"https://api.thingspeak.com/update?api_key={write_api_key}"

def read_from_serial(ser):
    try:
        if ser.in_waiting > 0:
            json_data = ser.readline().decode('utf-8').strip()
            print(f"Read JSON data: {json_data}")
            data = json.loads(json_data)
            return data
    except Exception as e:
        print(f"Error reading from serial: {e}")
    return None

def send_to_thingspeak(total_count, uptime, hit_rate):
    try:
        response = requests.get(thingspeak_url + f"&field1={total_count}&field2={uptime}&field3={hit_rate}")
        if response.status_code == 200:
            print(f"Successfully sent data to ThingSpeak: {total_count}, {uptime}, {hit_rate}")
        else:
            print(f"Failed to send data to ThingSpeak: {response.status_code}")
    except Exception as e:
        print(f"Error sending data to ThingSpeak: {e}")

while True:
    total_count = 0
    uptimes = []
    hit_rates = []

    for ser in [ser1, ser2, ser3, ser4]:
        data = read_from_serial(ser)
        if data:
            try:
                total_count += int(data["count"])
                uptimes.append(data["uptime"])
                hit_rates.append(float(data["hit_rate"]))
            except (json.JSONDecodeError, KeyError):
                print(f"Invalid JSON data: {data}")

    if uptimes and hit_rates:
       #Sending the first uptime and the average hit rate
        uptime = uptimes[0]
        avg_hit_rate = sum(hit_rates) / len(hit_rates)

        if int(time.time()) % 15 == 0:  # Send data every 15 seconds, might need too delete that line
            send_to_thingspeak(total_count, uptime, avg_hit_rate)
            time.sleep(1)  # Ensure there's a small delay to avoid rapid multiple sends

    time.sleep(1)  # Read data every second
