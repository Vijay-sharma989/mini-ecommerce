from app.database.connection import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, ForeignKey, Boolean, DateTime, Numeric, CheckConstraint
from app.models.category import Category
from app.models.user import User
from datetime import datetime, timezone
from decimal import Decimal


class Product(Base):
    __tablename__="products"

    __table_args__=(
        CheckConstraint(
            "stock >= 0",
            name="check_product_stock_non_negative"
        ),
        CheckConstraint(
            "price >= 0",
            name="check_product_price_non_negative"
        )
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    category : Mapped["Category"] = relationship("Category") 
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    seller: Mapped["User"] = relationship("User")
    price: Mapped[Decimal] = mapped_column(Numeric(10,2), nullable=False)
    stock: Mapped[int] = mapped_column(default=0, nullable=False)
    image_url: Mapped[str|None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default= lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
