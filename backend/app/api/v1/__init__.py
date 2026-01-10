"""
API v1 Router
"""
from fastapi import APIRouter

# Import individual routers
from app.api.v1.endpoints import auth, projects, companies, evaluations, ocr, admin

router = APIRouter()

# Include sub-routers
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(projects.router, prefix="/projects", tags=["Projects"])
router.include_router(companies.router, prefix="/companies", tags=["Companies"])
router.include_router(evaluations.router, prefix="/evaluations", tags=["Evaluations"])
router.include_router(ocr.router, prefix="/ocr", tags=["OCR"])
router.include_router(admin.router, prefix="/admin", tags=["Admin"])
