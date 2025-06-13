from SimplyRobotics import KitronikSimplyRobotics
import network
import socket
import utime
import _thread

board = KitronikSimplyRobotics()
running = False

# WiFi credentials
SSID = ''
PASSWORD = ''

# Connect to WiFi with timeout and retries
def connect_wifi(ssid, password, timeout=99):
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    if sta_if.isconnected():
        print("Already connected:", sta_if.ifconfig())
        return sta_if
    print(f"Connecting to WiFi '{ssid}'...")
    sta_if.connect(ssid, password)
    start = utime.time()
    while not sta_if.isconnected():
        if utime.time() - start > timeout:
            print("Failed to connect to WiFi within timeout")
            return None
        utime.sleep(1)
    print("Connected to WiFi:", sta_if.ifconfig())
    return sta_if

sta_if = connect_wifi(SSID, PASSWORD)
if not sta_if:
    raise RuntimeError("WiFi connection failed. Check your credentials and try again.")

# HTML page with viewport meta for mobile responsiveness
html = """\
HTTP/1.0 200 OK

<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Servo Control</title>
</head>
<body>
    <h1>Servo Sweep Control</h1>
    <form action="/toggle" method="get">
        <button type="submit">{}</button>
    </form>
    <p>IP: {}</p>
</body>
</html>
"""

def servo_sweep():
    global running
    while True:
        if running:
            print("Servo sweep running...")
            # Sweep up
            for degrees in range(180):
                if not running:
                    break
                for servo in range(8):
                    board.servos[servo].goToPosition(degrees)
                utime.sleep_ms(10)
            # Sweep down
            for degrees in range(180):
                if not running:
                    break
                for servo in range(8):
                    board.servos[servo].goToPosition(180 - degrees)
                utime.sleep_ms(10)
        else:
            utime.sleep_ms(100)

def web_server():
    global running
    s = socket.socket()
    s.bind(('0.0.0.0', 8080))  # Using port 8080 to avoid conflicts
    s.listen(1)
    print("Web server running at http://{}:8080".format(sta_if.ifconfig()[0]))

    while True:
        cl, addr = s.accept()
        print('Client connected from', addr)
        cl_file = cl.makefile('rwb', 0)
        request_line = cl_file.readline()
        if not request_line:
            cl.close()
            continue

        # Read and discard HTTP headers
        while True:
            header = cl_file.readline()
            if header == b'' or header == b'\r\n':
                break

        try:
            path = request_line.decode().split(' ')[1]
            path = path.split('?')[0]
        except Exception:
            path = '/'

        if path == '/toggle':
            running = not running
            print("Servo running:", running)

        button_text = "Stop Sweep" if running else "Start Sweep"
        response = html.format(button_text, sta_if.ifconfig()[0])
        cl.send(response.encode())
        cl.close()

# Start servo sweep in a background thread
_thread.start_new_thread(servo_sweep, ())

# Run web server on the main thread
web_server()

