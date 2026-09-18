from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="File Vault",
    description="Безопасная передача файлов и текста по временным ссылкам.",
    version="0.1.0",
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", tags=["Pages"])
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.get("/create", tags=["Pages"])
async def create_secret(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="create.html",
    )


@app.get("/secret/test", tags=["Pages"])
async def test_secret(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="secret.html",
    )


@app.get("/destroyed", tags=["Pages"])
async def destroyed(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="destroyed.html",
    )


@app.get("/api/health", tags=["System"])
async def health_check():
    return {
        "status": "ok",
        "service": "file-vault",
        "version": "0.1.0",
    }
