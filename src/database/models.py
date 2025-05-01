from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())


class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True,
                                    auto_increment=True)
    tg_id: Mapped[int] = mapped_column(BigInteger,
                                       nullable=True,
                                       unique=True)
    bx_id: Mapped[int] = mapped_column(BigInteger,
                                       nullable=False,
                                       unique=True)
    access_token: Mapped[str] = mapped_column(String,
                                              nullable=False,
                                              unique=True)
    refresh_token: Mapped[str] = mapped_column(String,
                                               nullable=False,
                                               unique=True)
