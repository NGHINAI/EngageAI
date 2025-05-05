from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Example model for user authentication
class UserCreate(BaseModel):
    username: str
    password: str

@app.get("/api/v1/healthcheck")
def healthcheck():
    return {"status": "ok"}