"""
API Endpoints for Bangladesh Inland Vessel Statutory Code & Reference Library.
"""

import os
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, Response
from fastapi.responses import JSONResponse, FileResponse

from app.services.statutory_service import StatutoryService

router = APIRouter(prefix="/library", tags=["library"])
service = StatutoryService()

PDF_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'assets', 'docs', 'Prevention_of_Inland_Vessel_Accidents_Laws_and_Rules_EN.pdf'
)


@router.get("/books")
async def get_all_books():
    """
    Returns metadata and rule counts for all 13 statutory books.
    """
    overview = service.get_library_overview()
    return JSONResponse(content=overview)


@router.get("/book/{book_id}")
async def get_book(book_id: int):
    """
    Returns chapters and rules for a specific book.
    """
    details = service.get_book_details(book_id)
    if not details:
        raise HTTPException(status_code=404, detail=f"Book ID {book_id} not found")
    return JSONResponse(content=details)


@router.get("/rule/{rule_id}")
async def get_rule(rule_id: int):
    """
    Returns full content, HTML formatting, and PDF page number for a rule.
    """
    rule = service.get_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule ID {rule_id} not found")
    return JSONResponse(content=rule)


@router.get("/search")
async def search_library(
    q: str = Query(..., min_length=1, description="Search term, Rule number, keyword, or member"),
    book_id: Optional[int] = Query(None, description="Optional book ID filter"),
    limit: int = Query(40, ge=1, le=100)
):
    """
    Full-text and exact match search across all 13 statutory books.
    """
    res = service.search_rules(query=q, book_id=book_id, limit=limit)
    return JSONResponse(content=res)


@router.get("/pdf")
async def get_statutory_pdf():
    """
    Streams the official 201-page English statutory volume PDF for inline viewing and sync.
    """
    if not os.path.exists(PDF_PATH):
        raise HTTPException(status_code=404, detail="Statutory PDF file not found on server")

    return FileResponse(
        path=PDF_PATH,
        media_type="application/pdf",
        filename="Prevention_of_Inland_Vessel_Accidents_Laws_and_Rules_EN.pdf",
        headers={
            "Content-Disposition": "inline; filename=\"Prevention_of_Inland_Vessel_Accidents_Laws_and_Rules_EN.pdf\"",
            "Accept-Ranges": "bytes"
        }
    )
