import network
import socket
import time
import machine
import math
import json
from picozero import pico_temp_sensor, pico_led

CONVERSION = 3.3 / (65535)
BETA = 3960  # Beta coefficient of thermistor (datasheet)
R0 = 1050  # Reference resistance (10kΩ) (datasheet)
T0 = 298.15 #written in kelvin (datasheet)

# reading analog input
potentiometer = machine.ADC(26)
thermo_resistor = machine.ADC(28)
ir_sensor = machine.ADC(27)

# formating GPIO connections
red_led = machine.Pin(15, machine.Pin.OUT)
green_led = machine.Pin(14, machine.Pin.OUT)


def read_temperature():
    # Read raw ADC value
    raw_temp = thermo_resistor.read_u16()

    # Convert ADC value to voltage by multiplying conversion factor
    voltage_temp = raw_temp * CONVERSION

    # Calculate thermistor resistance
    resistance_temp = R0 * ((3.3 / voltage_temp) - 1)

    # Ensures resistance is in proper range
    if resistance_temp <= 0:
        resistance_temp = 1e-6  

    # Calculate temperature in Kelvin
    temp_K = 1 / ((1 / T0) + (1 / BETA) * -math.log(resistance_temp / R0))
    temp_C = temp_K - 273.15 
    print("rawtemp", raw_temp)
    return round(temp_C, 3)
    
    #reads potentiometer and converts to 3.3V format
def read_potentiometer():
    raw_pot = potentiometer.read_u16()
    voltage_pot = raw_pot * CONVERSION
    return round(voltage_pot,3)
    
    #reads ir sensor and converts to 3.3V format
def read_ir():
    raw_ir = ir_sensor.read_u16()
    voltage_ir = raw_ir * CONVERSION
    return round(voltage_ir, 3)

#testing
# while True:
    
#     print("temp")
#     print(read_temperature())
#     print("potentiometer")
#     print(read_potentiometer())
#     print("ir")
#     print(read_ir())
#     
#     time.sleep(.1)

# while True:
#     temp_C = read_temperature()
#     poten = read_potentiometer()
#     
#     if temp_C < (16+3*poten) && temp_C > (14+3*poten):
#         


# Create an Access Point
ssid = 'Group8PICO'  # access point name.
password = '12345678'  # password

ap = network.WLAN(network.AP_IF)
ap.config(essid=ssid, password=password)
ap.active(True)  # Activate the access point

while ap.active() == False:
    pass
print('Connection is successful')
print(ap.ifconfig())  # This line will print the IP address of the Pico board

# Create a socket server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)  # maximum number of requests that can be queued

def web_page():
    html = """<!DOCTYPE html>
<html lang="en">
   <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>AmbuLogger</title>
      <style>
         body {
         .flex-container {
         display: flex;
         flex-direction: row;
         font-size: 30px;
         text-align: center;
         }
         .flex-item-left {
         background-color: #f1f1f1;
         padding: 10px;
         flex: 50%;
         }
         .flex-item-right {
         background-color: #D3D3D3;
         padding: 10px;
         flex: 50%;
         }
         @media (max-width: 950px) {
         .flex-container {
         flex-direction: column;
         }
         }
         font-family: Helvetica;
         display: flex;
         flex-direction: column;
         justify-content: center;
         align-items: center;
         margin: 0;
         padding: 0;
         font-size: 16px;
         }
         h1  {
         text-align: center;
         font-size: 40px;
         font-family: Helvetica, sans-serif;
         color: white;
         }
         h2  {
         text-align: center;
         font-size: 15px;
         color: #00008B;
         font-family: Helvetica, sans-serif;
         color: gray;
         }
         .container {
         display: flex;
         flex-direction: column;
         align-items: center;
         padding: 20px;
         width: 100%;
         }
         .distance-container {
         text-align: left;
         margin-bottom: 20px;
         display: flex;
         gap: 11px;
         }
         .button-container {
         width: 500px;
         height: 50px;
         margin-top: 10px;
         align-items: center;
         display: flex;
         justify-content: center;
         font-weight: bold;
         color: white;
         border-radius: 5px;
         }
         .temperature-container {
         text-align: center;
         }
         label {
         font-size: 16px;
         font-weight: bold;
         display: block;
         margin-bottom: 10px;
         }
         input {
         padding: 10px;
         font-size: 18px;
         width: 150px;
         text-align: center;
         margin-bottom: 10px;
         border: 2px solid black;
         border-radius: 10px;
         height: 30px;
         }
         button {
         padding: 10px 20px;
         font-size: 18px;
         cursor: pointer;
         margin: 5px;
         width: 265px;
         font-family: Helvetica, sans-serif;
         border: 2px solid black;
         border-radius: 20px;
         background-color: #9ca0b5;
         height: 50px;
         }
         #estimatedTime {
         font-size: 18px;
         font-weight: bold;
         margin-left: 10px;
         color: blue;
         }
         #timer {
         font-size: 24px;
         font-weight: bold;
         margin-top: 20px;
         font-family: Helvetica, sans-serif;
         }
         #emergency {
         display: none;
         background-color: orange;
         color: white;
         font-size: 20px;
         font-weight: bold;
         padding: 10px;
         border-radius: 5px;
         position: absolute;
         right: 50px;
         top: 100px;
         }
         meter {
         width: 500px;
         height: 30px;
         }
         #colorBox {
         width: 500px;
         height: 50px;
         border: 2px solid black;
         margin-top: 10px;
         align-items: center;
         display: flex;
         justify-content: center;
         font-weight: bold;
         color: white;
         border-radius: 10px;
         font-size: 16px;
         }
         #colorBox2 {
         width: 160px;
         height: 50px;
         border: 2px solid black;
         display: flex;
         align-items: center;
         justify-content: center;
         font-weight: bold;
         color: white;
         font-size: 16px;
         border-radius: 10px;
         }
         #colorBox3 {
         width: 325px;
         height: 50px;
         border: 2px solid black;
         display: flex;
         align-items: center;
         justify-content: center;
         font-weight: bold;
         color: white;
         border-radius: 10px;
         font-size: 16px;
         }
         #mainBox {
         display: flex;
         gap: 11px;
         flex-wrap: wrap;
         justify-content: center;
         align-content: center;
         width: 600px;
         position: relative;
         }
         #tempValueContainer {
         width: 200px;
         height: 100px;
         display: flex;
         align-items: center;
         justify-content: center;
         font-weight: bold;
         color: black;
         font-size: 90px;
         position: relative;
         border-radius: 10px;
         }
         #timer {
         width: 500px;
         height: 50px;
         display: flex;
         align-items: center;
         justify-content: center;
         font-weight: bold;
         color: black;
         font-size: 65px;
         border-radius: 10px;
         }
         #intendedTempBox {
         width: 500px;
         height: 50px;
         border: 2px solid black;
         margin-top: 4px;
         align-items: center;
         display: flex;
         justify-content: center;
         font-weight: bold;
         color: white;
         border-radius: 10px;
         font-size: 16px;
         }
         #estimateDisplay {
         width: 300px;
         height: 50px;
         border: 2px solid black;
         display: flex;
         align-items: center;
         justify-content: center;
         font-weight: bold;
         color: white;
         border-radius: 10px;
         background-color: #D3D3D3;
         }
         #startTimeDisplay{
         font-size: 20px;
         }
         #stopTimeDisplay{
         font-size: 20px;
         }
      </style>
   </head>
   <body>
      <div class="container" style="background-color:#1E3A4C;">
         <h1>AmbuLogger</h1>
         <h2>HGR Smart Systems</h2>
      </div>
      <div class="flex-container">
         <div class="flex-item-left">
            <div id = "mainBox">
               <div class="button-container">
                  <button id="startButton" onclick="startTimer()" disabled>Start</button>
                  <button id="stopButton" onclick="stopTimer()">Stop</button>
               </div>
               <div class="distance-container">
                  <input type="number" id="distance" placeholder="Enter distance" oninput="calculateTime()">
                  <div id=estimateDisplay>
                     <span id="estimatedTime"></span>
                  </div>
               </div>
               <div id="timer">Time: 00:00</div>
               <div id="startTimeDisplay"></div>
               <div id="stopTimeDisplay"></div>
            </div>
            <div id="emergency">🚨 EMERGENCY: Travel Time Exceeded! 🚨</div>
         </div>
         <div class="flex-item-right">
            <div id = "mainBox">
               <div id = "tempValueContainer"> 22.275</div>
               <div class="temperature-container">
                  <meter id="Temperature" value="0" min="10" max="35"></meter>
                  <div id="colorBox" ></div>
               </div>
               <div id="intendedTempBox"> </div>
               <div class="gate-container">
                  <div id="colorBox2"></div>
               </div>
               <div class="gate-count-container">
                  <div id="colorBox3"></div>
               </div>
               
               <form action="./lighton">
                    <button type="submit"> Toggle light mode</button>
               </form>
            </div>
         </div>
      </div>
      </div>
      <script>
         let sensorData = {}
         
         function fetchSensorData() {
             fetch('/sensor')
             .then(response => response.json())
             .then(data => {
                 let temperature = data.temperature;
                 let potentiometer = data.potentiometer;
                 let irSensor = data.irSensor;
         
                 document.getElementById("Temperature").value = temperature;
         
                 updateTempBox(temperature, potentiometer);
                 updateGateStatus(irSensor);
                 updateTempValue(temperature);
                 updateIntendedTemp(potentiometer);
                 updateGateCount(irSensor);
             })
             .catch(error => console.error("Fetch error:", error));
         }
         
         setInterval(fetchSensorData, 250);
         
         function updateGateStatus(value) {
             let colorBox2 = document.getElementById("colorBox2");
             let colorBox3 = document.getElementById("colorBox3");
             colorBox2.style.background = "gray";
             if (value > 2.9) {
                 colorBox2.style.background = "red";
                 colorBox2.textContent = "Gate Open";
             } else {
         
                 colorBox2.style.background = "green";
                 colorBox2.textContent = "Gate Closed";
             }
         }
         
         
         function updateTempBox(value, value2) {
             let colorBox = document.getElementById("colorBox");
             if (value < (16+3*value2) && value > (14+3*value2)) {
                 colorBox.style.backgroundColor = "green";  
                 colorBox.textContent = "Temperature within range [±1°C]";
                 } else {
                 colorBox.style.backgroundColor = "red";
                 colorBox.textContent = "Temperature OUT OF RANGE [±1°C]";
                 }
         
         }
         
         function updateTempValue(value) {
             let box = document.getElementById("tempValueContainer");
             box.textContent = value + "°C";
         
         }
         
         
         
         function updateIntendedTemp(value) {
         
         let box = document.getElementById("intendedTempBox");
         box.style.backgroundColor = "gray";
         box.textContent = "Target Temperature set to: "+ (15 + 3 * value).toFixed(2);
         }
         
         let count = 0;
         let previousState = false; // Stores the previous reading
         
         function updateGateCount(value) {
         let box = document.getElementById("colorBox3");
         
         let currentState = value > 2.9; //the expression evaluates to 1 if the gate is open
         
         if (currentState && !previousState) {
             count += 1; // only changes the count if detects a change from previous reading
         }
         
         previousState = currentState;
         
         box.style.backgroundColor = currentState ? "green" : "gray";
         box.textContent = "Times gate has opened: " + count;
         }
         
         let estimatedSeconds = 0;
         let timer;
         let startTime;
         let elapsedTime = 0;
         
         function calculateTime() {
         let distance = parseFloat(document.getElementById("distance").value);
         let estimatedTimeDisplay = document.getElementById("estimatedTime");
         let startButton = document.getElementById("startButton");
         
         if (isNaN(distance) || distance <= 0) {
             estimatedTimeDisplay.textContent = "";
             startButton.disabled = true;
             return;
         }
         
         if (distance <= 0.2) estimatedSeconds = 30;
         else if (distance <= 1) estimatedSeconds = 120;
         else if (distance <= 5) estimatedSeconds = 600;
         else if (distance <= 10) estimatedSeconds = 1200;
         else if (distance <= 20) estimatedSeconds = 1800;
         else if (distance <= 30) estimatedSeconds = 3000;
         else estimatedSeconds = 7200;
         
         let minutes = Math.floor(estimatedSeconds / 60);
         let seconds = estimatedSeconds % 60;
         estimatedTimeDisplay.textContent = `Estimated Time: ${minutes} min ${seconds} sec`;
         
         startButton.disabled = false;
         
         // Save to localStorage
         localStorage.setItem("distance", distance);
         localStorage.setItem("estimatedSeconds", estimatedSeconds);
         localStorage.setItem("estimatedTimeDisplay", estimatedTimeDisplay.textContent);
         }
         
         function startTimer() {
         // Hide emergency message initially
         document.getElementById("emergency").style.display = "none";
         
         startTime = Date.now();
         localStorage.setItem("startTime", startTime);
         
         // Display start time
         let startTimeDisplay = document.getElementById("startTimeDisplay");
         let now = new Date();
         startTimeDisplay.textContent = `Start Time: ${now.toLocaleString()}`;
         
         timer = setInterval(updateTimer, 1000);
         }
         
         function stopTimer() {
         clearInterval(timer);
         
         // Display stop time
         let stopTimeDisplay = document.getElementById("stopTimeDisplay");
         let now = new Date();
         stopTimeDisplay.textContent = `Stop Time: ${now.toLocaleString()}`;
         
         localStorage.removeItem("startTime"); // Reset start time on stop
         localStorage.setItem("elapsedTime", elapsedTime);
         }
         
         function updateTimer() {
         let currentTime = Date.now();
         elapsedTime = Math.floor((currentTime - startTime) / 1000);
         let remainingTime = estimatedSeconds - elapsedTime;
         
         if (remainingTime <= 0) {
             remainingTime = 0;
             document.getElementById("emergency").style.display = "block"; // Show emergency message
             clearInterval(timer);
         }
         
         let minutes = Math.floor(remainingTime / 60);
         let seconds = remainingTime % 60;
         document.getElementById("timer").textContent = `Time: ${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
         
         // Save elapsed time
         localStorage.setItem("elapsedTime", elapsedTime);
         }
         
         function loadPreviousData() {
         if (localStorage.getItem("distance")) {
             document.getElementById("distance").value = localStorage.getItem("distance");
             document.getElementById("estimatedTime").textContent = localStorage.getItem("estimatedTimeDisplay");
             estimatedSeconds = parseInt(localStorage.getItem("estimatedSeconds"));
             document.getElementById("startButton").disabled = false;
         }
         
         if (localStorage.getItem("startTime")) {
             startTime = parseInt(localStorage.getItem("startTime"));
             let currentTime = Date.now();
             elapsedTime = Math.floor((currentTime - startTime) / 1000);
         
             // Update timer display
             let remainingTime = estimatedSeconds - elapsedTime;
             if (remainingTime <= 0) {
                 remainingTime = 0;
                 document.getElementById("emergency").style.display = "block"; // Show emergency message
             }
         
             let minutes = Math.floor(remainingTime / 60);
             let seconds = remainingTime % 60;
             document.getElementById("timer").textContent = `Time: ${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
         
             // Restart the timer only if the timer was running before the refresh
             if (remainingTime > 0) {
                 timer = setInterval(updateTimer, 1000);
             }
         }
         }
         
         // Load saved data when page refreshes
         window.onload = loadPreviousData;
         
         
         
      </script>
   </body>
</html>"""
    return html

counter = 1

while True:

    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024).decode()
    

            
       #determine of light state toggle is enabled     
    led_on = request.find('lighton')
    print(led_on)

        #sends data to webpage
    if "/sensor" in request:
        sensor_data = {
            "temperature": read_temperature(),
            "potentiometer": read_potentiometer(),
            "irSensor": read_ir()
        }
        response = "HTTP/1.1 200 OK\nContent-Type: application/json\n\n" + json.dumps(sensor_data)
        conn.sendall(response.encode())  # Send the JSON response
    else:
        response = web_page()  # Serve HTML page
        conn.send("HTTP/1.1 200 OK\n")
        conn.send("Content-Type: text/html\n")
        conn.send("Connection: close\n\n")
        conn.sendall(response.encode())  # Ensure encoding
        
        
        #Determine LED state every quarter second
    temp_C = read_temperature()
    poten = read_potentiometer()
    ir = read_ir()
    
    
        #Tests if the light functions are enabled from the toggle button in code
    if led_on == 5:
        counter *= -1
        
        #Determines if the program should test the LED state
    print(counter)
    if counter > 0:
        print("testing")
        
        if temp_C < (16+3*poten) and temp_C > (14+3*poten):
            green_led.value(1)
        else:
            green_led.value(0)
        
        if ir > 2.9:

            red_led.value(1)
        else:
            red_led.value(0)
        time.sleep(0.25)
    else:
        green_led.value(0)
        red_led.value(0)
        
        
    conn.close()
