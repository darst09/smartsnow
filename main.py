from config.local import PARAMS
from core.app import App


def main():
    result = App(PARAMS).calculate()

    print("Ширина трассы:", result.width)
    print("Буфер установки:", result.installation_buffer)
    print("Установка на трассе:", result.allow_on_track)
    print("Исходных точек:", len(result.coordinates))
    print("Подготовленных точек:", len(result.points))

if __name__ == "__main__":
    main()
