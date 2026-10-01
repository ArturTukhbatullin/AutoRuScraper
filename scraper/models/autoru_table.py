from datetime import date
from typing import Optional
from sqlalchemy import String, Numeric, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class autoru_table(Base):
    __tablename__ = "autoru_data"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    url: Mapped[str]
    cost: Mapped[float] = mapped_column(Numeric(20, 2, asdecimal=False))
    millege: Mapped[str]
    engine_volume: Mapped[str]
    motor_power: Mapped[str]
    fuel_type: Mapped[str]
    body_type: Mapped[str]
    drive_type: Mapped[str]
    gearbox_type: Mapped[str]
    owners_num: Mapped[Optional[str]]
    configuration: Mapped[Optional[str]]
    steering_wheel_type: Mapped[Optional[str]]
    color: Mapped[Optional[str]]
    saler_comment: Mapped[Optional[str]]
    parse_city : Mapped[str]
    parse_mark : Mapped[str]
    parse_model : Mapped[str]
    parse_date: Mapped[date] = mapped_column(Date())

    @classmethod
    def from_pydantic(cls, item: "autoru_item") -> "autoru_table":
        return cls(**item.model_dump())