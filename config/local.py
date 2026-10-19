
from config.app import BASE_DIR
from geo.track_loader import TrackLoader


# Загружаем трассу из файла Яндекс Карт.
# TrackLoader сам соединяет участки и упорядочивает точки.
points = TrackLoader().load(
    BASE_DIR / "data" / "track.geojson"
)


PARAMS = {
    "track": {
        "points": points,
        "width": 6.0,
        "installation_buffer": 2.0,
        "allow_on_track": True,
    },
}
