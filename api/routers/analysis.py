from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_, desc, asc
from typing import Optional, List
from db.database import get_db
from db.models import Item, Area, ItemPrice

# Create router with prefix and tags
router = APIRouter(
    prefix="/analysis",
    tags=["analysis"],
    responses={404: {"description": "Not found"}},
)
