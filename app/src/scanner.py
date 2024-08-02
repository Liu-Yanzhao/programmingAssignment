import cv2
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
    s = scanner(0, 1, 'Scanner')
    code = s.scan()
    print(code)