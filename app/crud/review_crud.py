from sqlmodel.ext.asyncio.session import AsyncSession
from app.schemas.review_schema import ReviewUpdate
from app.models.review_model import Review
from typing import Optional, List
from sqlmodel import select


async def get_all_reviews(db: AsyncSession) -> List[Review]:
    statement = select(Review)
    result = await db.scalars(statement)
    return result.all()


async def get_review_by_id(db: AsyncSession, review_id: int) -> Optional[Review]:
    return await db.get(Review, review_id)


async def create_review(db: AsyncSession, review: Review) -> Review:
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review


async def update_review(
    review_id: int, db: AsyncSession, review_data: ReviewUpdate
) -> Optional[Review]:
    db_review = await db.get(Review, review_id)
    if not db_review:
        return None

    updated_data = review_data.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(db_review, key, value)

    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    return db_review


async def delete_review(review_id: int, db: AsyncSession) -> Optional[Review]:
    review_to_delete = await db.get(Review, review_id)
    if not review_to_delete:
        return None

    await db.delete(review_to_delete)
    await db.commit()
    return review_to_delete
