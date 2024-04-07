import os

from sqlalchemy import JSON, Column, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

USER_POSTGRES = os.getenv("USER_POSTGRES", "postgres")
PASSWORD_POSTGRES = os.getenv("PASSWORD_POSTGRES", "Nervnii39")
DB_POSTGRES = os.getenv("DB_POSTGRES", "async")
PORT_POSTGRES = os.getenv("PG_PORT", "5431")
HOST_POSTGRES = os.getenv("PG_HOST", "127.0.0.1")


DSN = f"postgresql+asyncpg://{USER_POSTGRES}:{PASSWORD_POSTGRES}@{HOST_POSTGRES}:{PORT_POSTGRES}/{DB_POSTGRES}"

engine = create_async_engine(DSN)

Session = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase, AsyncAttrs):
    pass

class StarWars(Base):

    __tablename__ = "StarWarriors"

    id = Column(Integer, primary_key=True)
    warrior_id = Column(Integer)
    birth_year = Column(String)
    eye_color = Column(String)
    hair_color = Column(String)
    films = Column(String)
    gender = Column(String)
    height = Column(String)
    homeworld = Column(String)
    mass = Column(String)
    name = Column(String)
    skin_color = Column(String)
    species = Column(String)
    starships = Column(String)
    vehicles = Column(String)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)