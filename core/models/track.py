
from geo.elevation_provider import ElevationProvider
from geo.coordinate_converter import CoordinateConverter
from core.models.point import Point


class Track:
    def __init__(
        self,
        coordinates,
        width,
        installation_buffer,
        allow_on_track,
    ):
        # Исходные географические координаты трассы
        self.coordinates = coordinates

        # Ширина трассы в метрах
        self.width = width

        # Минимальное расстояние установки пушки от трассы
        self.installation_buffer = installation_buffer

        # Разрешена ли установка пушки непосредственно на трассе
        self.allow_on_track = allow_on_track

        # Высоты точек трассы
        self.elevations = []

        # Подготовленные точки трассы в метрических координатах
        self.points = []

        # Автоматически подготавливаем трассу
        self._build()

    def _build(self):
        # Если координат нет, ничего не создаём
        if not self.coordinates:
            return

        # Получаем высоты всех точек трассы
        self.elevations = ElevationProvider().get_elevations(
            self.coordinates
        )

        # Преобразуем широту и долготу в координаты X, Y
        # в метрах с помощью CoordinateConverter
        positions = CoordinateConverter().to_metric(
            self.coordinates
        )

        # Проверяем, что для каждой точки получена высота
        if len(positions) != len(self.elevations):
            raise ValueError(
                "Количество координат и высот не совпадает"
            )

        # Создаём объекты Point, объединяя
        # метрические координаты и высоту каждой точки
        self.points = []

        for (x, y), elevation in zip(positions, self.elevations):
            point = Point(x, y, elevation)
            self.points.append(point)
