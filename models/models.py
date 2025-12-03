import os
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    Text,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy import create_engine

# ---------------------------------------------------------------------------
# SQLAlchemy session / engine setup
# ---------------------------------------------------------------------------
DATABASE_URL = os.environ.get("GAMEON_DATABASE_URL", "sqlite:///gameon.db")

_engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    # Needed so the same connection can be shared across threads in dev server
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **_engine_kwargs)
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))


def get_session():
    """Return a scoped session (thread-local)."""
    return SessionLocal()


class BaseModel(object):
    """Lightweight mixin to mimic previous NDB-style helpers."""

    @classmethod
    def query(cls, session=None):
        session = session or get_session()
        return session.query(cls)

    @classmethod
    def byId(cls, entity_id, session=None):
        session = session or get_session()
        return session.get(cls, entity_id)

    def put(self, session=None):
        session = session or get_session()
        session.add(self)
        session.commit()
        session.refresh(self)
        return self

    def to_dict(self):
        data = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            data[column.name] = value
        return data


Base = declarative_base(cls=BaseModel)

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
    def by_external_id(cls, external_id, session=None):
        # convenience alias with pythonic name
        return cls.byExternalId(external_id, session=session)

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


# Create tables on import for simple deployments (SQLite/local dev).
# In production, migrations should manage schema.
Base.metadata.create_all(engine)
