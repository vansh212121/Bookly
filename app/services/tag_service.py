# from sqlmodel.ext.asyncio.session import AsyncSession
# from typing import List
# from app.crud import tag_crud
# from app.schemas.tag_schema import TagCreate, TagUpdate
# from app.models.tag_model import Tag
# from app.core.exceptions import TagAlreadyExists, TagNotFound


# async def get_all_tags(db: AsyncSession) -> List[Tag]:
#     """Service to get a list of all tags."""
#     return await tag_crud.get_all_tags(db=db)


# async def create_new_tag(tag_data: TagCreate, db: AsyncSession) -> Tag:
#     """Service to create a new tag."""
#     # Check if a tag with this name already exists to prevent duplicates
#     existing_tag = await tag_crud.get_tag_by_name(name=tag_data.name, db=db)
#     if existing_tag:
#         raise TagAlreadyExists("A tag with this name already exists.")

#     return await tag_crud.create_tag(tag_data=tag_data, db=db)


# async def update_a_tag(tag_id: int, tag_data: TagUpdate, db: AsyncSession) -> Tag:
#     """Service to update a tag."""
#     tag_to_update = await tag_crud.update_tag(tag_id=tag_id, tag_data=tag_data, db=db)
#     if not tag_to_update:
#         raise TagNotFound("Tag not found")
#     return tag_to_update


# async def delete_a_tag(tag_id: int, db: AsyncSession) -> None:
#     """Service to delete a tag."""
#     tag_to_delete = await tag_crud.delete_tag(tag_id=tag_id, db=db)
#     if not tag_to_delete:
#         raise TagNotFound("Tag not found")
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from app.crud import tag_crud
from app.schemas.tag_schema import TagCreate, TagUpdate
from app.models.tag_model import Tag
from app.core.exceptions import TagAlreadyExists, TagNotFound

async def get_all_tags(db: AsyncSession) -> List[Tag]:
    """Service to get a list of all tags."""
    return await tag_crud.get_all_tags(db=db)

async def create_new_tag(tag_data: TagCreate, db: AsyncSession) -> Tag:
    """Service to create a new tag, ensuring it's unique."""
    # Normalize the name to prevent duplicates like "Fantasy" and "fantasy"
    normalized_name = tag_data.name.strip().lower()
    
    existing_tag = await tag_crud.get_tag_by_name(name=normalized_name, db=db)
    if existing_tag:
        raise TagAlreadyExists(f"A tag with the name '{normalized_name}' already exists.")
    
    # Create a new TagCreate object with the normalized name to be safe
    normalized_tag_data = TagCreate(name=normalized_name)
    return await tag_crud.create_tag(tag_data=normalized_tag_data, db=db)

async def update_a_tag(tag_id: int, tag_data: TagUpdate, db: AsyncSession) -> Tag:
    """Service to update a tag."""
    tag_to_update = await tag_crud.get_tag_by_id(tag_id=tag_id, db=db)
    if not tag_to_update:
        raise TagNotFound(f"Tag not found")
    
    # Optional: Normalize the updated name if it's provided
    if tag_data.name is not None:
        tag_data.name = tag_data.name.strip().lower()

    return await tag_crud.update_tag(tag_id=tag_id, tag_data=tag_data, db=db)

async def delete_a_tag(tag_id: int, db: AsyncSession) -> None:
    """Service to delete a tag."""
    tag_to_delete = await tag_crud.get_tag_by_id(tag_id=tag_id, db=db)
    if not tag_to_delete:
        raise TagNotFound(f"Tag not found")
        
    await tag_crud.delete_tag(tag_id=tag_id, db=db)
