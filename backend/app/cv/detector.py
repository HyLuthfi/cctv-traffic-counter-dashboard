from ultralytics import YOLO

class DetektorKendaraan:
    def __init__(self, model_path="yolov8n.pt"):
        self.model = YOLO(model_path)
        self.kelas_kendaraan = [2, 3, 5, 7]

    def deteksi_dan_lacak(self, frame):
        hasil = self.model.track(frame, persist=True, classes=self.kelas_kendaraan, verbose=False)
        return hasil[0]
