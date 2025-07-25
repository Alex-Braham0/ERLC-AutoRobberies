import time
from datetime import datetime
from mss import mss
import numpy as np
from PIL import Image
import win32api
import win32con

x_offset = 0

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

    def binary_search_pixel(self, arr, pin_index, y_min, y_max, threshold_rgb, direction="up"):
        result = None
        threshold = self.brightness(threshold_rgb)

        while y_min + self.pinSizes[pin_index] <= y_max:
            y_mid = (y_min + y_max) // 2
            b, g, r, _ = arr[y_mid, self.pinLocations[pin_index]]
            current_brightness = self.brightness((r, g, b))

            if current_brightness > threshold:
                result = y_mid
                if direction == "up":
                    y_min = y_mid + 1  # search higher
                else:
                    y_max = y_mid - 1  # search lower
            else:
                if direction == "up":
                    y_max = y_mid - 1
                else:
                    y_min = y_mid + 1

        return result

    def brightness(self, rgb):
        r, g, b = rgb
        return 0.2126*r + 0.7152*g + 0.0722*b  # luminance

    def find_pin(self, pin_index, arr):
        high = None
        low = None

        high = self.binary_search_pixel(arr, pin_index, 379, 539, (140, 140, 140), "up")
        low = self.binary_search_pixel(arr, pin_index, 541, 700, (140, 140, 140), "down")
        # print(f"{high}, {low}")
        return (high, low)

    def calculate_average_speed(self, past_locations):
        speeds = []
        for location_index in range(1, len(past_locations)):
            speeds.append(abs(past_locations[location_index-1]-past_locations[location_index]))
        return sum(speeds)/len(speeds)
    
    def calculate_direction(self, last_location, location):
        down_direction = None
        if (last_location[0] != None and location[0] == None) or (last_location[1] == None and location[1] != None):
            down_direction = True
        elif (last_location[0] == None and location[1] != None) or (last_location[1] != None and location[1] == None):
            down_direction = False
        elif last_location[0] != None and location[0] != None and (last_location[0] < location[0]):
            down_direction = True
        elif last_location[1] != None and location[1] != None and (last_location[1] < location[1]):
            down_direction = True
        elif last_location[0] != None and location[0] != None and (last_location[0] > location[0]):
            down_direction = False
        elif last_location[1] != None and location[1] != None and (last_location[1] > location[1]):
            down_direction = False
        elif last_location[0] == 379 and location[0] == 379:
            down_direction = True
        elif last_location[0] == 700 and location[0] == 700:
            down_direction = True
        else:
            print("Error:")
            print(f"last loc: {last_location}")
            print(f"current loc: {location}")
        return down_direction

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

            # with mss() as sct:
            #     shot = sct.grab(sct.monitors[1])
            #     arr = np.array(shot)              # BGRA
            #     b, g, r, a = arr[540, 675]       # pixel at (675, 540)
            #     rgb = (r, g, b)
            #     print(rgb)
            if self.getpixel(arr, 675+x_offset, 540) != (255, 201, 3):
                if index == 0:
                    successful = False
                else:
                    failed = True
                # successful = False
                break
            
            # Displaying the current pin being processed
            print(f"Pin {index+1}")

            # Waiting for pin and target line to overlap
            # pin_over_lin = False
            
            # past_locations = []
            # location = self.find_pin(index, arr)
            # while not pin_over_lin:#self.getpixel(arr, pin, 530) != (165, 165, 165) and self.getpixel(arr, pin, 550) != (165, 165, 165):
            
            valid_pin = False
            pin_over_line = None
            wait_for_clear = True
            arr = self.screenshot()
            while not valid_pin:
                
                if self.brightness(self.getpixel(arr, pin+x_offset, 539)) > self.brightness((130, 130, 130)) and self.brightness(self.getpixel(arr, pin+x_offset, 541)) > self.brightness((130, 130, 130)):
                    pin_over_line = True
                if not pin_over_line and wait_for_clear:
                    wait_for_clear = False
                valid_pin = pin_over_line and not wait_for_clear
                time.sleep(0.01)
                arr = self.screenshot()
            self.fast_click()
            self.save_np_as_png(arr, f"fast-{index+1}.png")

                # past_locations.append(location)
                # if len(past_locations) > 10:
                #     past_locations.pop(0)
                
                # location = self.find_pin(index, arr)

                # if past_locations[-1] == (None, None) or location == (None, None):
                #     self.save_np_as_png(arr, f"error.png")
                #     continue
                
                # if len(past_locations) < 2:
                #     continue

                # # print(past_locations[-1], location)
                # # print("last check")
                # down_direction=self.calculate_direction(past_locations[-1], location)
                # if down_direction == None:
                #     continue
                # if down_direction: # Moving Down

                #     if location[1] != None and past_locations[-1][1] == None:
                #         print("Click")
                #         pin_over_lin = True
                #     # if location[0] != None and past_locations[-1][0] != None and past_locations[-1][1] == None and ((location[1] != None and location[1] == 541 and past_locations[-1][0] < 539) or (location[0] < 539 and location[0] > 540-(540-past_locations[-1][0])/2)):
                #     #     print("Click")
                #     #     pin_over_lin = True
                #         # self.save_np_as_png(arr, f"click-{location}.png")

                # else:
                #     if location[0] != None and past_locations[-1][0] == None:
                #         print("Click")
                #         pin_over_lin = True
                    # if location[1] != None and past_locations[-1][1] != None and past_locations[-1][0] == None and ((location[0] != None and location[0] == 539 and past_locations[-1][1] > 541) or (location[1] > 541 and location[1] < 540+(540-past_locations[-1][1])/2)):
                    #     print("Click")
                    #     pin_over_lin = True


                    # print(abs(past_locations[-1]-location) < speed*1.3)
                    # if location >= 540-(past_locations[-1]-location)/2 and past_locations[-1] < 540:# and abs(past_locations[-1]-location) < speed*1.75:#-self.pinSizes[index]//2:
                    #     print("Click")
                    #     self.save_np_as_png(arr, f"click.png")
                    #     exit()
                        # pin_over_lin = True
                # elif not down_direction: # Moving up
                #     if location <= 540+(past_locations[-1]-location)/2 and past_locations[-1] > 540  and abs(past_locations[-1]-location) < speed*1.3:#+self.pinSizes[index]//2:
                #         pin_over_lin = True

            # print(location)
            # print(past_locations)
            # print(f"Direction: {'Down' if down_direction else 'Up'}")
            # self.fast_click()
            # # pydirectinput.click()
            # self.save_np_as_png(arr, f"fast-{index+1}.png")
            
            # time.sleep(0.1)

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