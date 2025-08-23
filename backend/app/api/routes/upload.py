from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.document_parser import DocumentParser
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize document parser
document_parser = DocumentParser()

@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Upload and parse a single resume
    
    This endpoint:
    1. Validates file format
    2. Extracts text from PDF/Word documents
    3. Extracts basic contact information
    4. Returns parsed content for review
    """
    
    logger.info(f"Processing upload: {file.filename}")
    
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.doc', '.docx')):
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file format. Please upload PDF, DOC, or DOCX files."
            )
        
        # Validate file size
        if not document_parser.validate_file_size(file):
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 10MB."
            )
        
        # Parse document
        parsed_text = await document_parser.parse_document(file)
        
        # Extract contact information
        contact_info = document_parser.extract_contact_info(parsed_text)
        
        # Create preview (first 500 characters)
        text_preview = parsed_text[:500] + "..." if len(parsed_text) > 500 else parsed_text
        
        logger.info(f"Successfully processed {file.filename}")
        
        return {
            "status": "success",
            "filename": file.filename,
            "file_size_kb": len(parsed_text) / 1024,
            "text_length": len(parsed_text),
            "text_preview": text_preview,
            "contact_info": contact_info,
            "message": "Resume parsed successfully. Ready for analysis."
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing file: {str(e)}"
        )

@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported file formats"""
    return {
        "supported_formats": document_parser.supported_formats,
        "max_file_size_mb": 10,
        "description": "Upload PDF, DOC, or DOCX resume files for analysis"
    }