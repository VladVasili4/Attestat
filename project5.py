"""
Основные изменения:
Метод load_prices — обрабатывает файлы, извлекая данные по заданным критериям.
Метод _search_product_price_weight — ищет индексы столбцов по их возможным названиям.
Метод export_to_html — сохраняет данные в HTML.
Метод find_text — выполняет поиск по заданному тексту.
Попробуйте запустить код, указав путь к папке с файлами, и убедитесь, что он работает корректно.


"""


import os
import csv
import html


class PriceMachine:
    def __init__(self):
        self.data = []  # Список для хранения данных
        self.result = ''  # Результат для экспорта в HTML
        self.name_length = 0  # Длина самого длинного названия продукта
        self.last_search_result = []  # Результаты последнего поиска

    def load_prices(self, folder_path='files_of_prices'):
        """
        Сканирует указанный каталог. Ищет файлы со словом price в названии.
        В файле ищет столбцы с названием товара, ценой и весом.
        """
        if not folder_path:
            folder_path = os.getcwd()

        files = [f for f in os.listdir(folder_path) if "price" in f.lower() and f.endswith(".csv")]
        if not files:
            print("Файлы не найдены.")
            return

        for file in files:
            file_path = os.path.join(folder_path, file)
            with open(file_path, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=',')                           # !!!!!!!!!!!!!! Не ";", а "," !!!!!
                headers = next(reader, None)
                if headers:
                    product_idx, price_idx, weight_idx = self._search_product_price_weight(headers)
                    if product_idx is not None and price_idx is not None and weight_idx is not None:
                        for row in reader:
                            try:
                                product_name = row[product_idx].strip()
                                price = float(row[price_idx])
                                weight = float(row[weight_idx])
                                price_per_kg = price / weight
                                self.data.append({
                                    "name": product_name,
                                    "price": price,
                                    "weight": weight,
                                    "file": file,
                                    "price_per_kg": price_per_kg
                                })
                                self.name_length = max(self.name_length, len(product_name))
                            except (ValueError, IndexError):
                                continue
        print("Данные успешно загружены.")

    def _search_product_price_weight(self, headers):
        """
        Возвращает индексы столбцов для названия товара, цены и веса.
        """
        product_names = {"товар", "название", "наименование", "продукт"}
        price_names = {"цена", "розница"}
        weight_names = {"вес", "масса", "фасовка"}

        product_idx = next((i for i, h in enumerate(headers) if h.strip().lower() in product_names), None)
        price_idx = next((i for i, h in enumerate(headers) if h.strip().lower() in price_names), None)
        weight_idx = next((i for i, h in enumerate(headers) if h.strip().lower() in weight_names), None)

        return product_idx, price_idx, weight_idx

    def export_to_html(self, fname='output.html'):
        """
        Экспортирует данные в HTML файл.
        """
        if not self.data:
            print("Нет данных для экспорта.")
            return

        result = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>            
        </head>
        <body>
            <table border="1">
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        '''

        for idx, item in enumerate(self.data, start=1):
            result += f'''
                <tr>
                    <td>{idx}</td>
                    <td>{html.escape(item["name"])}</td>
                    <td>{item["price"]:.2f}</td>
                    <td>{item["weight"]:.2f}</td>
                    <td>{html.escape(item["file"])}</td>
                    <td>{item["price_per_kg"]:.2f}</td>
                </tr>
            '''

        result += '''
            </table>
        </body>
        </html>
        '''
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"Данные успешно экспортированы в файл {fname}")

    def find_text(self, text):
        """
        Выполняет поиск по тексту в названии товара.
        Если текст равен '*', возвращает весь список данных.
        """
        if not self.data:
            print("Данные отсутствуют.")
            return []

        if text == "*":
            print("Вывод всех записей:")
            return sorted(self.data, key=lambda x: x["price_per_kg"])

        filtered = [item for item in self.data if text.lower() in item["name"].lower()]
        if not filtered:
            print("Ничего не найдено.")
        return sorted(filtered, key=lambda x: x["price_per_kg"])


# Логика работы программы
if __name__ == "__main__":
    pm = PriceMachine()
    folder = input("Введите путь к папке с прайс-листами (нажмите Enter для текущей папки): ").strip()
    pm.load_prices(folder)

    while True:
        query = input("Введите текст для поиска (или 'exit' для выхода): ").strip()
        if query.lower() == "exit":
            break
        results = pm.find_text(query)
        if not results:
            print("Ничего не найдено.")
        else:
            print(f"{'№':<5}{'Название':<{pm.name_length + 2}}{'Цена':<10}{'Вес':<10}{'Файл':<15}{'Цена за кг.':<10}")
            for idx, item in enumerate(results, start=1):
                print(f"{idx:<5}{item['name']:<{pm.name_length + 2}}{item['price']:<10.2f}{item['weight']:<10.2f}"
                      f"{item['file']:<15}{item['price_per_kg']:<10.2f}")

    export = input("Хотите экспортировать данные в HTML? (да/нет): ").strip().lower()
    if export == "да":
        pm.export_to_html()

    print("Программа завершена.")
