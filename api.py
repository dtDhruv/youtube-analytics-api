from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn
from yt import get_data
import os

app = FastAPI()


@app.get("/yt/{id}")
async def root(id):
    csv_file_path = "./data.csv"
    get_data(id)
    if os.path.exists(csv_file_path):
        return FileResponse(path=csv_file_path, filename=csv_file_path, media_type="text/csv")
    else:
        return {"error": "CSV file not found"}
    return {"message": id}

def main():
    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )   
    
if __name__ == "__main__":
    main()