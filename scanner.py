import cv2
from pyzbar.pyzbar import decode, ZBarSymbol

class scanner():
    def __init__(self, camera_id, delay, window_name):
        self.camera_id = camera_id
        self.delay = delay
        self.window_name = window_name

    def scan(self):
        cap = cv2.VideoCapture(self.camera_id)

        while True:
            ret, frame = cap.read()
            code = None

            if ret:
                code = self.decode_barcode(frame)
                cv2.imshow(self.window_name, frame)

            # breaks out of while loop when code is scanned or when 'q' is pressed
            if cv2.waitKey(self.delay) & 0xFF == ord('q') or code:
                break 
        
        cv2.destroyWindow(self.window_name)
        return code

    def decode_barcode(self, frame):
        for d in decode(frame, symbols=[ZBarSymbol.CODE128]):
            code = d.data.decode()
            return code
        

if __name__ == "__main__":
    s = scanner(0, 1, 'Scanner')
    code = s.scan()
    print(code)