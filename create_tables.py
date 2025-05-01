# create_tables.py
from db.base import engine, Base
from models import Users, Rooms, Friends, Tokens  # Явный импорт всех моделей!
import asyncio
from datetime import *
import time
async def drop_tables():
    async with engine.begin() as conn:
        print("🗑️ Удаляем все таблицы...")
        await conn.run_sync(Base.metadata.drop_all)
    print("✅ Все таблицы успешно удалены!")

async def create_tables():
    async with engine.begin() as conn:
        print("🔄 Создаем таблицы...")
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Все таблицы успешно созданы!")

if __name__ == "__main__":
    # print("1. Удаление таблиц")
    # asyncio.run(drop_tables())
    print("\n2. Создание таблиц")
    asyncio.run(create_tables())


# python create_tables.py
# # Таблицы созданы без ошибок.

# exec -it music_flow_db psql -U vasya -d bd -c "\dt"
#            List of relations
#  Schema |   Name    | Type  | Owner 
# --------+-----------+-------+-------
#  public | friends   | table | vasya
#  public | rooms     | table | vasya
#  public | tokens    | table | vasya
#  public | users     | table | vasya
# (4 rows)
# create_tables.py
# from sqlalchemy import create_engine
# from db.base import Base
# from models import Users, Rooms, Friends, Tokens

# print('123')
# def create_all_tables():
#     engine = create_engine("postgresql+psycopg2://postgres:123@localhost:5432/postgres")
#     Base.metadata.create_all(engine)
#     print("Таблицы созданы!")


# if __name__ == "__main__":
#     create_all_tables()
