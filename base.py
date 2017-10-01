from pymongo import ASCENDING, TEXT, DESCENDING
from utils import async_timing


async def create_indexes(db):
    torrents = db.torrents
    torrents_indexes = await torrents.index_information()

    for index_info in ({"name": "fulltext", "keys": [("name", TEXT),
                                                     ("info_hash", TEXT),
                                                     ("files.path", TEXT)],
                        "weights": {"name": 99999, "info_hash": 99999, "files.path": 1},
                        "default_language": "english"},
                       {"name": "info_hash", "keys": [("info_hash", ASCENDING)], "unique": True},
                       {"name": "access_count", "keys": [("access_count", ASCENDING)]},
                       {"name": "timestamp", "keys": [("timestamp", DESCENDING)]}):
        if index_info["name"] not in torrents_indexes:
            await torrents.create_index(**index_info)


@async_timing
async def search_torrents(db, query, fields, offset=0, limit=0):
    assert isinstance(fields, list)

    projection = {"score": {"$meta": "textScore"}, "_id": False}

    for field in fields:
        projection[field] = True

    cursor = db.torrents.find(
        filter={"$text": {"$search": query}},
        projection=projection,
        sort=[("score", {"$meta": "textScore"}), ("timestamp", DESCENDING)]
    )

    if cursor:
        results_count = await cursor.count()
        results = await cursor.skip(offset).limit(limit).to_list(None)
    else:
        results_count, results = 0, []

    return results_count, results


@async_timing
async def get_torrent_details(db, info_hash):
    result = await db.torrents.find_one(
        filter={"info_hash": info_hash},
        projection={
            "_id": False,
            "name": True,
            "files": True,
            "info_hash": True
        }
    )

    return result


@async_timing
async def get_last_torrents(db, fields, offset=0, limit=100):
    projection = {"_id": False}
    projection.update({field: True for field in fields})

    cursor = db.torrents.find(
        filter={},
        projection=projection,
        sort=[("timestamp", DESCENDING)]
    )

    if cursor:
        results_count = min(await cursor.count(), 100)
        results = await cursor.skip(offset).limit(limit).to_list(None)
    else:
        results_count, results = 0, []

    return results_count, results


@async_timing
async def get_torrents_count(db):
    result = await db.torrents.count()
    return result
