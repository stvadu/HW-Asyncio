import asyncio
import aiohttp
import datetime
from more_itertools import chunked
from models import Base, Session, StarWars, engine, init_db


simple_keys = [
    "name",
    "height",
    "mass",
    "hair_color",
    "skin_color",
    "eye_color",
    "birth_year",
    "gender",
]

complex_keys = {
    "films": "title",
    "species": 'name',
    "homeworld": "name",
    "vehicles": "name",
    "starships": "name",
}
async def get_warrior_data(warrior_id):
    session = aiohttp.ClientSession()
    response = await session.get(f"https://swapi.py4e.com/api/people/{warrior_id}")
    warrior_raw_data = await response.json()
    if response.status == 200:
        result_dict = {key: warrior_raw_data[key] for key in simple_keys}
        for key, value in complex_keys.items():
            if len(warrior_raw_data[key]) == 0 :
                result_str = "-"
            else:
                result_str = await get_warrior_data_by_link(value, warrior_raw_data[key])
            result_dict[key] = result_str
    else:
        result_dict = {key: "-" for key in simple_keys}
        result_dict = result_dict | {key: "-" for key, value in complex_keys.items()}
    await session.close()
    await engine.dispose()
    return result_dict

async def get_warrior_data_by_link(key, raw_data):
    client = aiohttp.ClientSession()
    if type(raw_data) is str:
        raw_data = [raw_data]
    result_list = [await client.get(record) for record in raw_data]
    result_json_list = []
    for record in result_list:
        result_json_list.append(await record.json())


    result = "' ".join([record[key] for record in result_json_list])
    await client.close()
    return result


async def add_warriors(warriors_list_json, warrior_id):
    warriors_list = [
        StarWars(
            warrior_id=warrior_id + i + 1,
            birth_year=warrior["birth_year"],
            eye_color=warrior["eye_color"],
            hair_color=warrior["hair_color"],
            films=warrior["films"],
            gender=warrior["gender"],
            height=warrior["height"],
            homeworld=warrior["homeworld"],
            mass=warrior["mass"],
            name=warrior["name"],
            skin_color=warrior["skin_color"],
            species=warrior["species"],
            starships=warrior["starships"],
            vehicles=warrior["vehicles"],
        )
        for i, warrior in enumerate(warriors_list_json)
    ]
    async with Session() as session:
        session.add_all(warriors_list)
        await session.commit()

async def main():
    await init_db()
    counter = 0
    for warrior_ids_chunk in chunked(range(1, 10), 5):
        print("loading...")
        warrior_coros = [get_warrior_data(warrior_id) for warrior_id in warrior_ids_chunk]
        warriors = await asyncio.gather(*warrior_coros)
        insert_warrior_coro = add_warriors(warriors, warrior_ids_chunk[0])
        asyncio.create_task(insert_warrior_coro)
        print(f"{warrior_ids_chunk} were added")
    task = asyncio.current_task()
    tasks = asyncio.all_tasks()
    tasks.remove(task)
    await asyncio.gather(*tasks)
    print("Done!")


if __name__ == "__main__":
    start = datetime.datetime.now()
    asyncio.run(main())
    print(f"Time spent: {datetime.datetime.now() - start} ")