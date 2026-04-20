from fastapi import FastAPI

app = FastAPI(title="Construction Material Tracker")


@app.get("/")
async def root():
    return {"message": "Construction Tracker is running"}
