from pymongo import DESCENDING
from utils import async_timing


@async_timing
async def search_torrents(db, query, fields, offset=0, limit=0):
    assert isinstance(fields, list)

    projection = {"score": {"$meta": "textScore"}, "_id": False}

    for field in fields:
        projection[field] = True

    cursor = await db.torrents.find(
        filter={"$text": {"$search": query}},
        projection=projection,
        sort=[("score", {"$meta": "textScore"}), ("timestamp", DESCENDING)]
    )

    if cursor:
        results_count, results = cursor.count(), list(cursor.skip(offset).limit(limit))
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

    cursor = await db.torrents.find(
        filter={},
        projection=projection,
        sort=[("timestamp", DESCENDING)]
    )

    if cursor:
        results_count, results = min(cursor.count(), 100), list(cursor.skip(offset).limit(limit))
    else:
        results_count, results = 0, []

    return results_count, results


@async_timing
async def get_torrents_count(db):
    result = await db.torrents.count()
    return result
