
import time
import pigpio
import RPi.GPIO as GPIO
from gpiozero import AngularServo, Device
from gpiozero.pins.pigpio import PiGPIOFactory

# ----------------------
# Pins
# ----------------------
IN1, IN2, ENA = 16, 20, 12
SERVO_PIN = 2
TRIG = 26
ECHO_FRONT = 23
ECHO_BACK = 8
ECHO_LEFT = 25
ECHO_RIGHT = 24
S0, S1, S2, S3, OUT = 27, 22, 14, 15, 17
SWITCH_PIN = 19
LED_RED, LED_GREEN, LED_BLUE = 13, 6, 5 # LEDs

# ----------------------
# TUNING PARAMETERS - Adjust these!
# ----------------------
STEERING_GAIN = 2.0      # How aggressive the steering is (higher = sharper turns)
MAX_STEERING_ANGLE = 60  # Maximum steering angle limit
DEAD_ZONE = 5            # Ignore differences smaller than this (cm)
NORMAL_SPEED = 200       # Normal driving speed
CORNER_SPEED = 210       # Reduced speed at sharp corners
INNER_WALL_OFFSET = 0   # How much closer to inner wall (cm) - positive = favor inner wall
DIRECTION = "counterclockwise"  # Set to "clockwise" or "counterclockwise"

# ----------------------
# Setup
# ----------------------
pi = pigpio.pi()
if not pi.connected: raise RuntimeError("pigpio daemon not running")

GPIO.setmode(GPIO.BCM)
GPIO.setup(S0, GPIO.OUT)
GPIO.setup(S1, GPIO.OUT)
GPIO.setup(S2, GPIO.OUT)
GPIO.setup(S3, GPIO.OUT)
GPIO.setup(OUT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.output(S0, GPIO.HIGH)
GPIO.output(S1, GPIO.LOW)

for p in (IN1,IN2,ENA,TRIG): pi.set_mode(p, pigpio.OUTPUT)
for p in (ECHO_FRONT,ECHO_BACK,ECHO_LEFT,ECHO_RIGHT): pi.set_mode(p,pigpio.INPUT)
pi.set_PWM_frequency(ENA,2000)

GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


Device.pin_factory = PiGPIOFactory()
servo = AngularServo(SERVO_PIN,min_pulse_width=0.0006,max_pulse_width=0.0023)
servo.angle=0
# Switch + LEDs
GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_RED, GPIO.OUT)
GPIO.setup(LED_GREEN, GPIO.OUT)
GPIO.setup(LED_BLUE, GPIO.OUT)
GPIO.output(LED_RED, GPIO.LOW)
GPIO.output(LED_GREEN, GPIO.LOW)
GPIO.output(LED_BLUE, GPIO.LOW)
# ----------------------
# Motor functions
# ----------------------
def run_motor(value):
    forward = value>=0
    pi.write(IN1,1 if forward else 0)
    pi.write(IN2,0 if forward else 1)
    pi.set_PWM_dutycycle(ENA,min(255,abs(int(value))))

def stop_motor(brake=False):
    pi.set_PWM_dutycycle(ENA,0)
    pi.write(IN1,1 if brake else 0)
    pi.write(IN2,1 if brake else 0)

# ----------------------
# Ultrasonic
# ----------------------
def get_distance(trig, echo, max_distance_cm = 300):
    """
    Measure distance using HC-SR04 with proper timing.
    max_distance_cm controls timeout.
    """
    # Pre-pulse low
    pi.write(trig, 0)
    time.sleep(0.002)       # 2 ms low

    # 10 µs trigger pulse
    pi.write(trig, 1)
    time.sleep(10e-6)
    pi.write(trig, 0)

    # Calculate timeout based on max range
    timeout = (2 * max_distance_cm / 34300) + 0.02  # sec
    t0 = time.time()

    # Wait for echo high
    while pi.read(echo) == 0:
        if time.time() - t0 > timeout:
            return float('inf')
    start = time.time()

    # Wait for echo low
    while pi.read(echo) == 1:
        if time.time() - t0 > timeout:
            return float('inf')
    stop = time.time()

    # Convert pulse duration to distance (cm)
    return (stop - start) * 34300 / 2
# ----------------------
# Color sensor
# ----------------------
GPIO.output(S0,GPIO.HIGH); GPIO.output(S1,GPIO.LOW)
def count_pulses(pin,duration=0.12):
    count,start,last=0,time.time(),GPIO.input(pin)
    while time.time()-start<duration:
        current=GPIO.input(pin)
        if current==1 and last==0: count+=1
        last=current
    return count

def read_rgb():
    GPIO.output(S2,GPIO.LOW); GPIO.output(S3,GPIO.LOW); red=count_pulses(OUT)
    GPIO.output(S2,GPIO.LOW); GPIO.output(S3,GPIO.HIGH); blue=count_pulses(OUT)
    GPIO.output(S2,GPIO.HIGH); GPIO.output(S3,GPIO.HIGH); green=count_pulses(OUT)
    return red,green,blue

def detect_ground_color(r,g,b):
    r_f,g_f,b_f = r or 1,g or 1,b or 1
    if r_f>g_f*1.4 : return "orange"
    if b_f>r_f*1.3 : return "blue"
    return "unknown"



# ----------------------
# Safe distance cache + function
# ----------------------
last_distances = {"front": 50, "back": 50, "left": 30, "right": 30}

def safe_distance(name, trigger, echo, samples=3):
    """Return a filtered safe distance for a given sensor."""
    readings = []
    for _ in range(samples):
        d = get_distance(trigger, echo)
        if 2 <= d <= 100:   # Accept only realistic values (2cm–100cm)
            readings.append(d)
        time.sleep(0.01)

    if readings:
        dist = sorted(readings)[len(readings)//2]  # median
        last_distances[name] = dist
        return dist
    else:
        # fallback to last good reading
        return last_distances[name]


# ----------------------
# Proportional Steering Function
# ----------------------
def calculate_steering_angle(d_left, d_right, direction="unknown"):
    """
    Calculate steering angle proportional to the difference between left and right distances.
    
    For your servo: +angle = LEFT, -angle = RIGHT
    
    direction: "clockwise" or "counterclockwise" - determines which is the inner wall
    
    Returns angle between -MAX_STEERING_ANGLE and +MAX_STEERING_ANGLE
    """
    # Calculate the difference with offset for inner wall preference
    # If going counterclockwise: left wall is inner, so favor left (subtract offset from left distance)
    # If going clockwise: right wall is inner, so favor right (subtract offset from right distance)
    
        # Unknown direction - use centered steering
    difference = d_left - d_right
    
    # Apply dead zone - ignore small differences
    if abs(difference) < DEAD_ZONE:
        return 0
    
    # Calculate proportional steering angle
    angle = -difference * STEERING_GAIN
    
    # Clamp to maximum steering angle
    angle = max(-MAX_STEERING_ANGLE, min(MAX_STEERING_ANGLE, angle))
    
    return angle

# ----------------------
# Square course loop
# ----------------------
lap_count,color_bluepasses,color_orangepasses=0,0,0
last_bluecolor="unknown"
last_orangecolor="unknown"
print("Switch OFF - waiting")

while GPIO.input(SWITCH_PIN) == 1:
    time.sleep(0.1)

# Switch pressed → turn on blue LED
GPIO.output(LED_BLUE, GPIO.HIGH)
print("Switch ON - running")

try:
    while lap_count < 3:
        if GPIO.input(SWITCH_PIN) == 1:  
            stop_motor()
            servo.angle = 0
            GPIO.output(LED_BLUE, GPIO.LOW)
            time.sleep(0.05)
            continue
        else:
            GPIO.output(LED_BLUE, GPIO.HIGH)

        # safe distance readings
        d_front = get_distance(TRIG, ECHO_FRONT)
        time.sleep(0.1)   # let echoes fade

        d_left  = get_distance(TRIG, ECHO_LEFT) + 10
        time.sleep(0.1)

        d_right = get_distance(TRIG, ECHO_RIGHT) 
        time.sleep(0.1)


        # feedback print
        print(f"F:{d_front:.1f}cm L:{d_left:.1f}cm  R:{d_right:.1f}cm")

        # PROPORTIONAL centering logic - smooth steering based on wall distances
        steering_angle = calculate_steering_angle(d_left, d_right, DIRECTION)
        servo.angle = -steering_angle
        
        # Adjust motor speed based on steering angle - slow down at sharp corners
        if abs(servo.angle) >= 50:  # At sharp corners
            motor_speed = CORNER_SPEED
        else:
            motor_speed = NORMAL_SPEED        

        
        run_motor(motor_speed)
        
        # Optional: print steering for debugging
        if steering_angle != 0:
            print(f"  → Steering: {steering_angle:.1f}° (diff: {d_left-d_right:.1f}cm) Speed: {motor_speed}")

        # ----------------------
        # FAILSAFE: emergency wall avoidance
        # ----------------------
        if d_front < 20:  # too close!
            print("⚠️  Failsafe triggered: Wall too close")

            # Stop immediately
            stop_motor()
            time.sleep(0.1)

            # Decide turn direction
            if d_left > d_right:
                print("Turning LEFT while backing")
                servo.angle = -60
            else:
                print("Turning RIGHT while backing")
                servo.angle = 60

            # Reverse with steering angle
            run_motor(-210)
            time.sleep(1.5)   # back up for 2 seconds

            # Stop and straighten
            stop_motor()
            servo.angle = 0
            print("Failsafe complete, resuming path")
            continue  # skip rest of loop for this iteration



        # lap counting
        r, g, b = read_rgb()
        color = detect_ground_color(r, g, b)
        if color == "blue" and last_bluecolor != "blue":
            color_bluepasses += 1
            last_bluecolor = "blue"
            print(f"Lap marker crossed ({color_bluepasses}/4)")
        elif color != "blue":
            last_bluecolor = color
        
        if color == "orange" and last_orangecolor != "orange":
            color_orangepasses += 1
            last_orangecolor = "orange"
            print(f"Lap marker crossed ({color_orangepasses}/4)")
        elif color != "orange":
            last_orangecolor = color

        if color_bluepasses >= 4 or color_orangepasses >=4:
            lap_count += 1
            color_bluepasses = 0
            color_orangepasses = 0
            print(f"Lap {lap_count} complete")

        time.sleep(0.05)

    # finish
    print("All laps done, moving forward")
    run_motor(NORMAL_SPEED)
    time.sleep(2)
    stop_motor(brake=True)
    servo.angle = 0


except KeyboardInterrupt: stop_motor(brake=True); servo.angle=0
finally:
    stop_motor(brake=True)
    servo.angle = 0
    GPIO.output(LED_BLUE, GPIO.LOW)
    pi.stop()
   

