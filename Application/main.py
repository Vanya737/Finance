import flet as ft
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

def main(page: ft.Page):
    page.title = "Финансовый трекер"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window_width = 400
    page.window_height = 700

    # Данные
    df = pd.DataFrame(columns=["Дата", "Сумма", "Тип", "Категория", "Описание"])

    # Функция для создания графика расходов по категориям
    def create_expenses_graph():
        expenses_df = df[df["Тип"] == "Расход"]
        expenses_by_category = expenses_df.groupby("Категория")["Сумма"].sum()
        colors = ['#FF6347', '#FFD700', '#FF69B4', '#1E90FF', '#90EE90', '#FFA07A', '#9370DB', '#20B2AA']
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(expenses_by_category.values, labels=expenses_by_category.index, autopct='%1.1f%%', startangle=140,
               colors=colors)
        ax.axis('equal')
        ax.set_title("Расходы по категориям")
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        return img_base64

    # Функция для создания графика доходов/расходов по времени
    def create_timeline_graph():
        fig, ax = plt.subplots(figsize=(6, 4))
        income_total = df[df["Тип"] == "Доход"]["Сумма"].sum()
        expenses_total = df[df["Тип"] == "Расход"]["Сумма"].sum()
        labels = ['Доходы', 'Расходы']
        sizes = [income_total, expenses_total]
        colors = ['skyblue', 'lightcoral']
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        ax.set_title("Соотношение доходов и расходов")
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        return img_base64

    # Функция для обновления графиков и расчетов
    def update_data():
        # Расчет баланса
        total_income = df[df["Тип"] == "Доход"]["Сумма"].sum()
        total_expenses = df[df["Тип"] == "Расход"]["Сумма"].sum()
        balance = total_income - total_expenses
        balance_text.value = f"Баланс: {balance:.2f}"

        # Обновление графиков
        expenses_graph.src_base64 = create_expenses_graph()
        timeline_graph.src_base64 = create_timeline_graph()
        page.update()

    # Функция для добавления записи
    def add_record(e):
        try:
            new_record = {
                "Дата": date_picker.value,
                "Сумма": float(amount_text_field.value),
                "Тип": type_dropdown.value,
                "Категория": category_dropdown.value,
                "Описание": description_text_field.value,
            }
            df.loc[len(df)] = new_record
            df.to_csv("finances.csv", index=False)
            amount_text_field.value = ""
            description_text_field.value = ""
            update_data()

        except ValueError:
            ft.snackbar(page, "Пожалуйста, введите корректные данные.", open=True)

    # Виджеты
    amount_text_field = ft.TextField(label="Сумма", value="0.0")
    date_picker = ft.TextField(label="Дата")
    type_dropdown = ft.Dropdown(label="Тип", options=[ft.dropdown.Option("Доход"), ft.dropdown.Option("Расход")])
    category_dropdown = ft.Dropdown(
        label="Категория",
        options=[
            ft.dropdown.Option("Еда"),
            ft.dropdown.Option("Транспорт"),
            ft.dropdown.Option("Развлечения"),
            ft.dropdown.Option("Одежда"),
            ft.dropdown.Option("Зарплата"),
            ft.dropdown.Option("Инвестиции"),
            ft.dropdown.Option("Другое"),
        ],
    )
    description_text_field = ft.TextField(label="Описание (опционально)")
    add_button = ft.ElevatedButton("Добавить запись", on_click=add_record)
    balance_text = ft.Text(size=20)
    expenses_graph = ft.Image(width=400, height=300)
    timeline_graph = ft.Image(width=400, height=300)

    # Макет с размещением графиков рядом
    page.add(
        ft.Tabs(
            [
                ft.Tab(
                    text="Добавить транзакцию",
                    content=ft.Column(
                        [
                            amount_text_field,
                            date_picker,
                            type_dropdown,
                            category_dropdown,
                            description_text_field,
                            add_button,
                        ]
                    ),
                ),
                ft.Tab(
                    text="Баланс",
                    content=ft.Column(
                        [
                            balance_text,
                        ]
                    ),
                ),
                ft.Tab(
                    text="Графики",
                    content=ft.Column(
                        [
                            ft.Container(
                                content=expenses_graph,
                                width=400,
                                height=300,
                            ),
                            ft.Container(
                                content=timeline_graph,
                                width=400,
                                height=300,
                            ),
                        ]
                    ),
                ),
            ]
        )
    )

    # Чтение данных и обновление
    try:
        df = pd.read_csv("finances.csv")
    except FileNotFoundError:
        print("Файл finances.csv не найден. Создаю новый файл.")
        df = pd.DataFrame(columns=["Дата", "Сумма", "Тип", "Категория", "Описание"])
        df.to_csv("finances.csv", index=False)
    except pd.errors.EmptyDataError:
        print("Файл finances.csv пуст. Использую пустой DataFrame.")
    finally:
        update_data()  # Обновляем графики и расчеты

ft.app(target=main)
