from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class autoru_item(BaseModel):
    """Схема одного объявления с auto.ru."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")

    name: str = Field(..., max_length=100)
    url: str
    cost: float
    millege: str
    engine_volume: str
    motor_power: str
    fuel_type: str
    body_type: str
    drive_type: str
    gearbox_type: str

    # Опциональные поля
    owners_num: Optional[str] = None
    configuration: Optional[str] = None
    steering_wheel_type: Optional[str] = None
    color: Optional[str] = None
    saler_comment: Optional[str] = None

    parse_city : str
    parse_mark : str
    parse_model : str
    parse_date: date

    @classmethod
    def from_row(cls, row: dict) -> "autoru_item":
        """Безопасный парсинг строки DataFrame с дефолтами."""
        return cls.model_validate({
            "name": row.get("name"),
            "url": row.get("url"),
            "cost": float(row.get("cost") or 0),
            "millege": row.get("millege") or "",
            "engine_volume": row.get("engine_volume") or "",
            "motor_power": row.get("motor_power") or "",
            "fuel_type": row.get("fuel_type") or "",
            "body_type": row.get("body_type") or "",
            "drive_type": row.get("drive_type") or "",
            "gearbox_type": row.get("gearbox_type") or "",
            "owners_num": row.get("owners_num"),
            "configuration": row.get("configuration"),
            "steering_wheel_type": row.get("steering_wheel_type"),
            "color": row.get("color"),
            "saler_comment": row.get("saler_comment"),
            "parse_city": row.get("parse_city"),
            "parse_mark": row.get("parse_mark"),
            "parse_model": row.get("parse_model"),
            "parse_date": row.get("parse_date"),
        })