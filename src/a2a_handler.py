import logging
from typing import Dict, Any
from src.dictionary_agent import DictionaryAgent

logger = logging.getLogger(__name__)


class A2AHandler:
    """
    Handles Agent-to-Agent (A2A) Protocol communication with Telex.im
    Uses JSON-RPC format
    """
    
    def __init__(self):
        self.agent = DictionaryAgent()
        logger.info(f"✅ A2A Handler initialized: {self.agent.name}")
    
    async def handle_a2a_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process A2A protocol message from Telex
        
        Expected JSON-RPC format:
        {
            "jsonrpc": "2.0",
            "method": "message",
            "params": {
                "message": "define ephemeral",
                "user": {...},
                "channel": {...}
            },
            "id": "request-id"
        }
        """
        try:
            # Validate JSON-RPC structure
            if payload.get("jsonrpc") != "2.0":
                return self._create_error_response(
                    payload.get("id"),
                    -32600,
                    "Invalid JSON-RPC version"
                )
            
            method = payload.get("method")
            params = payload.get("params", {})
            request_id = payload.get("id")
            
            logger.info(f"📨 A2A Request - Method: {method}, ID: {request_id}")
            
            # Handle different methods
            if method == "message":
                return await self._handle_message(params, request_id)
            
            elif method == "ping":
                return self._create_success_response(
                    request_id,
                    {"status": "ok", "agent": self.agent.name}
                )
            
            elif method == "info":
                return self._create_success_response(
                    request_id,
                    self._get_agent_info()
                )
            
            else:
                return self._create_error_response(
                    request_id,
                    -32601,
                    f"Method not found: {method}"
                )
        
        except Exception as e:
            logger.error(f"❌ A2A Handler error: {str(e)}", exc_info=True)
            return self._create_error_response(
                payload.get("id"),
                -32603,
                f"Internal error: {str(e)}"
            )
    
    async def _handle_message(self, params: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Handle incoming message - Telex optimized format"""
        try:
            # Extract message content (try multiple field names)
            message_text = (
                params.get("message") or
                params.get("text") or
                params.get("content") or
                params.get("input") or
                ""
            )
            
            user_info = params.get("user", {})
            channel_info = params.get("channel", {})
            
            user_id = user_info.get("id", "unknown") if isinstance(user_info, dict) else str(user_info)
            channel_id = channel_info.get("id", "unknown") if isinstance(channel_info, dict) else str(channel_info)
            
            logger.info(f"📝 Message from user {user_id} in channel {channel_id}: '{message_text}'")
            
            if not message_text or len(message_text.strip()) == 0:
                return self._create_error_response(
                    request_id,
                    -32602,
                    "No message content provided"
                )
            
            # Process with dictionary agent
            bot_response = self.agent.process_message(message_text)
            
            logger.info(f"🤖 Generated response ({len(bot_response)} chars): {bot_response[:100]}...")
            
            # Return response in multiple formats for compatibility
            result = {
                # Standard fields
                "type": "message",
                "content": bot_response,
                "format": "text",  # Changed from "markdown" to "text"
                
                # Alternative fields (Telex might look for these)
                "message": bot_response,
                "text": bot_response,
                "response": bot_response,
                
                # Metadata
                "status": "success",
                "agent": "SmartDict Bot"
            }
            
            response = self._create_success_response(request_id, result)
            
            logger.info(f"✅ Sending response: {str(response)[:200]}...")
            
            return response
        
        except Exception as e:
            logger.error(f"❌ Error in _handle_message: {str(e)}", exc_info=True)
            return self._create_error_response(
                request_id,
                -32603,
                f"Error processing message: {str(e)}"
            )
    
    def _create_success_response(self, request_id: str, result: Any) -> Dict[str, Any]:
        """Create JSON-RPC success response"""
        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }
    
    def _create_error_response(
        self, 
        request_id: str, 
        code: int, 
        message: str
    ) -> Dict[str, Any]:
        """Create JSON-RPC error response"""
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            },
            "id": request_id
        }
    
    def _get_agent_info(self) -> Dict[str, Any]:
        """Return agent information"""
        return {
            "name": self.agent.name,
            "version": "1.0.0",
            "capabilities": ["message", "definitions", "examples"],
            "commands": ["define", "meaning", "help"],
            "status": "online"
        }