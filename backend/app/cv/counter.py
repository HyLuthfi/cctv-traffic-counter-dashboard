class PenghitungKendaraan:
    def __init__(self, garis_y):
        self.garis_y = garis_y
        self.posisi_sebelumnya = {}
        self.jumlah_masuk = 0
        self.jumlah_keluar = 0

    def proses_deteksi(self, hasil_deteksi):
        if hasil_deteksi.boxes is None or hasil_deteksi.boxes.id is None:
            return

        kotak = hasil_deteksi.boxes.xyxy.cpu().numpy()
        id_objek = hasil_deteksi.boxes.id.cpu().numpy()

        for (x1, y1, x2, y2), obj_id in zip(kotak, id_objek):
            pusat_y = (y1 + y2) / 2

            if obj_id in self.posisi_sebelumnya:
                y_lama = self.posisi_sebelumnya[obj_id]

                if y_lama < self.garis_y and pusat_y >= self.garis_y:
                    self.jumlah_masuk += 1
                elif y_lama > self.garis_y and pusat_y <= self.garis_y:
                    self.jumlah_keluar += 1

            self.posisi_sebelumnya[obj_id] = pusat_y
