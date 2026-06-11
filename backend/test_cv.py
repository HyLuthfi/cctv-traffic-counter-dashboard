import cv2
import os
from app.cv.capture import AmbilFrame
from app.cv.detector import DetektorKendaraan
from app.cv.counter import PenghitungKendaraan

def jalankan_tes():
    sumber = "https://raw.githubusercontent.com/intel-iot-devkit/sample-videos/master/person-bicycle-car-detection.mp4"
    pengambil = AmbilFrame(sumber)
    detektor = DetektorKendaraan("yolov8n.pt")
    penghitung = PenghitungKendaraan(garis_y=200)

    print("Memulai pemrosesan video...")

    while True:
        sukses, frame = pengambil.baca_frame()
        if not sukses:
            break

        hasil = detektor.deteksi_dan_lacak(frame)
        penghitung.proses_deteksi(hasil)

        frame_annotasi = hasil.plot()
        cv2.line(frame_annotasi, (0, 200), (frame.shape[1], 200), (0, 0, 255), 2)
        
        teks = f"Masuk: {penghitung.jumlah_masuk} | Keluar: {penghitung.jumlah_keluar}"
        cv2.putText(frame_annotasi, teks, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("TrafficVision - CV Engine", frame_annotasi)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    pengambil.lepas()
    cv2.destroyAllWindows()
    
    print(f"Total Masuk: {penghitung.jumlah_masuk}")
    print(f"Total Keluar: {penghitung.jumlah_keluar}")

if __name__ == "__main__":
    jalankan_tes()
