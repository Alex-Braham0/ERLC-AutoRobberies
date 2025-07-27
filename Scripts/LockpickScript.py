import time
from datetime import datetime
from mss import mss
import numpy as np
from PIL import Image
import win32api
import win32con

# House robbery 5 minute cooldown

# do direction detection for pins

class LockpickScript:
    name = "Lockpick Robbery"
    cooldown = 5*60 # 5 mins
    def __init__(self):
        # List of pixel locations representing pins on the lock
        self.pinLocations = [746, 831, 917, 1002, 1088, 1173]
        self.pinSizes = [119, 96, 73, 49, 41, 34]

    def screenshot(self):
        with mss() as sct:
            shot = sct.grab(sct.monitors[1])  # Full screen
            # img = np.array(shot)[..., :3][..., ::-1]  # BGRA → RGB
            return np.array(shot)

    def pixel(self, x, y):
        with mss() as sct:
            shot = sct.grab(sct.monitors[1])
            arr = np.array(shot)              # BGRA
            b, g, r, a = arr[y, x]       # pixel at (675, 540)
            return (r, g, b)
        
    def getpixel(self, arr, x, y):
        b, g, r, a = arr[y, x]       # pixel at (675, 540)
        return (r, g, b)

    def fast_click(self, x=None, y=None):
        if x is not None and y is not None:
            win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

    def save_np_as_png(self, arr, filename):
        # Convert NumPy array (H, W, 3) or (H, W, 4) to PIL Image
        img = Image.fromarray(arr)
        img.save(filename)

    def brightness(self, rgb):
        r, g, b = rgb
        return 0.2126*r + 0.7152*g + 0.0722*b  # luminance

    def lightness(self, rgb):
        r, g, b = rgb
        return (max(r, g, b) + min(r, g, b)) / 2


    def find_pin(self, arr, pin_index):
        threshold = (100,100,100)
        # high = self.binary_search_pixel(arr, pin_index, 379, 539, threshold, "low")
        # low = self.binary_search_pixel(arr, pin_index, 541, 700, threshold, "high")

        high = self.linear_search_pixel(arr, pin_index, 379, 539, threshold, "positive")
        low = self.linear_search_pixel(arr, pin_index, 541, 700, threshold, "negative")
        return (high, low)
    
    def linear_search_pixel(self, arr, pin_index, y_min, y_max, threshold_rgb, direction="positive"):
        result = None
        threshold = self.brightness(threshold_rgb)
        if direction == "positive":
            range_y = range(y_min, y_max + 1)
        else:
            range_y = range(y_max, y_min - 1, -1)

        for y in range_y:
            if self.brightness(self.getpixel(arr, self.pinLocations[pin_index], y)) > threshold:
                result = y
                break
        return result

    def calc_pin_direction(self, pin_location, last_location):
        down_direction = None
        if pin_location[0] != None and last_location[0] != None:
            if pin_location[0] < last_location[0]:
                down_direction = False
            elif pin_location[0] > last_location[0]:
                down_direction = True
        elif pin_location[1] != None and last_location[1] != None:
            if pin_location[1] < last_location[1]:
                down_direction = False
            elif pin_location[1] > last_location[1]:
                down_direction = True
        elif (pin_location[1] == None and last_location[1] != None) or (pin_location[1] != None and last_location[1] == None):
            down_direction = True
        elif (pin_location[0] == None and last_location[0] != None) or (pin_location[0] != None and last_location[0] == None):
            down_direction = False
        else:
            print("Direction not detected")
        # print(f"Direction: {down_direction}")
        return down_direction

    def calc_pin_speed(self, pin_location, last_location):
        speed = None
        if pin_location[0] != None and last_location[0] != None:
            speed = abs(pin_location[0]-last_location[0])
        elif pin_location[1] != None and last_location[1] != None:
            speed = abs(pin_location[1]-last_location[1])
        else:
            print("Speed not detected")
            print(f"Current: {pin_location}")
            print(f"Last: {last_location}")
        # print(f"Speed: {speed}")
        return speed

    def run(self):
        # Displaying a countdown message before starting the main loop
        for sleep in range(3):
            print(f"Starting in {3 - sleep}")
            time.sleep(1)

        start_countdown = True

        successful = True
        failed = False

        # Looping through each pin location
        for index, pin in enumerate(self.pinLocations):
            arr = self.screenshot()
            # Checking if the color at a specific location indicates an ongoing robbery

            if self.getpixel(arr, 675, 540) != (255, 201, 3):
                if index == 0:
                    successful = False
                else:
                    failed = True
                # successful = False
                break
            
            # Displaying the current pin being processed
            print(f"Pin {index+1}")
            ready_to_click = False
            arr = self.screenshot()
            pin_location = self.find_pin(arr, index)
            down_direction = True
            speed = 0
            while not ready_to_click:

                last_location = pin_location
                pin_location = self.find_pin(arr, index)
                
                new_direction = self.calc_pin_direction(pin_location, last_location)
                if new_direction != None:
                    down_direction = new_direction
                new_speed = self.calc_pin_speed(pin_location, last_location)
                if new_speed != None:
                    speed = new_speed
                
                if down_direction:
                    if pin_location[0] != None and pin_location[0]+self.pinSizes[index] < 539 and pin_location[0]+self.pinSizes[index] > 540-speed and speed <100:
                        # print(pin_location)
                        # print(f"Going Down at {speed}")
                        print("Click")
                        ready_to_click = True
                         
                else:
                    if pin_location[1] != None and pin_location[1]-self.pinSizes[index] > 539 and pin_location[1]-self.pinSizes[index] < 540+speed and speed <100:
                        # print(pin_location)
                        # print(f"Going Up at {speed}")
                        print("Click")
                        ready_to_click = True

                if not ready_to_click:
                    arr = self.screenshot()
            
            self.fast_click()
            # self.save_np_as_png(arr, f"fast-{index+1}.png")

            time.sleep(0.05)

        time.sleep(0.05)
        
        if not failed:
            failed = self.check_for_fail_notif()
            
        # Displaying a message when the main loop exits
        start_countdown = successful and not failed

        if successful and not failed:
            print("Lockpick Completed")
        elif failed:
            print("Lockpick Failed")
        else:
            print("Robbery not detected")
        
        return start_countdown
    
    def check_for_fail_notif(self):
        arr = self.screenshot()
        failed = False
        if (self.getpixel(arr, 0, 800) == (255,0,0) and self.getpixel(arr, 4, 815) == (255,0,0)):
            failed = True
        elif (self.getpixel(arr, 0, 696) == (255,0,0) and self.getpixel(arr, 4, 726) == (255,0,0)):
            failed = True
        return failed

if __name__ == "__main__":
    lockpick = LockpickScript()
    lockpick.run()