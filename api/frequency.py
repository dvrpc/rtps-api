import re

import fastapi
from fastapi.responses import JSONResponse

from config import PG_CREDS
from main import db


# had been in this module's urls.py
# urlpatterns = [
#     url(r'^$', views.pageLoad, name='pageLoad')
# ]

# had been in rtps/urls.py
# url(r'^api/rtps/frequency\?*', include('frequency.urls')),

router = fastapi.APIRouter()


def zoneLoad():
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute(
                """
                WITH a as (
                    SELECT zonenum,
                        basescen as tBase,
                        x2tfreqsc as tDouble,
                        changetact as tActual,
                        percchange as tPercent
                    FROM public."f_zonet"
                )
                SELECT public."f_zonev".zonenum,
                    public."f_zonev".basescen as vBase,
                    public."f_zonev".x2tfreqsc as vDouble,
                    public."f_zonev".changevact as vActual,
                    public."f_zonev".percchange as vPercent,
                    a.tBase as tBase,
                    a.tDouble as tDouble,
                    a.tActual as tActual,
                    a.tPercent as tPercent
                FROM public."f_zonev"
                JOIN a ON public."f_zonev".zonenum = a.zonenum;
                """
            )
        except:
            return JSONResponse({"message": "Invalid query parameters"})
        results = cursor.fetchall()
    if not results:
        return JSONResponse({"message": "No results"})
    payload = {}
    for row in results:
        payload[int(round(row[0]))] = {
            "vBase": round(row[1], 2),
            "vDouble": round(row[2], 2),
            "vActual": round(row[3], 2),
            "vPercent": round(row[4], 2),
            "tBase": round(row[5], 2),
            "tDouble": round(row[6], 2),
            "tActual": round(row[7], 2),
            "tPercent": round(row[8], 2),
        }
    return payload


def busLoad():
    with db as cursor:
        try:
            cursor.execute("SELECT linename, changeride, percchange FROM f_bus")
        except:
            return JSONResponse({"message": "Invalid query parameters"})
        results = cursor.fetchall()
    if not results:
        return JSONResponse({"message": "No results"})
    payload = []
    for row in results:
        payload.append(
            {"linename": row[0], "AbsChange": round(row[1], 2), "Percent": round(row[2], 2)}
        )
    return payload


def railLoad():
    with db(PG_CREDS) as cursor:
        try:
            cursor.execute("SELECT linename, changeride, percchange FROM f_rail")
        except:
            return JSONResponse({"message": "Invalid query parameters"})
        results = cursor.fetchall()
    if not results:
        return JSONResponse({"message": "No results"})
    payload = {}
    for row in results:
        payload[row[0]] = {"absolute": round(row[1], 2), "percent": round(row[2], 2)}
    return payload


def transitLoad():
    with db as cursor:
        try:
            cursor.execute("SELECT linename, ampeakfreq, avg_freq FROM f_existing")
        except:
            return JSONResponse({"message": "Invalid query parameters"})
        results = cursor.fetchall()
    if not results:
        return JSONResponse({"message": "No results"})
    payload = {}
    for row in results:
        payload[str(row[0])] = {"am": round(row[1], 2), "avg_freq": round(row[2], 2)}
    return payload


@router.get("/api/rtps/v1/frequency")
def pageLoad(request):
    path = request.get_full_path()
    exp = re.compile(r"^/\w{3}/\w{4}/\w{9}\?(?=(zone|bus|rail|transit))")
    mo = re.search(exp, path)
    if "zone" in mo.group(1):
        return zoneLoad()
    elif "bus" in mo.group(1):
        return busLoad()
    elif "rail" in mo.group(1):
        return railLoad()
    elif "transit" in mo.group(1):
        return transitLoad()
    else:
        return JSONResponse({"status": "failed", "message": "something went wrong."})
