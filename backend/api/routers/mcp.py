from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from api.services import mcp_adapter

router = APIRouter(prefix="/mcp", tags=["mcp"])


class StoriesRequest(BaseModel):
    stories: List[Dict[str, Any]]


class RequirementsRequest(BaseModel):
    stories: List[Dict[str, Any]]


class ReportRequest(BaseModel):
    requirements: List[Dict[str, Any]]
    project_id: Optional[str] = "default"


@router.post("/analyze")
def analyze_stories(req: StoriesRequest):
    # call analyzer MCP
    resp = mcp_adapter.call_mcp("mcp_analyzer", "analyze_stories", {"stories": req.stories})
    if resp.get("error"):
        raise HTTPException(status_code=500, detail=resp)
    return resp


@router.post("/requirements")
def extract_and_prioritize(req: RequirementsRequest):
    # identify
    id_resp = mcp_adapter.call_mcp("mcp_requirement", "identify_requirements", {"stories": req.stories})
    if id_resp.get("error"):
        raise HTTPException(status_code=500, detail=id_resp)
    requirements = id_resp.get("response", {}).get("requirements", [])

    # prioritize
    pri_resp = mcp_adapter.call_mcp("mcp_requirement", "prioritize", {"requirements": requirements})
    if pri_resp.get("error"):
        raise HTTPException(status_code=500, detail=pri_resp)
    return pri_resp


@router.post("/report")
def build_report(req: ReportRequest):
    resp = mcp_adapter.call_mcp(
        "mcp_reporter",
        "build_final_report",
        {
            "core_requirements": req.requirements,
            "analyzer_output": {},
            "project_id": req.project_id,
        },
    )
    if resp.get("error"):
        raise HTTPException(status_code=500, detail=resp)
    return resp
