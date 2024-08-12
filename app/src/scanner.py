# Author: Liu Yanzhao
# Admin No / Grp: 240333N / AA2402

#################################################################################
## PLEASE MAKE SURE ALL PYTHON LIBARIRES ARE INSTALLED AND PYTHON 3.7* IS USED ##
#################################################################################

# Copyright (c) 2024 yamgao_

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Importing required libaries
import cv2
import time
from pyzbar.pyzbar import decode, ZBarSymbol

class scanner():
    def __init__(self, camera_id):
        """
        initialise camera

        :param camera_id: id of the camera to start, usually 0
        """
        self.camera_id = camera_id
        self.cap = cv2.VideoCapture(self.camera_id)  # initialises which camera to start 

    def scan(self):
        """
        captures a frame from the camera

        finds for a barcode and returns the code if found. 
        """
        ret, frame = self.cap.read()
        code = None

        if ret:
            code = self.decode_barcode(frame)
            return code, frame

    def stop(self):
        """
        switches off camera
        """
        self.cap.release()

    def decode_barcode(self, frame):
        """
        looks for barcode and returns code if found

        :param frame: frame from cv2 capture
        """
        for d in decode(frame, symbols=[ZBarSymbol.CODE128]):
            code = d.data.decode()
            return code
    
    def code_check(self, code, data):
        """
        verifies if the code is valid and present in the list of product ids

        :param code: code to check 
        :param data: product ids to check against
        """
        for item in range(len(data)):
            if code == data[item][0]:
                return item
        return None


if __name__ == "__main__":
    s = scanner(0)
    while 1:
        code, frame = s.scan()
        cv2.imshow("test", frame)
        if code:
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit the loop
            break
        time.sleep(1/30)
    s.stop()
    print(code)