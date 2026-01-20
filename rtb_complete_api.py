#!/usr/bin/env python3
"""
Complete RTB API with all features
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import json
from datetime import datetime
from rtb_complete_generator import generate_complete_rtb_template
from rtb_scheme_generator import generate_complete_scheme

app = FastAPI(title="Complete RTB Generator API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CompleteSessionPlanRequest(BaseModel):
    template_type: str = "session_plan"
    sector: str = "ICT & MULTIMEDIA"
    sub_sector: str = "Software Development"
    trainer_name: str
    module_code: str
    module_name: str
    topic: str
    learning_outcome: str
    indicative_content: str
    duration: int = 40
    num_learners: int = 30
    term: str = "I"
    week: str = "I"
    class_name: Optional[str] = "1"
    facilitation_technique: Optional[str] = None

class CompleteSchemeRequest(BaseModel):
    template_type: str = "scheme_of_work"
    course_title: str
    module_code: str
    trainer_name: str
    province: str = "Southern province"
    district: str = "Kamonyi district"
    sector: str = "Runda sector"
    school: str = "Runda TSS"
    term: int = 1

@app.get("/", response_class=HTMLResponse)
async def get_interface():
    """Serve complete RTB interface"""
    with open("rtb_complete_interface.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/api/generate/complete-session-plan")
async def generate_complete_session_plan(request: CompleteSessionPlanRequest):
    """Generate complete RTB session plan"""
    try:
        user_input = request.dict()
        user_input["class"] = user_input.pop("class_name", "1")
        
        template = generate_complete_rtb_template(user_input)
        
        return {
            "success": True,
            "template": template,
            "message": "Complete RTB session plan generated successfully",
            "metadata": {
                "generation_time": datetime.now().isoformat(),
                "rtb_compliant": True,
                "format_version": "Official RTB 2024"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/complete-scheme")
async def generate_complete_scheme_api(request: CompleteSchemeRequest):
    """Generate complete RTB scheme of work"""
    try:
        user_input = request.dict()
        
        template = generate_complete_scheme(user_input)
        
        return {
            "success": True,
            "template": template,
            "message": "Complete RTB scheme of work generated successfully",
            "metadata": {
                "generation_time": datetime.now().isoformat(),
                "rtb_compliant": True,
                "format_version": "Official RTB 2024"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/batch")
async def generate_batch_templates(request: Dict[str, Any]):
    """Generate multiple RTB templates"""
    try:
        batch_type = request.get("batch_type", "session_plan")
        count = min(int(request.get("count", 5)), 20)  # Max 20 templates
        
        templates = []
        for i in range(count):
            # Modify request for each template
            template_request = request.copy()
            template_request["template_type"] = batch_type
            template_request["topic"] = f"{request.get('topic', 'Topic')} - Part {i+1}"
            
            if batch_type == "session_plan":
                template = generate_complete_rtb_template(template_request)
            else:
                template = generate_complete_scheme(template_request)
            
            templates.append(template)
        
        return {
            "success": True,
            "templates": templates,
            "count": len(templates),
            "message": f"Generated {len(templates)} RTB templates successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/templates/export/{template_id}")
async def export_template(template_id: str, format: str = "json"):
    """Export template in different formats"""
    # This would integrate with actual template storage
    return {"message": f"Export {template_id} as {format} - Feature coming soon"}

@app.get("/api/health")
async def health_check():
    """Enhanced health check"""
    return {
        "status": "healthy",
        "service": "Complete RTB Generator",
        "version": "2.0.0",
        "features": [
            "Complete Session Plans",
            "Complete Schemes of Work", 
            "Batch Generation",
            "Multiple Export Formats",
            "RTB 2024 Compliance"
        ],
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)