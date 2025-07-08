# This is the initial code
# full_rpi_self_driving_car.py

import cv2
import time
import pigpio
import RPi.GPIO as GPIO

# -------------------------------
# Motor and Steering Definitions
# -------------------------------
# Motor Driver Pins (L298N or similar)
LEFT_EN = 18       # Enable pin (PWM)
LEFT_IN1 = 23      # Motor input 1
LEFT_IN2 = 24      # Motor input 2

# Servo for Steering
STEERING_SERVO = 12  # PWM pin (GPIO12 - PWM0)

# Start Button
START_BTN = 17

# -------------------------------
# GPIO Setup
# -------------------------------
GPIO.setmode(GPIO.BCM)
GPIO.setup(LEFT_IN1, GPIO.OUT)
GPIO.setup(LEFT_IN2, GPIO.OUT)
GPIO.setup(LEFT_EN, GPIO.OUT)
GPIO.setup(START_BTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Motor PWM setup
motor_pwm = GPIO.PWM(LEFT_EN, 1000)  # 1kHz frequency
motor_pwm.start(0)

# pigpio for Servo
pi = pigpio.pi()
pi.set_mode(STEERING_SERVO, pigpio.OUTPUT)

# -------------------------------
# Functions
# -------------------------------

def set_motor(forward=True, speed=50):
    GPIO.output(LEFT_IN1, GPIO.HIGH if forward else GPIO.LOW)
    GPIO.output(LEFT_IN2, GPIO.LOW if forward else GPIO.HIGH)
    motor_pwm.ChangeDutyCycle(speed)

def set_steering(angle):
    # Convert angle (0-180) to pulse width (1000-2000us)
    pulsewidth = int(1000 + (angle / 180) * 1000)
    pi.set_servo_pulsewidth(STEERING_SERVO, pulsewidth)

def wait_for_start():
    print("Waiting for start button press...")
    while GPIO.input(START_BTN) == GPIO.HIGH:
        time.sleep(0.1)
    print("Start signal received!")

def get_steering_angle(frame):
    # Placeholder for computer vision algorithm
    # Replace this with OpenCV-based lane detection
    return 90  # Straight ahead

# -------------------------------
# Main Execution Loop
# -------------------------------
def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera initialization failed.")
        return

    try:
        wait_for_start()
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            angle = get_steering_angle(frame)
            set_steering(angle)
            set_motor(forward=True, speed=60)

            # Debug display
            cv2.imshow("Camera View", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Interrupted by user.")

    finally:
        cap.release()
        pi.set_servo_pulsewidth(STEERING_SERVO, 0)
        pi.stop()
        motor_pwm.stop()
        GPIO.cleanup()
        cv2.destroyAllWindows()
        print("Cleanup completed.")

# -------------------------------
# Entry Point
# -------------------------------
if __name__ == "__main__":
    main()
