import cv2

class AmbilFrame:
    def __init__(self, sumber_video):
        self.kamera = cv2.VideoCapture(sumber_video)
        if not self.kamera.isOpened():
            raise ValueError(f"Gagal membuka sumber video: {sumber_video}")

    def baca_frame(self):
        sukses, frame = self.kamera.read()
        return sukses, frame

    def lepas(self):
        self.kamera.release()
