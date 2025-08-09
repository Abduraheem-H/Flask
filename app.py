from flask import Flask
from flask_smorest import Api

from resources import item, store


app = Flask(__name__)

app.config["API_TITLE"] = "Store and Item API"
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.2"
app.config["OPENAPI_JSON_PATH"] = "openapi.json"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"


api = Api(app)

api.register_blueprint(store.bp)
api.register_blueprint(item.bp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
