import os
import motor.motor_asyncio
import math
import jinja2
import aiohttp_jinja2
from aiohttp import web

from  utils import get_files_size, get_files_list
from base import get_torrents_count, search_torrents, get_torrent_details, get_last_torrents

try:
    import local
except ImportError:
    pass

results_per_page = int(os.getenv("RESULTS_PER_PAGE", "10"))

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client[os.getenv("MONGODB_BASE_NAME", "grapefruit")]


@aiohttp_jinja2.template("index.html")
async def render_home(request):
    _, torrents_count = await get_torrents_count(db)
    return {"torrents_count": torrents_count}


async def render_latest(request):
    page = int(request.match_info.get("page", "1"))

    elapsed_time, results_count, results = get_last_torrents(
        db,
        fields=["name", "files", "info_hash"],
        limit=results_per_page,
        offset=(min(page, 10) - 1) * results_per_page
    )

    response = await render_results("latest", "", page, results, min(results_count, 100), elapsed_time, request)
    return response


async def render_query(request):
    query = request.match_info["query"]
    page = int(request.match_info.get("page", "1"))

    elapsed_time, results_count, results = search_torrents(
        db,
        query=query,
        fields=["name", "files", "info_hash"],
        limit=results_per_page,
        offset=(page - 1) * results_per_page
    )

    response = await render_results("search", query, page, results, results_count, elapsed_time, request)
    return response


@aiohttp_jinja2.template("details.html")
async def render_torrent(request):
    info_hash = request.match_info["info_hash"]

    _, result = await get_torrent_details(db, info_hash)

    return {
        "query": result["name"],
        "title": result["name"],
        "size": get_files_size(result["files"]),
        "info_hash": result["info_hash"],
        "files": get_files_list(result["files"])
    }


@aiohttp_jinja2.template("results.html")
async def render_results(source_url, query, page, results, results_count, elapsed_time, request):
    return {
        "source_url": source_url,
        "query": query,
        "page": page,
        "total_pages": int(math.ceil(results_count / results_per_page)),
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


app = web.Application(middlewares=[error_middleware])
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("templates"))
app.router.add_static("/static", "static", name="static")
app.router.add_get("/", render_home)
app.router.add_get("/latest", render_latest)
app.router.add_get("/latest/{page}", render_latest)
app.router.add_get("/search/{query}", render_query)
app.router.add_get("/search/{query}/{page}", render_query)
app.router.add_get("/torrent/{info_hash}", render_torrent)

web.run_app(app)
