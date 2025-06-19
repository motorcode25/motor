from bluetooth import BLE
from time import sleep_ms
from KitronikPicoWBluetooth import BLEPeripheral
from machine import Pin
from SimplyRobotics import KitronikSimplyRobotics
import utime

board = KitronikSimplyRobotics()
led = Pin("LED", Pin.OUT)

speed = 50  # (unused here, but you can add speed controls for servos if needed)

# Setup Bluetooth peripheral
peripheral = BLEPeripheral(BLE())

# Wait for connection
while not peripheral.isConnected():
    sleep_ms(100)
    led(1)
    sleep_ms(100)
    led(0)
    sleep_ms(100)

# Set LED on steady to show connected
led(1)

received = None

def writeCallback(value):
    global received
    received = bytes(value)

peripheral.writeCallback = writeCallback

def readCallback():
    peripheral.readCallback = None
    return "START"

peripheral.readCallback = readCallback

while peripheral.readCallback is not None:
    sleep_ms(50)

# Servo sweep globals
sweep_pos = 0
sweep_dir = 1
running_sweep = False

def servo_sweep_step():
    global sweep_pos, sweep_dir
    for servo in range(8):
        board.servos[servo].goToPosition(sweep_pos)
    sweep_pos += sweep_dir
    if sweep_pos >= 180 or sweep_pos <= 0:
        sweep_dir *= -1

while peripheral.isConnected():
    if received is not None:
        command = received[0]
        received = None

        if command == 1:  # START servo sweep
            running_sweep = True
        elif command == 0:  # STOP servo sweep
            running_sweep = False

    if running_sweep:
        servo_sweep_step()

    sleep_ms(10)

# Cleanup when disconnected
for servo in range(8):
    board.servos[servo].goToPosition(90)  # Return servos to neutral position

led(0)

