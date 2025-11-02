from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime

from api.services import mcp_adapter

router = APIRouter(prefix="/mcp", tags=["mcp"])


class StoriesRequest(BaseModel):
    stories: List[Dict[str, Any]]


class RequirementsRequest(BaseModel):
    stories: List[Dict[str, Any]]


class ReportRequest(BaseModel):
    requirements: List[Dict[str, Any]]
    project_id: Optional[str] = "default"


class PipelineRequest(BaseModel):
    # Accept either raw_text (single document) or structured stories
    raw_text: Optional[str] = None
    stories: Optional[List[Dict[str, Any]]] = None
    project_id: Optional[str] = "default"


class CollectorIngestRequest(BaseModel):
    items: List[str]
    doc_id: Optional[str] = "doc"
    project_id: Optional[str] = "default"
    version: Optional[str] = "1"
    source_type: Optional[str] = "paste"
    filename: Optional[str] = None
    uploaded_by: Optional[str] = "user"
    timestamp: Optional[str] = None


class CollectorNormalizeRequest(BaseModel):
    chunks: List[Dict[str, Any]]
    one_liner: Optional[bool] = False


class CollectorExtractStoriesRequest(BaseModel):
    chunks: List[Dict[str, Any]]


@router.post("/collector/ingest")
def collector_ingest(req: CollectorIngestRequest):
    """Collector: Ingest raw text into chunks"""
    resp = mcp_adapter.call_mcp(
        "mcp_collector",
        "ingest_raw",
        {
            "items": req.items,
            "doc_id": req.doc_id,
            "project_id": req.project_id,
            "version": req.version,
            "source_type": req.source_type,
            "filename": req.filename,
            "uploaded_by": req.uploaded_by,
            "timestamp": req.timestamp or datetime.utcnow().isoformat(),
        }
    )
    if resp.get("error"):
        raise HTTPException(status_code=500, detail=resp)
    return resp


@router.post("/collector/normalize")
def collector_normalize(req: CollectorNormalizeRequest):
    """Collector: Normalize chunks"""
    resp = mcp_adapter.call_mcp(
        "mcp_collector",
        "normalize",
        {"chunks": req.chunks, "one_liner": req.one_liner}
    )
    if resp.get("error"):
        raise HTTPException(status_code=500, detail=resp)
    return resp


@router.post("/collector/extract-stories")
def collector_extract_stories(req: CollectorExtractStoriesRequest):
    """Collector: Extract structured stories from normalized chunks"""
    resp = mcp_adapter.call_mcp(
        "mcp_collector",
        "extract_stories",
        {"chunks": req.chunks}
    )
    if resp.get("error"):
        raise HTTPException(status_code=500, detail=resp)
    return resp


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


@router.post("/pipeline")
def run_pipeline(req: PipelineRequest):
    # 1) If raw_text provided, run collector.ingest_raw -> normalize -> extract_stories
    stories = req.stories or []
    if req.raw_text and not stories:
        # ingest
        ing = mcp_adapter.call_mcp("mcp_collector", "ingest_raw", {"items": [req.raw_text]})
        if ing.get("error"):
            raise HTTPException(status_code=500, detail={"stage": "collector.ingest_raw", "error": ing})
        chunks = ing.get("response", {}).get("chunks") or ing.get("chunks") or []

        # normalize
        norm = mcp_adapter.call_mcp("mcp_collector", "normalize", {"chunks": chunks})
        if norm.get("error"):
            raise HTTPException(status_code=500, detail={"stage": "collector.normalize", "error": norm})
        norm_chunks = norm.get("response", {}).get("chunks") or norm.get("chunks") or norm.get("chunks", [])

        # extract stories
        ext = mcp_adapter.call_mcp("mcp_collector", "extract_stories", {"chunks": norm_chunks})
        if ext.get("error"):
            raise HTTPException(status_code=500, detail={"stage": "collector.extract_stories", "error": ext})
        stories = ext.get("response", {}).get("stories") or ext.get("stories") or []

    # 2) Analyze stories
    anl = mcp_adapter.call_mcp("mcp_analyzer", "analyze_stories", {"stories": stories})
    if anl.get("error"):
        raise HTTPException(status_code=500, detail={"stage": "analyzer.analyze_stories", "error": anl})
    analysis = anl.get("response", {}) or anl

    # 3) Identify requirements
    idr = mcp_adapter.call_mcp("mcp_requirement", "identify_requirements", {"stories": stories, "analysis": analysis})
    if idr.get("error"):
        raise HTTPException(status_code=500, detail={"stage": "requirement.identify_requirements", "error": idr})
    requirements = idr.get("response", {}).get("requirements") or idr.get("requirements") or []

    # 4) Prioritize
    pri = mcp_adapter.call_mcp("mcp_requirement", "prioritize", {"requirements": requirements})
    if pri.get("error"):
        raise HTTPException(status_code=500, detail={"stage": "requirement.prioritize", "error": pri})
    prioritized = pri.get("response", {}) or pri

    # 5) Build report
    rep = mcp_adapter.call_mcp(
        "mcp_reporter",
        "build_final_report",
        {"core_requirements": requirements, "analyzer_output": analysis, "project_id": req.project_id},
    )
    if rep.get("error"):
        raise HTTPException(status_code=500, detail={"stage": "reporter.build_final_report", "error": rep})

    return {
        "ok": True,
        "stories": stories,
        "analysis": analysis,
        "requirements": requirements,
        "prioritized": prioritized,
        "report": rep.get("response") or rep,
    }
