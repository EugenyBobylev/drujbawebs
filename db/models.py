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


class User(Base):
    __tablename__: str = 'users'

    id = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    name = mapped_column(String)
    dob = mapped_column(Date)
    timezone = mapped_column(Integer)
    payed_events = mapped_column(Integer, default=1)
    companies = relationship('Company', back_populates='owner')
    events = relationship('Event', back_populates='owner')

    def __repr__(self) -> str:
        return f'tgid={self.id}; name="{self.name}"; timezone={self.timezone}; payed_vents={self.payed_events}'


class Company(Base):
    __tablename__: str = 'companies'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String, nullable=False)
    branch = mapped_column(String)
    payed_events = mapped_column(Integer, default=0, nullable=False)
    owner_id = mapped_column(ForeignKey("users.id"))
    owner = relationship('User', back_populates='companies')

    def __repr__(self) -> str:
        return f'id={self.id}; name="{self.name}"; barnch="{self.branch}"; ' \
               f'payed_events={self.payed_events}; owner_id={self.owner_id}'


class Event(Base):
    __tablename__: str = 'events'

    id = mapped_column(Integer, primary_key=True)
    type = mapped_column(String)
    target = mapped_column(String, nullable=False)
    owner_id = mapped_column(ForeignKey("users.id"), nullable=False)
    owner = relationship('User')
    campaign_start = mapped_column(DateTime, nullable=False)
    campaign_end = mapped_column(DateTime, nullable=False)
    closed = mapped_column(Boolean, default=False, nullable=False)
    event_bank = mapped_column(Double, default=0)
    recieve_link = mapped_column(Text)
    event_info = mapped_column(Boolean, default=False)
    event_datetime = mapped_column(DateTime)
    event_place = mapped_column(Text)
    event_dresscode = mapped_column(Text)
    gifts_example = mapped_column(Text)
    payed = mapped_column(Boolean, default=False, nullable=False)
    # participants_info json,
    # participants bigint[]

    def __repr__(self) -> str:
        return f'id={self.id}; type="{self.type}"; target="{self.target}"; ' \
               f'campaign_start={self.campaign_start.strftime("%d.%m.%Y")}; ' \
               f'campaign_end={self.campaign_end.strftime("%d.%m.%Y")};' \
               f'closed={self.closed}; payed={self.payed}; owner_id={self.owner_id}'


class Msg(Base):
    __tablename__ = 'texts'
    text_name = mapped_column(String(100), primary_key=True)
    text_value = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        return f'text_name="{self.text_name}"; text_value="{self.text_value}"'
