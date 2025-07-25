from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatbot import MOSDACChatbot

app = FastAPI()

# CORS configuration - Allow frontend to connect to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local React development
        "http://127.0.0.1:3000",  # Alternative localhost
        "https://mosdac-ai.onrender.com",  # Your deployed backend
        "*"  # Allow all origins (for testing)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chatbot = MOSDACChatbot()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    answer = chatbot.generate_response(req.message)
    return ChatResponse(answer=answer)

@app.get("/")
def root():
    return {"status": "MOSDAC Chatbot API running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
