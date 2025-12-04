import os
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, Table, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from datetime import datetime

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///gameon.db')
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
ScopedSession = scoped_session(SessionLocal)

def get_session():
    return ScopedSession()

Base = declarative_base()

class Score(Base):
    __tablename__ = 'scores'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    time = Column(DateTime, default=datetime.utcnow)
    score = Column(Integer, default=0)
    game_mode = Column(Integer, default=0)

    user = relationship("User", back_populates="scores")

class Achievement(Base):
    __tablename__ = 'achievements'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    time = Column(DateTime, default=datetime.utcnow)
    type = Column(Integer)

    user = relationship("User", back_populates="achievements")

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    external_id = Column(String, unique=True, nullable=False, index=True)
    cookie_user = Column(Integer)
    name = Column(String)
    email = Column(String)

    gold = Column(Integer, default=0)
    mute = Column(Integer, default=0)
    volume = Column(Float, default=0.5)

    levels_unlocked = Column(Integer, default=0)
    difficulties_unlocked = Column(Integer, default=0)

    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    profile_url = Column(String)
    access_token = Column(String)

    scores = relationship("Score", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="user", cascade="all, delete-orphan")

    @classmethod
    def byExternalId(cls, external_id, session=None):
        session = session or get_session()
        return session.query(cls).filter(cls.external_id == external_id).first()

    @classmethod
    def buyFor(cls, external_id, session=None):
        session = session or get_session()
        user = cls.byExternalId(external_id, session=session)
        if user:
            user.gold = 1
            session.commit()

    @classmethod
    def byToken(cls, token, session=None):
        session = session or get_session()
        return session.query(cls).filter(cls.access_token == token).first()

class Postback(Base):
    __tablename__ = 'postbacks'

    id = Column(Integer, primary_key=True)
    jwtPostback = Column(Text)
    orderId = Column(String)
    price = Column(String)
    currencyCode = Column(String)
    time = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)
