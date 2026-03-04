import serial
import csv
import matplotlib.pyplot as plt
import time

# configuration
PORT = "COM3"        
BAUD_RATE = 9600
OUTPUT_FILE = "sensor_data.csv" 
MAX_READINGS = 200

def collect_data():
    readings = []
    
    #check if connected
    print(f"Connecting to {PORT}...")
    with serial.Serial(PORT, BAUD_RATE, timeout=10) as ser:
        time.sleep(2)  # Wait for Arduino to reset
        ser.reset_input_buffer()
        
        #check if data is being collected
        print("Collecting data...")
        
        #set the while loop to organize readings in csv style
        while len(readings) < MAX_READINGS:
            line = ser.readline().decode("utf-8").strip()
            
            if not line or line.startswith("index"):  # Skip header
                continue
            
            parts = line.split(",")
            if len(parts) == 3:
                try:
                    index = int(parts[0])
                    temp  = float(parts[1])
                    hum   = float(parts[2])
                    readings.append((index, temp, hum))
                    print(f"  [{index}/200] Temp: {temp}°C  Humidity: {hum}%")
                except ValueError:
                    print(f"  Skipping bad line: {line}")
    
    return readings

#save data in csv file
def save_csv(readings):
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["index", "temperature", "humidity"])
        writer.writerows(readings)
    print(f"\nData saved to '{OUTPUT_FILE}'")

#plots
def plot_data(readings):
    indices     = [r[0] for r in readings]
    temperatures = [r[1] for r in readings]
    humidities   = [r[2] for r in readings]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    fig.suptitle("DHT11 Sensor — 200 Readings", fontsize=14, fontweight="bold")

    ax1.plot(indices, temperatures, color="tomato", linewidth=1.5, label="Temperature")
    ax1.set_ylabel("Temperature (°C)")
    ax1.set_ylim(min(temperatures) - 1, max(temperatures) + 1)
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.plot(indices, humidities, color="steelblue", linewidth=1.5, label="Humidity")
    ax2.set_ylabel("Humidity (%)")
    ax2.set_xlabel("Reading #")
    ax2.set_ylim(min(humidities) - 1, max(humidities) + 1)
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("sensor_plot.png", dpi=150)
    plt.show()
    print("Plot saved to 'sensor_plot.png'")

#set the guard
if __name__ == "__main__":
    readings = collect_data()
    save_csv(readings) 
    plot_data(readings)