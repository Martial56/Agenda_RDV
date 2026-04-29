from waitress import serve
from arv_agenda.wsgi import application

if __name__ == "__main__":
    serve(
        application,
        host="0.0.0.0",
        port=8010,
        threads=8
    )