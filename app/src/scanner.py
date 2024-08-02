import cv2
from pyzbar.pyzbar import decode, ZBarSymbol

class scanner():
    def __init__(self, camera_id, delay, window_name):
        self.camera_id = camera_id
        self.delay = delay
        self.window_name = window_name
        self.cap = cv2.VideoCapture(self.camera_id)

    def scan(self):
        ret, frame = self.cap.read()
        code = None

        if ret:
            code = self.decode_barcode(frame)
            return code, frame

    def stop(self):
        self.cap.release()

    def decode_barcode(self, frame):
        for d in decode(frame, symbols=[ZBarSymbol.CODE128]):
            code = d.data.decode()
            return code
    
    def code_check(self, code, data):
        for item in range(len(data)):
            if code == data[item][0]:
                return item
        return None


if __name__ == "__main__":
    s = scanner(0, 1, 'Scanner')
    code = s.scan()
    print(code)