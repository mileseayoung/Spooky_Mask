import time
import digitalio
import board
import busio
import adafruit_vl53l1x
import pwmio
from adafruit_motor import servo

        
def average(list):
    listsum = 0
    for i in list:
        listsum += i
    average = listsum/len(list)
    
    return average

def slope(list,interval):
    #find local slope
    try:
        slope = (list[99] - list[98])/(interval)
        return slope
    except:
        return 0


def glow(led, interval, min_dc = 0, max_dc = 200, step = 5):
    # Function to glow an LED firefly at a predefined frequency
    led.duty_cycle = min_dc
    curr_time = prev_time = time.monotonic()
    fade = False
    while True:
        curr_time = time.monotonic()
        diff_time = curr_time - prev_time
        if diff_time > interval:
            #print(led.duty_cycle)
            #print(fade)
            if led.duty_cycle in range(min_dc-1,max_dc+1) and fade == False:
                if led.duty_cycle >= max_dc:
                    fade = True
                else:
                    led.duty_cycle += step
            elif led.duty_cycle in range (min_dc-1,max_dc+1) and fade == True:
                if led.duty_cycle <= min_dc:
                    fade = False
                else:
                    led.duty_cycle += -step
            prev_time = time.monotonic()
            
        yield led.duty_cycle
        
def wiggle(servo, interval, min_dc = 0, max_dc = 180, step = 5):
    # Function to wiggle jaw so it "laughs" at a predefined frequency
    servo.angle = min_dc
    curr_time = prev_time = time.monotonic()
    fade = False
    while True:
        curr_time = time.monotonic()
        diff_time = curr_time - prev_time
        if diff_time > interval:
            print(servo.angle)
            print(fade)
            if int(servo.angle) in range(min_dc-step,max_dc+step) and fade == False:
                #print('debug')
                if int(servo.angle) >= max_dc-1:
                    fade = True
                else:
                    servo.angle += step
            elif int(servo.angle) in range (min_dc-step,max_dc+step) and fade == True:
                #print('debug')
                if int(servo.angle) <= min_dc+1:
                    fade = False
                else:
                    servo.angle += -step
            else:
                print('debug')
                pass
            prev_time = time.monotonic()    
            
        yield servo.angle        

# Initialize I2C communication object
i2c = busio.I2C(board.GP27,board.GP26)

# Initialize vl53l1x distance sensor object
vl53 = adafruit_vl53l1x.VL53L1X(i2c)
# Start sensor in LONG distance mode
vl53.distance_mode = 1
vl53.timing_budget = 50
# Start distance sensor ranging
vl53.start_ranging()

# Define status LED for debugging
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
# Turn on LED to signal code is running
led.value = True

# Define firefly-led control pin
firefly1_pwm = pwmio.PWMOut(board.GP11,frequency = 5000)
firefly1 = glow(firefly1_pwm,0.05)
firefly2_pwm = pwmio.PWMOut(board.GP12,frequency = 5000)
firefly2 = glow(firefly2_pwm,0.08)
firefly3_pwm = pwmio.PWMOut(board.GP13,frequency = 5000)
firefly3 = glow(firefly3_pwm,0.04)
firefly4_pwm = pwmio.PWMOut(board.GP14,frequency = 5000)
firefly4 = glow(firefly4_pwm,0.06)
firefly5_pwm = pwmio.PWMOut(board.GP15,frequency = 5000)
firefly5 = glow(firefly5_pwm,0.07)
fireflies = [firefly1, firefly2, firefly3, firefly4, firefly5]

# Define eye-led control pins
left_eye = digitalio.DigitalInOut(board.GP5)
left_eye.direction = digitalio.Direction.OUTPUT
right_eye = digitalio.DigitalInOut(board.GP4)
right_eye.direction = digitalio.Direction.OUTPUT
left_eye.value = True
time.sleep(1)
left_eye.value = False
right_eye.value = True
time.sleep(1)
right_eye.value = False
print('Eyes tested')

# Define digital output pin to control servo for jaw
jaw_servo_pwm = pwmio.PWMOut(board.GP2, duty_cycle=2**15, frequency = 50)
jaw_servo = servo.Servo(jaw_servo_pwm, min_pulse = 1000, max_pulse = 2000)
#jaw_wiggle = wiggle(jaw_servo,0.01, min_dc = 145, max_dc = 165)
# Define digital output pin to control servo for left eye
right_eye_servo_pwm = pwmio.PWMOut(board.GP1, duty_cycle=2**15, frequency = 50)
right_eye_servo = servo.Servo(right_eye_servo_pwm, min_pulse=1000, max_pulse=2150)
#right_eye_wiggle = wiggle(right_eye_servo, 0.1, min_dc = 130, max_dc = 180)
#while True:
    #next(right_eye_wiggle)
# Define digital output pin to control servo for right eye
left_eye_servo_pwm = pwmio.PWMOut(board.GP0, duty_cycle=2**15, frequency = 50)
left_eye_servo = servo.Servo(left_eye_servo_pwm, min_pulse=1000, max_pulse=2050)


time.sleep(1)
# Set initial value for distance
#dist = 0
##_________NOTE________________
## Jaw and right eye servo "closed" position is 180 deg, left eye servo closed position is 0 deg
jaw_servo.angle = 160
right_eye_servo.angle = 180
left_eye_servo.angle = 0
#groupSet(180,servo1,servo2)

time.sleep(1)

jaw_servo.angle = 135
right_eye_servo.angle =130
left_eye_servo.angle =50


# Set up timing variables
curr_time = time.monotonic()
prev_time = time.monotonic()
interval = 0.5
runs = 0

# Set up distance storage array
dist_hist = []
for n in range(0,100):
    dist_hist.append(None)

while True:
    # glow fireflies irrespective of FSM intervals
    for firefly in fireflies:
        next(firefly)
    # Update current time variable for running FSM
    curr_time = time.monotonic()
    diff_time  = curr_time - prev_time
    #print(diff_time)
    if diff_time > interval:
        #print(f"Jaw: {jaw_servo.angle}\r\nRight Eye: {right_eye_servo.angle}\r\nLeft Eye: {left_eye_servo.angle}")
        #print(f'Left eye: {left_eye.value}, right_eye: {right_eye.value}')
        
        if vl53.data_ready:
            dist = vl53.distance
            print(f'Distance: {dist}, mode: {vl53.distance_mode}')
            if dist is not None:
                dist_hist.pop(0)
                dist_hist.append(dist)
                print(slope(dist_hist,interval))
            else:   
                # Toggle between short and long distance modes when passing the transition point 
                if vl53.distance_mode == 1:
                    vl53.distance_mode = 2
                elif vl53.distance_mode == 2:
                    vl53.distance_mode = 1
            
        try:
            if dist <= 70:
                jaw_servo.angle = 160
                right_eye.value = True
                right_eye_servo.angle = 100
                left_eye.value = True
                left_eye_servo.angle = 80
                pass
            elif dist <= 250:
                jaw_servo.angle = 135
                right_eye.value = False
                right_eye_servo.angle = 180
                left_eye.value = True
                left_eye_servo.angle = 50
            else:
                jaw_servo.angle = 135
                right_eye.value = False
                right_eye_servo.angle = 180
                left_eye.value = False
                left_eye_servo.angle = 0
            
        except TypeError:
            jaw_servo.angle = 135
            right_eye.value = False
            right_eye_servo.angle = 180
            left_eye.value = False
            left_eye_servo.angle = 0
        
        # Update previous time and run counter at end of run
        prev_time = time.monotonic()
        runs += 1
