from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import List, Optional
from app.models.tag_model import Tag
from app.schemas.tag_schema import TagCreate, TagUpdate

async def get_tag_by_id(tag_id: int, db: AsyncSession) -> Optional[Tag]:
    """Gets a single tag by its ID."""
    return await db.get(Tag, tag_id)

async def get_tag_by_name(name: str, db: AsyncSession) -> Optional[Tag]:
    """
    Gets a single tag by its unique name.
    This is a crucial helper function for our "get-or-create" logic.
    """
    statement = select(Tag).where(Tag.name == name)
    result = await db.execute(statement)
    return result.scalar_one_or_none()

async def get_all_tags(db: AsyncSession) -> List[Tag]:
    """Gets a list of all tags."""
    statement = select(Tag).order_by(Tag.name) # Order alphabetically
    results = await db.scalars(statement)
    return results.all()

async def create_tag(tag_data: TagCreate, db: AsyncSession) -> Tag:
    """Creates a new tag."""

    new_tag = Tag.model_validate(tag_data)
    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)
    return new_tag

async def update_tag(tag_id: int, tag_data: TagUpdate, db: AsyncSession) -> Optional[Tag]:
    """Updates an existing tag's name."""
    tag = await db.get(Tag, tag_id)
    if not tag:
        return None
    
    update_data = tag_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tag, key, value)
        
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag

async def delete_tag(tag_id: int, db: AsyncSession) -> Optional[Tag]:
    """Deletes a tag."""
    tag = await db.get(Tag, tag_id)
    if not tag:
        return None
        
    await db.delete(tag)
    await db.commit()
    return tag
