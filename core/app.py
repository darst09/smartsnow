from core.models.track import Track


class App:
    def __init__(self, data):
        self.data = data

    def calculate(self):
        track_data = self.data["track"]

        track = Track(
            coordinates=track_data["points"],
            width=track_data["width"],
            installation_buffer=track_data["installation_buffer"],
            allow_on_track=track_data["allow_on_track"],
        )

        # Позже:
        # Создание моделей пушек
        # Учёт ветра и рельефа
        # Расчёт покрытия
        # Запуск оптимизатора

        return track
