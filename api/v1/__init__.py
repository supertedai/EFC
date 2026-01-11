from fastapi import APIRouter

# Import sub-routers
from .concept import router as concept_router
from .methodology import router as methodology_router
from .meta.meta_api import router as meta_router

# Create main router
router = APIRouter()

# Include namespaced routers
router.include_router(concept_router, prefix="/concept", tags=["concept"])
router.include_router(methodology_router, prefix="/methodology", tags=["methodology"])
router.include_router(meta_router, prefix="/meta", tags=["meta"])
