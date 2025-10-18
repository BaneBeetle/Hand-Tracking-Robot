
from robot_hat import Servo
import time

# Create Servo object with PWM object 
grip = Servo("P11") 
neck = Servo('P10') 
torso = Servo('P9') 
hips = Servo('P8')

print("Center")

grip.angle(0)
time.sleep(2)
neck.angle(0)
time.sleep(2)
torso.angle(0)
time.sleep(2)
hips.angle(0)

time.sleep(2)
print("Moving to extremes (-90 degrees)")
torso.angle(-90)
time.sleep(2)
neck.angle(-90)
time.sleep(2)
grip.angle(-90)
time.sleep(2)
hips.angle(-90)
time.sleep(2)
hips.angle(90)
time.sleep(2)
hips.angle(0)
