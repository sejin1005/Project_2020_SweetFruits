# Use HX711 Example.py

import threading
import time
import sys

class Get_Weight:
    def __init__(self):
        EMULATE_HX711 = False

        if not EMULATE_HX711:
            from modules.hx711 import HX711
        else:
            from modules.emulated_hx711 import HX711

        referenceUnit = 1

        
        self.hx = HX711(20, 16)
        self.hx.set_reading_format("MSB", "MSB")

        self.hx.set_reference_unit(474)
        self.hx.set_reference_unit(referenceUnit)

        self.hx.reset()

        self.hx.tare()

        print("Tare Done! Add weight now...")
    
    def measure_Weight(self):
        try:
            val = self.hx.get_weight(5) + 150
            print(val)

            self.hx.power_down()
            self.hx.power_up()
            time.sleep(0.1)
            return val
            #break
        except (KeyboardInterrupt, SystemExit):
            cleanAndExit()

    def cleanAndExit():
        print("Cleaning...")

        if not EMULATE_HX711:
            GPIO.cleanup()
        
        print("Bye!")
        sys.exit()
    
if __name__ == '__main__':
    
   # EMULATE_HX711 = False

    #if not EMULATE_HX711:
    #    from hx711 import HX711
    #else:
    #    from emulated_hx711 import HX711

    #referenceUnit = 1

    gw = Get_Weight()
    t = threading.Thread(target = gw.measure_Weight, args = ())
    t.start()
    print("done!")