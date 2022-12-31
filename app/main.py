from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.models import mongodb
from app.models.book import Book
from app.book_scraper import NaverBookScraper

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # book = Book(keyword="파이썬", publisher="BJPublic", price=1200, image='me.png')
    # print(await mongodb.engine.save(book))     # DB에 저장
    return templates.TemplateResponse("./index.html",
                                      {"request": request,
                                       "title": "콜렉터 북북이"})


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str):
    # 쿼리에서 검색어 추출
    keyword = q
    # 데이터 수집
    naver_book_sraper = NaverBookScraper()
    books = await naver_book_sraper.search(keyword, 10)
    book_models = []
    for book in books:
        book_model = Book(
            keyword=keyword,
            publisher=book['publisher'],
            price=book['discount'] if book.get('discount') else -1,
            image=book['image']
        )
        book_models.append(book_model)
    await mongodb.engine.save_all(book_models)

    return templates.TemplateResponse("./index.html",
                                      {"request": request,
                                       "title": "콜렉터 북북이",
                                       "keyword": q})


@app.on_event("startup")
async def on_app_start():
    mongodb.connect()


@app.on_event("shutdown")
async def on_app_shutdown():
    mongodb.close()