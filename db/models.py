from sqlalchemy import Column, Integer, String, Date, Boolean, SmallInteger, BigInteger, DateTime, Double, Text, \
    ForeignKey, Float, Time, Numeric
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
    birthdate = mapped_column(Date)
    timezone = mapped_column(Integer)
    payed_events = mapped_column(Integer, default=1)

    owner_companies = relationship('Company', back_populates='owner')      # компании в которых я админ
    member_companies = relationship('UserCompany', back_populates='user')  # компании в которых я сотрудник
    fundraisings = relationship('Fundraising', back_populates='owner')  # сборы где я ответственное лицо

    def __repr__(self) -> str:
        return f'tgid={self.id}; name="{self.name}"; timezone={self.timezone}; payed_vents={self.payed_events}'


class UserCompany(Base):
    """
    Additional information about the company employee
    """
    __tablename__: str = 'usercompany'
    user_id = mapped_column(BigInteger, ForeignKey("users.id"), primary_key=True)
    company_id = mapped_column(Integer, ForeignKey("companies.id"), primary_key=True)
    job = mapped_column(String, default='')     # должность
    phone = mapped_column(String, default='')   # телефон
    email = mapped_column(String, default='')   # электронная почта

    user = relationship('User', back_populates='user_companies')
    company = relationship('Company', back_populates='company_users')


class Company(Base):
    """
    Company
    """
    __tablename__: str = 'companies'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String, nullable=False)        # название компании
    industry = mapped_column(String, default='')        # сфера деятельности
    person_count = mapped_column(Integer, default=0)    # количество человек в компании
    payed_events = mapped_column(Integer, default=0, nullable=False)  # количество оплаченных сборов
    owner_id = mapped_column(ForeignKey("users.id"))    # ответственный за сбор
    owner = relationship('User', back_populates='owner_companies')
    company_users = relationship('UserCompany', back_populates='company')

    def __repr__(self) -> str:
        return f'id={self.id}; name="{self.name}"; barnch="{self.branch}"; ' \
               f'payed_events={self.payed_events}; owner_id={self.owner_id}'


class Fundraising(Base):
    """
    Сбор средств (на подарок, на ресторан и т.д.)
    """
    __tablename__: str = 'fundrasing'

    id = mapped_column(Integer, primary_key=True)
    reason = mapped_column(String, default='')          # основание для сбора (ДР, юбилей, свадьба, 8-е марта)
    target = mapped_column(String, nullable=False)      # кому собираем
    owner_id = mapped_column(ForeignKey("users.id"), nullable=False)  # лицо ответственное за сбор
    owner = relationship('User')                                      # лицо ответственное за сбор
    start = mapped_column(Date, nullable=False)         # дата регистрации сбора
    end = mapped_column(Date, nullable=False)           # дата окончания сбора
    event_date = mapped_column(Date, nullable=False)    # дата события
    transfer_info = mapped_column(Text)                 # реквизиты перевода (номер карты или телефон)
    gift_info = mapped_column(Text)                     # варианты подарков
    congratulation_date = mapped_column(Date)           # дата праздничного мероприятия
    congratulation_time = mapped_column(Time)           # время праздничного мероприятия
    event_place = mapped_column(Text)                   # место проведения мероприятия
    event_dresscode = mapped_column(Text)               # дресс-код
    invite_url = mapped_column(String, nullable=False, default='')  # ссылка приглашения для участия в сборе

    def __repr__(self) -> str:
        return f'id={self.id}; reason="{self.reason}"; target="{self.target}"; ' \
               f'campaign_start={self.start.strftime("%d.%m.%Y")}; ' \
               f'campaign_end={self.end.strftime("%d.%m.%Y")};' \
               f'owner_id={self.owner_id}'


class Member(Base):
    fundrasing_id = mapped_column(Integer, ForeignKey("fundrasing.id"), primary_key=True)  # код сбора
    user_id = mapped_column(BigInteger, ForeignKey("users.id"), primary_key=True)  # телеграм id пользователя
    User = relationship('User', back_populates="members")
    transfer_sum = mapped_column(Numeric, nullable=False, default=0)  # сумма взноса
    transfer_date = mapped_column(Date)  # дата взноса


class Msg(Base):
    __tablename__ = 'texts'
    text_name = mapped_column(String(100), primary_key=True)
    text_value = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        return f'text_name="{self.text_name}"; text_value="{self.text_value}"'
