from fastapi import FastAPI

app = FastAPI()

@app.post("/topic")
def create_topic_handler():
    return {"Hello": "World"}

@app.post("/comment")
def read_root():
    return {"Hello": "World"}

@app.put("/vote")
def read_root():
    return {"Hello": "World"}
