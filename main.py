import random

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request


AB_CONFIGURATIONS = {
    "version-a": {
        "homePage": "with-orange-background",
        "checkout": [
            {"home": {"nextAction": "/basket", "title": "Version A"}},
            {"basket": {"nextAction": "/account", "title": "Version A : Basket is the first step"}},
            {"account": {"nextAction": "/submit", "title": "Version A : Account is the second step"}},
            {"submit": {"nextAction": "", "title": "Success"}},
        ]
    },
    "version-b": {
        "homePage": "with-orange-background",
        "checkout": [
            {"home": {"nextAction": "/account", "title": "Version B"}},
            {"account": {"nextAction": "/basket", "title": "Version B : Account is the first step"}},
            {"basket": {"nextAction": "/submit", "title": "Version B : Basket is the second step"}},
            {"submit": {"nextAction": "", "title": "Success"}},
        ]
    }
}

MAP_PAGE = {
    "with-orange-background": "landing_page.html",
    "basket": "basket_page.html",
    "account": "account_page.html",
    "submit": "success_page.html",
}

templates = Jinja2Templates(directory="templates/")

app = FastAPI()

def get_version():
    return random.choice(list(AB_CONFIGURATIONS.keys()))

@app.get("/")
def get_home(request: Request):
    version = get_version()
    version_info = AB_CONFIGURATIONS[version]
    response = templates.TemplateResponse(
        MAP_PAGE.get(version_info['homePage']),
        {
            "request": request,
            "title": version,
            "nextAction": version_info['checkout'][0]['home']['nextAction'],
        }
    )
    # New version each session
    response.set_cookie(key="ab_version", value=version, max_age=60*5)  # expires in five minutes
    return response

@app.get("/{action}")
def get_action_page(request: Request, action: str):
    version = request.cookies.get('ab_version', get_version())

    for step in AB_CONFIGURATIONS[version]['checkout']:
        page_data = step.get(action)
        if page_data:
            return templates.TemplateResponse(MAP_PAGE.get(action), {
                "request": request,
                "title": page_data['title'],
                "nextAction": page_data['nextAction'],
                }
            )

    return HTMLResponse(content="Not Found", status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
