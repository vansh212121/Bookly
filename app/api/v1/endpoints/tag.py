from fastapi import APIRouter, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from app.utils.deps import get_session, RoleChecker
from app.models.user_model import UserRole
from app.schemas.tag_schema import TagCreate, TagUpdate, TagResponse
from app.services import tag_service
from app.core.config import settings


router = APIRouter(tags=["Tags"], prefix=f"{settings.API_V1_STR}/tags")
admin_only = Depends(RoleChecker([UserRole.ADMIN]))


@router.get("/tags", response_model=List[TagResponse], dependencies=[admin_only])
async def get_all_tags(db: AsyncSession = Depends(get_session)):
    """
    Get a list of all tags. (Admin only)
    """
    return await tag_service.get_all_tags(db=db)


@router.post(
    "/tags",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[admin_only],
)
async def create_tag(tag_data: TagCreate, db: AsyncSession = Depends(get_session)):
    """
    Create a new tag. (Admin only)
    """
    return await tag_service.create_new_tag(tag_data=tag_data, db=db)


@router.patch("/tags/{tag_id}", response_model=TagResponse, dependencies=[admin_only])
async def update_tag(
    tag_id: int, tag_data: TagUpdate, db: AsyncSession = Depends(get_session)
):
    """
    Update a tag's name. (Admin only)
    """
    return await tag_service.update_a_tag(tag_id=tag_id, tag_data=tag_data, db=db)


@router.delete(
    "/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[admin_only]
)
async def delete_tag(tag_id: int, db: AsyncSession = Depends(get_session)):
    """
    Delete a tag. (Admin only)
    """
    await tag_service.delete_a_tag(tag_id=tag_id, db=db)
    return None
