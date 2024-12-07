"""
Основные шаги реализации:
Класс PriceListAnalyzer:

Метод load_prices считывает файлы, фильтрует их по столбцам и обрабатывает данные.
Метод export_to_html сохраняет данные в HTML.
Метод find_text выполняет поиск по тексту и сортирует результаты.
Главный цикл:

Считывает данные из папки.
Предоставляет консольный интерфейс для поиска.
Экспортирует результаты в HTML по запросу.
Пример запуска:
Убедитесь, что файлы находятся в папке, указанной в начале программы.
Выполните скрипт, введите текст для поиска, и результаты появятся на экране.
Для экспорта в HTML выберите да при соответствующем запросе.

"""


import os
import pandas as pd


class PriceListAnalyzer:
    def __init__(self, folder):
        self.folder = folder
        self.data = pd.DataFrame()

    def load_prices(self):
        """Сканирует папку и загружает данные из прайс-листов."""
        files = [f for f in os.listdir(self.folder) if "price" in f.lower() and f.endswith(".csv")]
        all_data = []
        for file in files:
            file_path = os.path.join(self.folder, file)
            try:
                df = pd.read_csv(file_path, sep=';', encoding='utf-8')
                df.columns = [col.strip().lower() for col in
                              df.columns]  # Привести названия столбцов к нижнему регистру
                product_col = next(
                    (col for col in df.columns if col in {"название", "продукт", "товар", "наименование"}), None)
                price_col = next((col for col in df.columns if col in {"цена", "розница"}), None)
                weight_col = next((col for col in df.columns if col in {"фасовка", "масса", "вес"}), None)

                if product_col and price_col and weight_col:
                    df = df[[product_col, price_col, weight_col]]
                    df.columns = ["Наименование", "Цена", "Вес"]
                    df["Вес"] = df["Вес"].astype(float)
                    df["Цена"] = df["Цена"].astype(float)
                    df["Файл"] = file
                    df["Цена за кг"] = df["Цена"] / df["Вес"]
                    all_data.append(df)
            except Exception as e:
                print(f"Ошибка обработки файла {file}: {e}")

        self.data = pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

    def export_to_html(self, filename="output.html"):
        """Выгружает данные в HTML файл."""
        if self.data.empty:
            print("Данные отсутствуют.")
        else:
            self.data.to_html(filename, index=False, escape=False)
            print(f"Данные успешно сохранены в файл {filename}")

    def find_text(self, query):
        """Ищет текст в столбце 'Наименование' и возвращает результаты."""
        if self.data.empty:
            print("Данные отсутствуют.")
            return pd.DataFrame()
        filtered = self.data[self.data["Наименование"].str.contains(query, case=False, na=False)]
        return filtered.sort_values(by="Цена за кг", ascending=True)


def main():
    folder = input("Введите путь к папке с прайс-листами: ").strip()
    analyzer = PriceListAnalyzer(folder)
    analyzer.load_prices()

    if analyzer.data.empty:
        print("Не удалось загрузить данные. Проверьте содержимое папки.")
        return

    while True:
        query = input("Введите текст для поиска (или 'exit' для выхода): ").strip()
        if query.lower() == "exit":
            print("Работа завершена.")
            break
        results = analyzer.find_text(query)
        if results.empty:
            print("Ничего не найдено.")
        else:
            print(results.to_string(index=False, columns=["Наименование", "Цена", "Вес", "Файл", "Цена за кг"]))

    export = input("Хотите экспортировать данные в HTML? (да/нет): ").strip().lower()
    if export == "да":
        analyzer.export_to_html()


if __name__ == "__main__":
    main()
