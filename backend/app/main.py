# -*- coding: utf-8 -*-
# !/usr/bin/python3

import zipfile
from io import BytesIO
from typing import Iterator

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from playwright.sync_api import sync_playwright

from app.logger import Logger
from app.google_image_downloader import GoogleImageDownloader

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to GoogleImageDownloader API"}


downloader = GoogleImageDownloader(
    output_path=None,
    proxy=None,
    headless=True,
)


def call_downloader(
    search_string: str, limit: int = -1, proxy_server: str = None
) -> Iterator[bytes]:
    downloader.proxy_server = proxy_server
    try:
        with sync_playwright() as plwght:
            downloader.set_new_playwright(plwght)
            images = downloader.process(search=search_string, limit=limit)
            if images:
                for image in images:
                    yield image
            downloader.close_playwright()
    except Exception as e:
        Logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{search_string}")
def download(search_string: str, limit: int = 10, proxy_server: str = None):
    zip_io = BytesIO()
    with zipfile.ZipFile(zip_io, mode="w", compression=zipfile.ZIP_DEFLATED) as tmp_zip:
        imgs = call_downloader(search_string, limit, proxy_server)
        if imgs:
            for img in imgs:
                tmp_zip.writestr(img["filename"], img["data"])
    return StreamingResponse(
        iter([zip_io.getvalue()]),
        media_type="application/x-zip-compressed",
        headers={
            "Content-Disposition": f"attachment; filename={search_string}_images.zip"
        },
    )
