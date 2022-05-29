from app.selenium.m3u8_scraper import retrieve_m3u8_url

from fastapi import APIRouter, HTTPException, Header

router = APIRouter(
    prefix="/streams",
)


@router.get("/watchlivestream")
def get_livestream_url(
        token: str = Header(...),
):
    try:
        url = retrieve_m3u8_url()
        print("HERE: " + str(url))
        return {"url": url}

    except Exception as e:
        print(e)
        return HTTPException(400, detail=e)
