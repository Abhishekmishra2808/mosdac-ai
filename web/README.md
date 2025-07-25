# MOSDAC Chatbot Backend

## Quick Start

The backend was successfully diagnosed and should now be ready to run!

### Prerequisites ✅
- ✅ FastAPI installed
- ✅ Uvicorn installed  
- ✅ Google Generative AI installed
- ✅ Python-dotenv installed
- ✅ Scraped data available (52 pages loaded)
- ✅ GEMINI_API_KEY configured
- ✅ API module loads successfully

### Running the Backend

You have several options to start the backend:

#### Option 1: Using Python directly
```bash
cd "c:\Users\abhis\Desktop\modac-chatbot-scraper\web"
C:/Users/abhis/Desktop/modac-chatbot-scraper/venv/Scripts/python.exe api.py
```

#### Option 2: Using Uvicorn (Recommended)
```bash
cd "c:\Users\abhis\Desktop\modac-chatbot-scraper\web"
C:/Users/abhis/Desktop/modac-chatbot-scraper/venv/Scripts/uvicorn.exe api:app --host 127.0.0.1 --port 8000 --reload
```

#### Option 3: Using the batch files
- Double-click `start_backend.bat` or
- Double-click `start_backend_uvicorn.bat`

### Testing the Backend

#### Option 1: Run the diagnostic test
```bash
cd "c:\Users\abhis\Desktop\modac-chatbot-scraper\web"
C:/Users/abhis/Desktop/modac-chatbot-scraper/venv/Scripts/python.exe test_backend.py
```

#### Option 2: Test the API endpoints
Once the server is running, you can test:
- Health check: http://127.0.0.1:8000/
- Interactive docs: http://127.0.0.1:8000/docs

### API Endpoints

- `GET /` - Health check endpoint
- `POST /chat` - Chat with the MOSDAC chatbot
  ```json
  {
    "message": "What is MOSDAC?"
  }
  ```

### Data Loaded
- 📊 52 pages of MOSDAC content
- 🛰️ 224 data products across 37 pages  
- 📊 43 tables across 27 pages
- 📝 189 lists across 34 pages

### Troubleshooting

If you encounter issues:

1. **Import errors**: Run `test_backend.py` to diagnose
2. **Data not found**: Make sure you're in the web directory when starting
3. **API key issues**: Check your `.env` file
4. **Port already in use**: Change the port number in the command

### Files Created/Modified
- ✅ `requirements.txt` - Added FastAPI dependencies
- ✅ `.env` - Environment variables (contains your API key)
- ✅ `api.py` - Added main block for running server
- ✅ `chatbot.py` - Fixed data path resolution
- ✅ `test_backend.py` - Diagnostic tool
- ✅ `start_backend.bat` - Windows startup script
- ✅ `start_backend_uvicorn.bat` - Alternative startup script
