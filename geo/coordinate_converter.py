
from pyproj import Transformer


class CoordinateConverter:
    def __init__(self):
        # WGS84 — географическая система координат.
        # Координаты задаются широтой и долготой в градусах.
        geo_crs = "EPSG:4326"

        # UTM, зона 38N — метрическая система координат.
        # Подходит для трассы в Корте (Марий Эл).
        # Координаты X и Y выражаются в метрах.
        metric_crs = "EPSG:32638"

        # Преобразователь из географических координат
        # в метрические (широта/долгота -> X/Y).
        self._to_metric = Transformer.from_crs(
            geo_crs,
            metric_crs,
            always_xy=True,
        )

        # Обратный преобразователь из метрических координат
        # в географические (X/Y -> широта/долгота).
        self._to_geo = Transformer.from_crs(
            metric_crs,
            geo_crs,
            always_xy=True,
        )

    def to_metric(self, coordinates):
        """
        Преобразует список географических координат в метры.

        Вход:
            [
                {"latitude": 56.600491, "longitude": 47.966353},
                ...
            ]

        Выход:
            [
                (x, y),
                ...
            ]
        """

        # Собираем долготы и широты в отдельные массивы.
        longitudes = [point["longitude"] for point in coordinates]
        latitudes = [point["latitude"] for point in coordinates]

        # Преобразуем сразу все точки.
        # always_xy=True означает, что сначала передаём
        # долготу, затем широту.
        xs, ys = self._to_metric.transform(
            longitudes,
            latitudes,
        )

        # Объединяем X и Y в пары.
        # Порядок точек сохраняется.
        return list(zip(xs, ys))

    def to_geo(self, coordinates):
        """
        Преобразует метрические координаты обратно
        в географические.

        Вход:
            [
                (x, y),
                ...
            ]

        Выход:
            [
                {"latitude": 56.600491, "longitude": 47.966353},
                ...
            ]
        """

        # Разделяем метрические координаты на X и Y.
        xs = [point[0] for point in coordinates]
        ys = [point[1] for point in coordinates]

        # Преобразуем все точки обратно в WGS84.
        # Результат: долгота и широта в градусах.
        longitudes, latitudes = self._to_geo.transform(
            xs,
            ys,
        )

        # Возвращаем координаты в формате SmartSnow.
        # Такой формат можно использовать для Яндекс Карт.
        return [
            {
                "latitude": latitude,
                "longitude": longitude,
            }
            for longitude, latitude in zip(
                longitudes,
                latitudes,
            )
        ]
