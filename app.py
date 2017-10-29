import os
import motor.motor_asyncio
import math
import jinja2
import asyncio
import aiohttp_jinja2
from aiohttp import web

from  utils import get_files_size, get_files_list
from base import create_indexes, get_torrents_count, search_torrents, get_torrent_details, get_last_torrents

try:
    import local
except ImportError:
    pass

RESULTS_PER_PAGE = 10


@aiohttp_jinja2.template("index.html")
async def render_home(db, request):
    _, torrents_count = await get_torrents_count(db)
    return {"torrents_count": torrents_count}


async def render_latest(db, request):
    page = int(request.match_info.get("page", "1"))

    elapsed_time, (results_count, results) = await get_last_torrents(
        db, ["name", "files", "info_hash"], (min(page, 10) - 1) * RESULTS_PER_PAGE, RESULTS_PER_PAGE
    )

    response = await render_results("/latest", "", page, results, min(results_count, 100), elapsed_time, request)
    return response


async def render_query(db, request):
    query = request.match_info.get("query", None)
    page = int(request.match_info.get("page", "1"))

    if query:
        elapsed_time, (results_count, results) = await search_torrents(
            db, query, ["name", "files", "info_hash"], (page - 1) * RESULTS_PER_PAGE, RESULTS_PER_PAGE
        )

        response = await render_results("/search", query, page, results, results_count, elapsed_time, request)
        return response
    elif request.query.get("q", None):
        url = "/search/{0}".format(request.query["q"])
        return web.HTTPFound(url)
    else:
        return web.HTTPFound("/")


@aiohttp_jinja2.template("details.html")
async def render_torrent(db, request):
    info_hash = request.match_info.get("info_hash", None)

    if info_hash:
        _, result = await get_torrent_details(db, info_hash)

        return {
            "query": result["name"],
            "title": result["name"],
            "size": get_files_size(result["files"]),
            "info_hash": result["info_hash"],
            "files": get_files_list(result["files"])
        }
    else:
        return web.HTTPFound("/")


@aiohttp_jinja2.template("results.html")
async def render_results(source_url, query, page, results, results_count, elapsed_time, request):
    return {
        "source_url": source_url,
        "query": query,
        "page": page,
        "total_pages": int(math.ceil(results_count / RESULTS_PER_PAGE)),
        "total_count": results_count,
        "time_elapsed": round(elapsed_time, 3),
        "results": map(lambda item: {
            "info_hash": item["info_hash"],
            "title": item["name"],
            "size": get_files_size(item["files"]),
            "files": get_files_list(item["files"], first_ten=True),
            "files_count": len(item["files"])
        }, results)
    }


@aiohttp_jinja2.template("error.html")
async def render_error(error_code, request):
    return {"error_code": error_code}


async def error_middleware(app, handler):
    async def middleware_handler(request):
        try:
            response = await handler(request)
            return response
        except web.HTTPException as ex:
            if ex.status in [403, 404, 500]:
                response = await render_error(ex.status, request)
                return response
            else:
                raise
        except Exception:
            response = await render_error(500, request)
            return response

    return middleware_handler


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
    db = client[os.getenv("MONGODB_BASE_NAME", "grapefruit")]

    loop.run_until_complete(create_indexes(db))

    app = web.Application(middlewares=[error_middleware])
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("templates"))

    app.router.add_static("/static", "static", name="static")
    app.router.add_get("/", lambda request: render_home(db, request))
    app.router.add_get("/latest", lambda request: render_latest(db, request))
    app.router.add_get("/latest/{page}", lambda request: render_latest(db, request))
    app.router.add_get("/search", lambda request: render_query(db, request))
    app.router.add_get("/search/{query}", lambda request: render_query(db, request))
    app.router.add_get("/search/{query}/{page}", lambda request: render_query(db, request))
    app.router.add_get("/torrent/{info_hash}", lambda request: render_torrent(db, request))

    web.run_app(app, host="0.0.0.0", loop=loop)
