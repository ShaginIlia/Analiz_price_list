from tabulate import tabulate
import csv
import os
import re


def display_results(results):
    """
    Функция, позволяющая отобразить результаты в виде таблицы с заголовками
    :param results: результаты, получаемые по анализу прайс-листов
    :return: таблица с данными в удобном формате grid
    """
    headers = ['№', 'Наименование', 'Цена', 'Вес', 'Файл', 'Цена за кг.']
    numbered_results = []
    for i, result in enumerate(results):
        row = [i + 1] + result[1:] + [result[0]]
        numbered_results.append(row)
    print(tabulate(numbered_results, headers=headers, tablefmt='grid'))


def export_to_html(results, filename):
    """
    Функция для записи таблицы в html формате и сохранении отдельным файлом
    :param results: результаты, получаемые по анализу прайс-листов
    :param filename: имя анализируемого файла
    :return: таблица в формате html, сохранённая в отдельном файле
    """
    headers = ['№', 'Наименование', 'Цена', 'Вес', 'Файл', 'Цена за кг.']
    numbered_results = []
    for i, result in enumerate(results):
        row = [i + 1] + result[1:] + [result[0]]
        numbered_results.append(row)
    table = tabulate(numbered_results, headers=headers, tablefmt='html')
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(table)


class PriceMachine:

    def __init__(self):
        self.data = []
        self.name_length = 0

    def load_prices(self, directory):
        """
        Функция для обработки каждого csv файла в папке, чтобы вычленить нужную информацию
        (название продукта, его цена, вес и т.д.)
        :param directory: папка с файлами
        :return: найденные заданные данные в файлах
        """
        for filename in os.listdir(directory):
            if filename.endswith('.csv') and 'price' in filename.lower():
                with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                    df = csv.DictReader(file)
                    for row in df:
                        product_name = None
                        price = None
                        weight = None
                        for column_name in row:
                            if re.search(r'(название|продукт|товар|наименование)', column_name, re.IGNORECASE):
                                product_name = row[column_name].strip()
                            elif re.search(r'(цена|розница)', column_name, re.IGNORECASE):
                                price = float(row[column_name].replace(',', '.').strip())
                            elif re.search(r'(фасовка|масса|вес)', column_name, re.IGNORECASE):
                                weight = float(row[column_name].replace(',', '.').strip())

                        if product_name and price is not None and weight is not None:
                            self.data.append([product_name, price, weight, filename, round(price / weight, 2)])

    def search_product(self, request):
        """
        Функция для поиска товаров в списке, сформированном выше - self.data
        :param request: запрос от пользователя, что надо найти
        :return: отсортированный список найденных результатов
        """
        results = []
        for row in self.data:
            if re.search(request, row[1], re.IGNORECASE):
                results.append(row)
        return sorted(results, key=lambda x: x[2] / x[3])

    def find_text(self, request):
        """
        Функция для поиска товаров по заданному запросу query
        :param request: запрос от пользователя
        :return: результаты в виде таблицы в консоль, и сохранения этих результатов в HTML-файл
        """
        results = self.search_product(request)
        display_results(results)
        html_filename = 'find_results.html'
        export_to_html(results, html_filename)
        print(f"Результаты поиска сохранены в файле: {html_filename}")

    def main(self, directory):
        """
        Итоговая функция, которая включает всё выше созданное для удобства использования
        :param directory: папка, где находятся нужные файлы
        :return: список с информацией о товарах
        """
        self.load_prices(directory)

        while True:
            request = input("Введите текст для поиска (или 'exit' для завершения): ")
            if request.lower() == 'exit':
                print("Работа завершена.")
                break
            self.find_text(request)


if __name__ == "__main__":
    pm = PriceMachine()
    current_directory = os.path.dirname(os.path.abspath('your_directory'))
    pm.main(current_directory)
