
import math

import rasterio
from bmi_topography import Topography

from config.app import APP


class ElevationProvider:
    def get_elevations(self, coordinates):
        # Если список координат пуст, возвращаем пустой список
        if not coordinates:
            return []

        # Получаем настройки сервиса высот
        config = APP["elevation"]
        api_key = config["api_key"]

        # Проверяем наличие API-ключа OpenTopography
        if not api_key:
            raise ValueError("Не задан OPENTOPOGRAPHY_API_KEY")

        # Собираем широты и долготы всех точек трассы
        latitudes = [p["latitude"] for p in coordinates]
        longitudes = [p["longitude"] for p in coordinates]

        # Запас территории вокруг трассы в метрах
        buffer_m = config["buffer_meters"]

        # Переводим запас из метров в градусы широты
        # Один градус широты примерно равен 111 320 метрам
        lat_buffer = buffer_m / 111_320

        # Для долготы учитываем широту местности:
        # чем ближе к полюсам, тем меньше длина градуса долготы
        mean_lat = math.radians(
            sum(latitudes) / len(latitudes)
        )
        lon_buffer = buffer_m / (
            111_320 * math.cos(mean_lat)
        )

        # Создаём объект для получения цифровой модели рельефа
        # Прямоугольник охватывает все точки трассы
        # с дополнительным запасом со всех четырёх сторон
        dem = Topography(
            dem_type=config["dataset"],
            south=min(latitudes) - lat_buffer,
            north=max(latitudes) + lat_buffer,
            west=min(longitudes) - lon_buffer,
            east=max(longitudes) + lon_buffer,
            output_format="GTiff",
            api_key=api_key,
        )

        # Скачиваем модель рельефа в формате GeoTIFF
        # Если такая область уже есть в кеше библиотеки,
        # используется ранее загруженный файл
        dem_path = dem.fetch()

        # Открываем файл цифровой модели рельефа
        with rasterio.open(dem_path) as raster:

            # Проверяем систему координат растра
            # EPSG:4326 означает широту и долготу WGS84
            if raster.crs is None or raster.crs.to_epsg() != 4326:
                raise ValueError("Ожидается DEM в EPSG:4326")

            # Преобразуем координаты в формат rasterio:
            # сначала долгота (X), затем широта (Y)
            points = [
                (p["longitude"], p["latitude"])
                for p in coordinates
            ]

            # Здесь будем хранить высоты точек трассы
            elevations = []

            # Получаем высоту для каждой точки из растра
            for value in raster.sample(points, masked=True):

                # Проверяем, что для точки есть данные
                if value.mask.any():
                    raise ValueError(
                        "Для одной из точек нет данных о высоте"
                    )

                # Добавляем высоту в метрах
                elevations.append(float(value[0]))

        # Возвращаем высоты в том же порядке,
        # в котором были переданы координаты трассы
        return elevations
