from app import create_app
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv(".env")

app = create_app()

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=2,  # liczba proxy przed aplikacją
    x_proto=1,
    x_host=1,
    x_prefix=1,
)

if __name__ == "__main__":
    app.run(debug=True)
