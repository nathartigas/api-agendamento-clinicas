from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(include_in_schema=False)


@router.get("/docs", response_class=HTMLResponse)
def swagger_ui() -> str:
    """Swagger UI com dependencias fixadas e protegidas por Subresource Integrity."""

    return """<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>API de Agendamento - Swagger UI</title>
    <link rel="stylesheet"
          href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14/swagger-ui.css"
          integrity="sha384-wxLW6kwyHktdDGr6Pv1zgm/VGJh99lfUbzSn6HNHBENZlCN7W602k9VkGdxuFvPn"
          crossorigin="anonymous">
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14/swagger-ui-bundle.js"
            integrity="sha384-wmyclcVGX/WhUkdkATwhaK1X1JtiNrr2EoYJ+diV3vj4v6OC5yCeSu+yW13SYJep"
            crossorigin="anonymous"></script>
    <script src="/static/swagger-init.js"></script>
  </body>
</html>
"""
