import time
import statistics
from datetime import datetime, timedelta
from mss import mss
import numpy as np
from PIL import Image
import win32api
import win32con

# Atm robbery 6 min cooldown

# use mss instead
# fix timeout

class ATMRobberyScript:
    name = "ATM Robbery"
    cooldown = 6*60 # 6 mins
    def __init__(self):
        # List of pixel locations to click based on the colours
        self.locations = [
            [680,428],
            [680,462],
            [680,492],
            [680,525],
            [680,555],
            [680,590],
            [680,625],
            [680,655],
            [680,690],
            [680,722],
            [845,428],
            [845,462],
            [845,492],
            [845,525],
            [845,555],
            [845,590],
            [845,625],
            [845,655],
            [845,690],
            [845,722],
            [1010,428],
            [1010,462],
            [1010,492],
            [1010,525],
            [1010,555],
            [1010,590],
            [1010,625],
            [1010,655],
            [1010,690],
            [1010,722],
            [1175,428],
            [1175,462],
            [1175,492],
            [1175,525],
            [1175,555],
            [1175,590],
            [1175,625],
            [1175,655],
            [1175,690],
            [1175,722]
        ]   

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

    def findColours(self, arr=None):
        if not arr:
            arr = self.screenshot()
        self.colours = []
        black = self.getpixel(arr, 978,390)
        if black != (0,0,0):
            print(f"Black has been defind: {black}")
        for location in self.locations:
            cellColours = []
            for n in range(0, 65):
                currentColour = self.getpixel(arr, location[0]+n, location[1])
                if currentColour != black:
                    cellColours.append(currentColour)  
            self.colours.append(statistics.mode(cellColours))
        print("Scanned all code colours")

    def euclidean(self, a, b):
        return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5

    def get_current_code_colour(self):
        arr = self.screenshot()
        cellColours = []
        for y in [349, 356, 364]:
            for x in range(0, 60):
                currentColour = self.getpixel(arr, 1040+x, y)
                if currentColour != (0,0,0):
                    cellColours.append(currentColour)
        
        return cellColours

    def is_code_colour_valid(self, code_colours):
        mode = statistics.mode(code_colours)
        if mode in self.colours:
            target = self.colours.index(mode)
            return target
        else:
            print("No colour match\nEstimating Colour")
            return self.colours.index(min(self.colours, key=lambda c: self.euclidean(mode, c)))
    
    def is_robbery_active(self, arr=None):
        if not arr:
            arr = self.screenshot()
        return self.getpixel(arr, 549,266) == (27,42,53) and self.getpixel(arr, 978,390) == (0,0,0)
    
    def is_robbery_failed(self, arr=None):
        if not arr:
            arr = self.screenshot()
        return self.getpixel(arr, 549,266) == (27,42,53) and self.getpixel(arr, 948,307) == (193,34,34)

    def rgb_to_url(self, rgb):
        hex_code = f'{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
        return f'https://www.colorhexa.com/{hex_code}'

    def run(self):
        # Displaying a countdown message before starting the main loop
        for sleep in range(5):
            print(f"Starting in {5-sleep}")
            time.sleep(1)

        if not self.is_robbery_active():
            print("Robbery not detected")
            return False

        self.findColours()
        
        # Main ATM hacking loop
        no_of_codes = 5
        code = 0
        # timeout = False
        while self.is_robbery_active(): # decode each of the 5 codes

            code_colours = self.get_current_code_colour()
            valid_colour_index = self.is_code_colour_valid(code_colours)
            # rgb = self.colours[valid_colour_index]
            # # print(f"Colour: {rgb}")
            # # print(self.rgb_to_url(rgb))
            print(f"Column: {(valid_colour_index//10)+1}")
            print(f"Row: {(valid_colour_index%10)+1}")

            print("Found current Code location")

            notClicked = True
            start = datetime.now()
            timeout = False
            while notClicked:# and not timeout:
                # Click when specified location matches colour
                
                arr = self.screenshot()
                if self.getpixel(arr, self.locations[valid_colour_index][0],self.locations[valid_colour_index][1]) == self.colours[valid_colour_index]:
                    self.fast_click()
                    print("Clicked")
                    self.save_np_as_png(arr, f"valid-{code}.png")
                    notClicked = False
                    code += 1
                    time.sleep(0.05)
                else:
                    timeout = datetime.now() - start > timedelta(seconds=30)

        # if not timeout:
        failed = self.is_robbery_failed()

        if not failed:
            print("ATM Completed")
        return True
        # else:
        #     print("Robbery Timed out")
        #     return True

if __name__ == "__main__":
    atm = ATMRobberyScript()
    atm.run()