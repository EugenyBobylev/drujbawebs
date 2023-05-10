from sqlalchemy import Integer, String, Date, BigInteger, Text, ForeignKey, Time
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
    """
    Telegram user in the bot
    """
    __tablename__: str = 'users'

    id = mapped_column(BigInteger, primary_key=True, autoincrement=False)  # this is the telegram id
    name = mapped_column(String)
    birthdate = mapped_column(Date)
    timezone = mapped_column(Integer)

    accounts = relationship('Account', back_populates='owner')

    def __repr__(self) -> str:
        return f'tgid={self.id}; name="{self.name}"; timezone={self.timezone}'


class Company(Base):
    """
    Company
    """
    __tablename__: str = 'companies'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id = mapped_column(Integer, ForeignKey('accounts.id', ondelete='CASCADE'), nullable=False)  # администратор
    name = mapped_column(String, nullable=False, unique=True)        # название компании
    industry = mapped_column(String, default='')        # сфера деятельности
    person_count = mapped_column(Integer, default=0)    # количество человек в компании

    admin = relationship('Account', foreign_keys=[account_id], uselist=False)

    def __repr__(self) -> str:
        return f'id={self.id}; name="{self.name}"'


class Account(Base):
    """
    Account of the telegram user in the bot
    """
    __tablename__: str = 'accounts'

    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    company_id = mapped_column(Integer, ForeignKey('companies.id', ondelete='CASCADE'), unique=True)
    payed_events = mapped_column(Integer, default=0)
    job_title = mapped_column(String, default='')
    phone = mapped_column(String, default='')
    email = mapped_column(String, default='')

    owner = relationship('User', foreign_keys=[user_id], back_populates='accounts', uselist=False)
    company = relationship('Company', foreign_keys=[company_id], uselist=False)
    fundraisings = relationship('Fundraising')
    donors = relationship('Donor')

    def __repr__(self) -> str:
        return f'id={self.id}; user_id={self.user_id}; company_id={self.company_id}'


class Donor(Base):
    __tablename__: str = 'donors'
    event_id = mapped_column(Integer, ForeignKey('fundraising.id', ondelete='CASCADE'), primary_key=True)
    account_id = mapped_column(Integer, ForeignKey('accounts.id', ondelete='CASCADE'), primary_key=True)
    payed = mapped_column(Integer, nullable=False, default=0)

    account = relationship('Account', foreign_keys=[account_id], back_populates='donors')
    fundraising = relationship('Fundraising', foreign_keys=[event_id], back_populates='donors')


class Fundraising(Base):
    """
    Сбор средств (на подарок, на ресторан и т.д.)
    """
    __tablename__: str = 'fundraising'

    id = mapped_column(Integer, primary_key=True)
    reason = mapped_column(String, nullable=False)      # основание для сбора (ДР, юбилей, свадьба, 8-е марта)
    target = mapped_column(String, nullable=False)      # кому собираем
    account_id = mapped_column(ForeignKey("accounts.id", ondelete='cascade'), nullable=False)
    start = mapped_column(Date)                         # дата регистрации сбора
    end = mapped_column(Date)                           # дата окончания сбора
    event_date = mapped_column(Date, nullable=False)    # дата события
    transfer_info = mapped_column(String, nullable=False)   # реквизиты перевода (номер карты или телефон)
    gift_info = mapped_column(Text, default='')         # варианты подарков
    congratulation_date = mapped_column(Date)           # дата праздничного мероприятия
    congratulation_time = mapped_column(Time)           # время праздничного мероприятия
    event_place = mapped_column(String, default='')     # место проведения мероприятия
    event_dresscode = mapped_column(String, default='')  # дресс-код
    invite_url = mapped_column(String, nullable=False, default='')  # ссылка приглашения для участия в сборе

    owner = relationship('Account', back_populates='fundraisings')  # лицо ответственное за сбор
    donors = relationship('Donor')

    def __repr__(self) -> str:
        return f'id={self.id}; reason="{self.reason}"; target="{self.target}"; ' \
               f'campaign_start={self.start.strftime("%d.%m.%Y")}; ' \
               f'campaign_end={self.end.strftime("%d.%m.%Y")};' \
               f'account_id={self.account_id}'


class Msg(Base):
    __tablename__ = 'texts'
    text_name = mapped_column(String(100), primary_key=True)
    text_value = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        return f'text_name="{self.text_name}"; text_value="{self.text_value}"'
