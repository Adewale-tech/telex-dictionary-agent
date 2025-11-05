from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import logging
import sys
import os


PORT = int(os.getenv("PORT", 8000))
# Logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SmartDict Bot - Telex A2A Agent",
    description="Dictionary agent using A2A Protocol",
    version="1.0.0"
)

# Import A2A handler
from src.a2a_handler import A2AHandler

# Initialize
a2a_handler = A2AHandler()

# Serve agent.json manifest
@app.get("/.well-known/agent.json")
async def agent_manifest():
    """
    Serve the agent manifest file
    This is REQUIRED for Telex to discover your agent
    """
    manifest_path = os.path.join(os.path.dirname(__file__), "..", ".well-known", "agent.json")
    
    if os.path.exists(manifest_path):
        return FileResponse(manifest_path, media_type="application/json")
    else:
        raise HTTPException(status_code=404, detail="Manifest not found")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "status": "online",
        "agent": a2a_handler.agent.name,
        "version": "1.0.0",
        "protocol": "A2A (Agent-to-Agent)",
        "manifest": "/.well-known/agent.json",
        "endpoints": {
            "a2a_webhook": "/a2a/message",
            "health": "/health",
            "info": "/info"
        }
    }

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "agent": a2a_handler.agent.name
    }

@app.get("/info")
async def info():
    """Agent information"""
    return a2a_handler._get_agent_info()

@app.post("/a2a/message")
async def a2a_webhook(request: Request):
    """
    Main A2A Protocol webhook endpoint
    This is where Telex sends messages using JSON-RPC format
    """
    try:
        # Log incoming request
        body = await request.body()
        logger.info(f"📨 A2A Webhook called")
        logger.debug(f"Raw body: {body.decode('utf-8')}")
        
        # Parse JSON-RPC payload
        payload = await request.json()
        logger.info(f"📦 Payload: {payload}")
        
        # Process with A2A handler
        response = await a2a_handler.handle_a2a_message(payload)
        
        logger.info(f"📤 Response: {response}")
        
        return JSONResponse(content=response)
    
    except Exception as e:
        logger.error(f"❌ Webhook error: {str(e)}", exc_info=True)
        
        # Return JSON-RPC error
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal server error: {str(e)}"
                },
                "id": None
            }
        )

@app.post("/test")
async def test_agent(request: Request):
    """Test endpoint for local testing"""
    try:
        data = await request.json()
        message = data.get("message", "")
        
        response = a2a_handler.agent.process_message(message)
        
        return {
            "input": message,
            "output": response
        }
    
    except Exception as e:
        return {"error": str(e)}

# Run server
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"🚀 Starting SmartDict Bot (A2A Protocol) on port {port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )