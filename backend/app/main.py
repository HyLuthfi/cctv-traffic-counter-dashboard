from fastapi import FastAPI

app = FastAPI(
    title="TrafficVision API",
    description="Backend API untuk sistem pemantauan lalu lintas",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "TrafficVision API is running"}
