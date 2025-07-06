from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import Optional, List
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
from dotenv import load_dotenv
import uuid
import time
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()
API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Initialize FastAPI app
app = FastAPI(
    title="DeepSeek Coder v2 API",
    description="Self-hosted DeepSeek Coder v2 API for code generation and analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this to your frontend domain in production
    # use late : allow_origins=["https://app.insightiq.kabutech.tech"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and tokenizer
model = None
tokenizer = None

class CodeRequest(BaseModel):
    prompt: str
    max_length: Optional[int] = 1024
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.95
    top_k: Optional[int] = 50
    do_sample: Optional[bool] = True
    num_return_sequences: Optional[int] = 1

class CodeResponse(BaseModel):
    id: str
    object: str = "text_completion"
    created: int
    model: str = "deepseek-coder-v2"
    choices: List[dict]
    usage: dict

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    model: Optional[str] = "deepseek-chat"
    stream: Optional[bool] = False


class AnalysisRequest(BaseModel):
    code: str
    analysis_type: Optional[str] = "general"  # general, security, performance, structure

class AnalysisResponse(BaseModel):
    id: str
    analysis: str
    suggestions: List[str]
    created: int

def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify API key"""
    if credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return credentials.credentials

def load_model():
    """Load DeepSeek Coder v2 model"""
    global model, tokenizer
    
    try:
        model_name = "deepseek-ai/deepseek-coder-1.3b-base"  # Using smaller model for 32GB RAM
        # Use deepseek-ai/deepseek-coder-6.7b-base if you have more RAM
        
        logger.info(f"Loading model: {model_name}")
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Load model with optimizations for your hardware
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,  # Use half precision to save memory
            device_map="auto",
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        
        logger.info("Model loaded successfully")
        
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise e

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    load_model()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "DeepSeek Coder v2 API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Health check with model status"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "tokenizer_loaded": tokenizer is not None
    }

@app.post("/v1/completions", response_model=CodeResponse)
async def create_completion(
    request: CodeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Generate code completion"""
    try:
        if model is None or tokenizer is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        # Tokenize input
        inputs = tokenizer.encode(request.prompt, return_tensors="pt")
        
        # Generate
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=min(request.max_length, 2048),
                temperature=request.temperature,
                top_p=request.top_p,
                top_k=request.top_k,
                do_sample=request.do_sample,
                num_return_sequences=request.num_return_sequences,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decode outputs
        generated_texts = []
        for output in outputs:
            generated_text = tokenizer.decode(output, skip_special_tokens=True)
            # Remove the original prompt from the generated text
            generated_text = generated_text[len(request.prompt):]
            generated_texts.append(generated_text)
        
        # Format response
        choices = []
        for i, text in enumerate(generated_texts):
            choices.append({
                "text": text,
                "index": i,
                "logprobs": None,
                "finish_reason": "stop"
            })
        
        return CodeResponse(
            id=f"cmpl-{uuid.uuid4()}",
            created=int(time.time()),
            choices=choices,
            usage={
                "prompt_tokens": len(inputs[0]),
                "completion_tokens": len(outputs[0]) - len(inputs[0]),
                "total_tokens": len(outputs[0])
            }
        )
        
    except Exception as e:
        logger.error(f"Error in completion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/analyze", response_model=AnalysisResponse)
async def analyze_code(
    request: AnalysisRequest,
    api_key: str = Depends(verify_api_key)
):
    """Analyze code and provide suggestions"""
    try:
        if model is None or tokenizer is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        # Create analysis prompt based on type
        if request.analysis_type == "security":
            analysis_prompt = f"Analyze the following code for security vulnerabilities and provide suggestions:\n\n{request.code}\n\nAnalysis:"
        elif request.analysis_type == "performance":
            analysis_prompt = f"Analyze the following code for performance issues and provide optimization suggestions:\n\n{request.code}\n\nAnalysis:"
        elif request.analysis_type == "structure":
            analysis_prompt = f"Analyze the following code structure and provide improvement suggestions:\n\n{request.code}\n\nAnalysis:"
        else:
            analysis_prompt = f"Analyze the following code and provide general suggestions for improvement:\n\n{request.code}\n\nAnalysis:"
        
        # Generate analysis
        inputs = tokenizer.encode(analysis_prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=1024,
                temperature=0.7,
                top_p=0.95,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decode response
        analysis_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        analysis_text = analysis_text[len(analysis_prompt):]
        
        # Extract suggestions (simple implementation)
        suggestions = []
        if "suggestion" in analysis_text.lower():
            lines = analysis_text.split('\n')
            for line in lines:
                if 'suggestion' in line.lower() or line.strip().startswith('-'):
                    suggestions.append(line.strip())
        
        return AnalysisResponse(
            id=f"analysis-{uuid.uuid4()}",
            analysis=analysis_text.strip(),
            suggestions=suggestions[:5],  # Limit to 5 suggestions
            created=int(time.time())
        )
        
    except Exception as e:
        logger.error(f"Error in analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/generate-data-dictionary")
async def generate_data_dictionary(
    request: CodeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Generate data dictionary from code or schema"""
    try:
        dict_prompt = f"Generate a comprehensive data dictionary for the following code or schema. Include field names, data types, descriptions, and constraints:\n\n{request.prompt}\n\nData Dictionary:"
        
        # Use the completion endpoint logic
        completion_request = CodeRequest(
            prompt=dict_prompt,
            max_length=request.max_length,
            temperature=0.3,  # Lower temperature for more consistent output
            top_p=0.9
        )
        
        return await create_completion(completion_request, api_key)
        
    except Exception as e:
        logger.error(f"Error generating data dictionary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/chat/completions")
async def chat_completion(
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
):
    """Chat completion endpoint using OpenAI message format"""
    try:
        if model is None or tokenizer is None:
            raise HTTPException(status_code=503, detail="Model not loaded")

        # Convert chat messages to a single prompt
        prompt_parts = []
        for msg in request.messages:
            if msg.role == "system":
                prompt_parts.append(f"[System]\n{msg.content}\n")
            elif msg.role == "user":
                prompt_parts.append(f"[User]\n{msg.content}\n")
            elif msg.role == "assistant":
                prompt_parts.append(f"[Assistant]\n{msg.content}\n")
        prompt_parts.append("[Assistant]\n")  # Indicate it's assistant's turn
        full_prompt = "\n".join(prompt_parts)

        # Tokenize and generate
        inputs = tokenizer.encode(full_prompt, return_tensors="pt")
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=min(request.max_tokens, 2048),
                temperature=request.temperature,
                pad_token_id=tokenizer.eos_token_id
            )

        output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        generated = output_text[len(full_prompt):].strip()

        return {
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": generated
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(inputs[0]),
                "completion_tokens": len(outputs[0]) - len(inputs[0]),
                "total_tokens": len(outputs[0])
            }
        }

    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )