from sqlalchemy import Column, BigInteger, Integer, String, Date, ForeignKey, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    identifier = Column(BigInteger, primary_key=True)
    role = Column(String(20), nullable=False, default="user")
    money = relationship("Money", back_populates="user", uselist=False)
    daily = relationship("Daily", back_populates="user", uselist=False)
    robbing = relationship("Robbing", back_populates="user", uselist=False)

class Money(Base):
    __tablename__ = "money"
    identifier = Column(BigInteger, ForeignKey("users.identifier", ondelete="CASCADE", onupdate="RESTRICT"), primary_key=True)
    money = Column(Integer, nullable=False, default=1000)
    user = relationship("User", back_populates="money")

class Daily(Base):
    __tablename__ = "daily"
    identifier = Column(BigInteger, ForeignKey("users.identifier", ondelete="CASCADE", onupdate="RESTRICT"), primary_key=True)
    last_daily = Column(Date, nullable=False, default=func.current_date())
    streak = Column(Integer, nullable=False, default=0)
    user = relationship("User", back_populates="daily")

class Robbing(Base):
    __tablename__ = "robbing"
    identifier = Column(BigInteger, ForeignKey("users.identifier", ondelete="CASCADE", onupdate="RESTRICT"), primary_key=True)
    next_robbing = Column(Date, nullable=False, default=func.current_date())
    user = relationship("User", back_populates="robbing")

class Cogs(Base):
    __tablename__ = "cogs"
    identifier = Column(BigInteger, primary_key=True)
    name = Column(String(50), nullable=False)
    enabled = Column(Integer, nullable=False, default=1)  # 1 for enabled, 0 for disabled