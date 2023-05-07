from sqlalchemy import Column, Integer, String, Date, Boolean, SmallInteger, BigInteger, DateTime, Double, Text, \
    ForeignKey, Float
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column


class Base(DeclarativeBase):
    __abstract__ = True

    @classmethod
    def get_fields(cls, with_pk: bool = False) -> [str]:
        if with_pk:
            fields = [field.name for field in cls.__table__.c]
        else:
            fields = [field.name for field in cls.__table__.c if not field.primary_key]
        return fields


class Msg(Base):
    __tablename__ = 'texts'
    text_name = mapped_column(String(100), primary_key=True)
    text_value = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        return f'text_name="{self.text_name}"; text_value="{self.text_value}"'
