#!/usr/bin/env python3
"""
RTB API - FastAPI endpoint for RTB template generation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import json
from rtb_ai_generator import generate_rtb_templates

app = FastAPI(title="RTB Template Generator API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SessionPlanRequest(BaseModel):
    template_type: str = "session_plan"
    sector: str = "ICT & MULTIMEDIA"
    sub_sector: str = "Software Development"
    trainer_name: str
    module: str
    topic: str
    learning_outcome: str
    duration: int = 40
    num_learners: int = 30
    term: str = "I"
    week: str = "I"
    class_name: Optional[str] = "1"

class SchemeOfWorkRequest(BaseModel):
    template_type: str = "scheme_of_work"
    course_title: str
    module_code: str
    trainer_name: str
    province: str = "Southern province"
    district: str = "Kamonyi district"
    sector: str = "Runda sector"
    school: str = "Runda TSS"

@app.get("/", response_class=HTMLResponse)
async def get_interface():
    """Serve the RTB web interface"""
    with open("rtb_web_interface.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/api/generate/session-plan")
async def generate_session_plan(request: SessionPlanRequest):
    """Generate RTB Session Plan"""
    try:
        # Convert to dict for the generator
        user_input = request.dict()
        user_input["class"] = user_input.pop("class_name", "1")
        
        # Generate template
        template = generate_rtb_templates(user_input)
        
        return {
            "success": True,
            "template": template,
            "message": "Session plan generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/scheme-of-work")
async def generate_scheme_of_work(request: SchemeOfWorkRequest):
    """Generate RTB Scheme of Work"""
    try:
        # Convert to dict for the generator
        user_input = request.dict()
        
        # Generate template
        template = generate_rtb_templates(user_input)
        
        return {
            "success": True,
            "template": template,
            "message": "Scheme of work generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate")
async def generate_template(request: Dict[str, Any]):
    """Universal template generation endpoint"""
    try:
        template = generate_rtb_templates(request)
        
        return {
            "success": True,
            "template": template,
            "message": f"RTB {request.get('template_type', 'template')} generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "RTB Template Generator"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)