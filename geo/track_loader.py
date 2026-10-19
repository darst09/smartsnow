
import json

from shapely import LineString, MultiLineString, line_merge

from geo.coordinate_converter import CoordinateConverter


class TrackLoader:
    def __init__(self, tolerance=1.0):
        # Максимальное расстояние между соединяемыми концами
        # линий в метрах.
        self.tolerance = tolerance

    def load(self, path):
        # 1. Читаем GeoJSON, экспортированный из Яндекс Карт.
        with open(path, encoding="utf-8") as file:
            data = json.load(file)

        # 2. Извлекаем линии из GeoJSON.
        # Порядок линий в файле может быть произвольным.
        lines = self._extract_lines(data)

        if not lines:
            raise ValueError("В GeoJSON не найдены линии трассы")

        converter = CoordinateConverter()
        metric_lines = []

        # 3. Переводим координаты в метры.
        # Shapely будет рассчитывать расстояния именно в метрах.
        for line in lines:
            coordinates = []

            for longitude, latitude in line:
                coordinates.append({
                    "latitude": latitude,
                    "longitude": longitude,
                })

            positions = converter.to_metric(coordinates)

            # Убираем подряд идущие одинаковые точки.
            cleaned = [positions[0]]

            for point in positions[1:]:
                if point != cleaned[-1]:
                    cleaned.append(point)

            # Игнорируем случайные линии нулевой длины.
            if len(cleaned) < 2:
                continue

            metric_lines.append(cleaned)

        if not metric_lines:
            raise ValueError("В GeoJSON нет корректных линий трассы")

        # 4. Совмещаем близкие концы линий.
        # Промежуточные точки при этом не изменяются.
        metric_lines = self._connect_endpoints(metric_lines)

        # 5. Shapely самостоятельно определяет порядок линий
        # и разворачивает их при необходимости.
        geometry = MultiLineString(metric_lines)
        track = line_merge(geometry)

        # 6. Проверяем, удалось ли собрать одну трассу.
        # Если остались отдельные участки или развилки,
        # не пытаемся угадывать правильный маршрут.
        if not isinstance(track, LineString):
            raise ValueError(
                "Не удалось собрать единую трассу. "
                "Проверьте разрывы и развилки в GeoJSON."
            )

        # 7. Возвращаем координаты в формате SmartSnow.
        # Дальше их можно передавать в существующий Track.
        return converter.to_geo(list(track.coords))

    def _extract_lines(self, data):
        # Получаем геометрические объекты из GeoJSON.
        # Поддерживаем FeatureCollection, Feature
        # и отдельную геометрию.
        if data["type"] == "FeatureCollection":
            geometries = []

            for feature in data["features"]:
                geometries.append(feature.get("geometry"))

        elif data["type"] == "Feature":
            geometries = [data.get("geometry")]

        else:
            geometries = [data]

        # Собираем LineString и MultiLineString.
        lines = []

        for geometry in geometries:
            if geometry is None:
                continue

            if geometry["type"] == "LineString":
                lines.append(geometry["coordinates"])

            elif geometry["type"] == "MultiLineString":
                lines.extend(geometry["coordinates"])

        for line in lines:
            if len(line) < 2:
                raise ValueError(
                    "Линия GeoJSON содержит менее двух точек"
                )

        return lines

    def _connect_endpoints(self, lines):
        # Собираем начала и концы всех линий.
        # Именно они должны соединяться между собой.
        endpoints = []

        for line in lines:
            endpoints.append(line[0])
            endpoints.append(line[-1])

        # Группируем близкие концы.
        # Первую точку группы используем как общую координату.
        groups = []

        for point in endpoints:
            matches = []

            for group in groups:
                reference = group[0]

                if (
                    LineString([point, reference]).length
                    <= self.tolerance
                ):
                    matches.append(group)

            if len(matches) > 1:
                raise ValueError(
                    "Неоднозначное соединение концов линий"
                )

            if matches:
                matches[0].append(point)
            else:
                groups.append([point])

        # Проверяем, что каждая группа достаточно компактна.
        # Это защищает от объединения слишком далёких точек.
        for group in groups:
            for first in group:
                for second in group:
                    if (
                        LineString([first, second]).length
                        > self.tolerance
                    ):
                        raise ValueError(
                            "Неоднозначное соединение концов линий"
                        )

        # Заменяем близкие концы одинаковыми координатами.
        # Внутренние точки каждой линии остаются прежними.
        result = []

        for line in lines:
            updated = list(line)

            for index in (0, -1):
                point = updated[index]

                for group in groups:
                    if point in group:
                        updated[index] = group[0]
                        break

            # После совмещения концов линия могла стать
            # вырожденной. Такой результат считаем ошибкой.
            if LineString(updated).length == 0:
                raise ValueError(
                    "После соединения концов появилась "
                    "линия нулевой длины"
                )

            result.append(updated)

        return result
