import tkinter as tk
from tkinter import ttk, messagebox, font
from datetime import datetime, timedelta, date
import json
import os
from calendar import monthrange
import locale
from tkinter import colorchooser

class ModernEmployeeScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("📅 Графификатор смен - Умное планирование")
        self.root.geometry("1400x900")
        
        # Пробуем установить локаль для русских названий месяцев
        self.setup_locale()
        
        # Цветовая схема ДО создания стилей
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'light': '#ecf0f1',
            'dark': '#2c3e50',
            'background': '#f5f7fa',
            'card': '#ffffff',
            'border': '#dcdde1',
            'info': '#17a2b8'
        }
        
        # Данные
        self.employees = []
        self.shifts = []
        self.shift_colors = {}
        
        # Категории работников по умолчанию
        self.categories = [
            "Официанты",
            "Повара", 
            "Бариста",
            "Администрация",
            "Уборка",
            "Охранники",
            "Другое"
        ]
        
        # Типы смен по умолчанию (теперь будут редактируемыми)
        self.shift_types_data = {
            "Утренняя": {"start": "08:00", "end": "16:00", "color": "#3498db"},
            "Дневная": {"start": "12:00", "end": "20:00", "color": "#2ecc71"},
            "Вечерняя": {"start": "16:00", "end": "00:00", "color": "#e67e22"},
            "Ночная": {"start": "00:00", "end": "08:00", "color": "#9b59b6"},
            "Выходной": {"start": "00:00", "end": "00:00", "color": "#95a5a6"},
            "Сокращенная": {"start": "08:00", "end": "14:00", "color": "#1abc9c"}
        }
        
        # Генерируем список типов смен для отображения
        self.shift_types = self.generate_shift_types_list()
        
        # Текущий месяц и год
        self.current_date = datetime.now()
        self.current_year = self.current_date.year
        self.current_month = self.current_date.month
        
        # Для перетаскивания смен
        self.drag_data = {"item": None, "day": None, "employee": None}
        self.dragging = False
        
        # Для копирования/вставки
        self.copied_shift = None
        
        # Автосохранение
        self.auto_save_id = None
        
        # Для фильтрации по категориям
        self.filter_category = "Все категории"
        
        # Счетчик часов
        self.hours_counter = {}
        
        # Настройка стилей
        self.setup_styles()
        
        # Загрузка данных при запуске
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Центрирование окна
        self.center_window()
        
        # Настройка горячих клавиш
        self.setup_hotkeys()
        
        # Запуск автосохранения
        self.start_auto_save()
        
        # Настройка перетаскивания
        self.setup_drag_and_drop()
        
        # Инициализация счетчика часов
        self.calculate_hours()
    
    def setup_hotkeys(self):
        """Настройка горячих клавиш"""
        self.root.bind('<Control-d>', lambda e: self.delete_selected_shift())
        self.root.bind('<Delete>', lambda e: self.delete_selected_shift())
        self.root.bind('<Control-Delete>', lambda e: self.delete_all_shifts_for_day())
        self.root.bind('<Control-s>', lambda e: self.save_data())
        self.root.bind('<Control-Shift-S>', lambda e: self.export_to_txt())
        self.root.bind('<Escape>', lambda e: self.clear_selection())
        self.root.bind('<Control-g>', lambda e: self.generate_month())
        self.root.bind('<Control-c>', lambda e: self.copy_selected_shift())
        self.root.bind('<Control-v>', lambda e: self.paste_shift())
        self.root.bind('<Control-f>', lambda e: self.filter_by_category())
        self.root.bind('<Button-3>', self.show_context_menu)  # Правая кнопка мыши
        self.root.bind('<Control-h>', lambda e: self.show_hours_statistics())  # Горячая клавиша для часов
    
    def setup_locale(self):
        """Настройка локали для русских названий месяцев"""
        locales_to_try = [
            'ru_RU.UTF-8',
            'ru_RU.utf8',
            'Russian_Russia.1251',
            'Russian',
            'ru'
        ]
        
        locale_set = False
        for loc in locales_to_try:
            try:
                locale.setlocale(locale.LC_TIME, loc)
                locale_set = True
                break
            except locale.Error:
                continue
        
        if not locale_set:
            print("Не удалось установить русскую локаль. Будут использоваться английские названия.")
    
    def setup_styles(self):
        """Настройка современных стилей"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Настраиваем цвета
        style.configure('TFrame', background=self.colors['background'])
        style.configure('TLabel', background=self.colors['background'], font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10))
        style.configure('TEntry', font=('Segoe UI', 10))
        style.configure('TCombobox', font=('Segoe UI', 10))
        
        # Кастомные стили для кнопок
        style.configure('Primary.TButton', 
                       background=self.colors['primary'], 
                       foreground='white',
                       borderwidth=1,
                       focusthickness=3,
                       focuscolor='none')
        
        style.configure('Success.TButton', 
                       background=self.colors['success'], 
                       foreground='white',
                       borderwidth=1)
        
        style.configure('Warning.TButton', 
                       background=self.colors['warning'], 
                       foreground='white',
                       borderwidth=1)
        
        style.configure('Danger.TButton', 
                       background=self.colors['danger'], 
                       foreground='white',
                       borderwidth=1)
        
        style.configure('Info.TButton',
                       background=self.colors['info'],
                       foreground='white',
                       borderwidth=1)
        
        # Стиль для карточек
        style.configure('Card.TFrame', 
                       background=self.colors['card'], 
                       relief=tk.RAISED, 
                       borderwidth=1)
        
        # Стиль для заголовков
        style.configure('Header.TLabel', 
                       font=('Segoe UI', 12, 'bold'), 
                       background=self.colors['primary'], 
                       foreground='white')
    
    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        # Основные фреймы с современным дизайном
        main_container = ttk.Frame(self.root, style='Card.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Верхняя панель с заголовком и навигацией
        self.create_header(main_container)
        
        # Основное содержимое
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Левая панель - управление
        left_panel = ttk.Frame(content_frame, style='Card.TFrame')
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.create_control_panel(left_panel)
        
        # Правая панель - график
        right_panel = ttk.Frame(content_frame, style='Card.TFrame')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.create_schedule_panel(right_panel)
        
        # Статус бар внизу
        self.create_status_bar(main_container)
        
        # Инициализация графика
        self.update_schedule_display()
    
    def create_header(self, parent):
        """Создание верхней панели с заголовком и поиском"""
        header_frame = ttk.Frame(parent, style='Card.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Заголовок приложения
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=10)
        
        title_label = tk.Label(title_frame, text="📅 Графификатор смен", 
                              font=('Segoe UI', 24, 'bold'), 
                              fg=self.colors['primary'],
                              bg=self.colors['card'])
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Умное планирование рабочих смен", 
                                 font=('Segoe UI', 11), 
                                 fg=self.colors['dark'],
                                 bg=self.colors['card'])
        subtitle_label.pack()
        
        # Панель поиска и фильтрации
        search_frame = ttk.Frame(header_frame)
        search_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Фильтр по категориям
        ttk.Label(search_frame, text="Категория:", 
                 font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(0, 5))
        
        self.category_filter_var = tk.StringVar(value="Все категории")
        self.category_filter = ttk.Combobox(search_frame, 
                                           textvariable=self.category_filter_var,
                                           values=["Все категории"] + self.categories,
                                           width=15, font=('Segoe UI', 10), state="readonly")
        self.category_filter.pack(side=tk.LEFT, padx=5)
        self.category_filter.bind('<<ComboboxSelected>>', lambda e: self.filter_by_category())
        
        # Поле поиска
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, 
                               width=20, font=('Segoe UI', 10))
        search_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="🔍", width=3,
                  command=self.search_employee, style='Primary.TButton').pack(side=tk.LEFT)
        
        search_entry.bind('<Return>', lambda e: self.search_employee())
        
        # Панель навигации по месяцам
        nav_frame = ttk.Frame(header_frame)
        nav_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Кнопки навигации
        nav_buttons = ttk.Frame(nav_frame)
        nav_buttons.pack()
        
        ttk.Button(nav_buttons, text="⏪", width=3, 
                  command=self.prev_year, style='Primary.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_buttons, text="◀", width=3,
                  command=self.prev_month, style='Primary.TButton').pack(side=tk.LEFT, padx=2)
        
        # Текущий месяц
        self.month_label = tk.Label(nav_frame, 
                                   font=('Segoe UI', 14, 'bold'),
                                   fg=self.colors['primary'],
                                   bg=self.colors['card'])
        self.month_label.pack(pady=5)
        
        ttk.Button(nav_buttons, text="▶", width=3,
                  command=self.next_month, style='Primary.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_buttons, text="⏩", width=3,
                  command=self.next_year, style='Primary.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Button(nav_frame, text="📅 Сегодня", 
                  command=self.today_month, style='Success.TButton').pack(pady=5)
    
    def create_control_panel(self, parent):
        """Создание панели управления"""
        # Заголовок панели
        header = tk.Label(parent, text="Управление графиком", 
                         font=('Segoe UI', 16, 'bold'),
                         fg=self.colors['primary'],
                         bg=self.colors['card'])
        header.pack(pady=20)
        
        # Notebook для вкладок
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Вкладка 1: Работники
        employees_tab = ttk.Frame(notebook)
        notebook.add(employees_tab, text="👥 Работники")
        self.create_employees_tab(employees_tab)
        
        # Вкладка 2: Смены
        shifts_tab = ttk.Frame(notebook)
        notebook.add(shifts_tab, text="📝 Смены")
        self.create_shifts_tab(shifts_tab)
        
        # Вкладка 3: Типы смен
        shift_types_tab = ttk.Frame(notebook)
        notebook.add(shift_types_tab, text="🔄 Типы смен")
        self.create_shift_types_tab(shift_types_tab)
        
        # Вкладка 4: Категории
        categories_tab = ttk.Frame(notebook)
        notebook.add(categories_tab, text="🏷️ Категории")
        self.create_categories_tab(categories_tab)
        
        # Вкладка 5: Часы работы
        hours_tab = ttk.Frame(notebook)
        notebook.add(hours_tab, text="⏱️ Часы работы")
        self.create_hours_tab(hours_tab)
        
        # Вкладка 6: Быстрые действия
        actions_tab = ttk.Frame(notebook)
        notebook.add(actions_tab, text="⚡ Действия")
        self.create_actions_tab(actions_tab)
    
    def create_employees_tab(self, parent):
        """Вкладка управления работниками"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Добавление работника
        add_frame = ttk.LabelFrame(frame, text="Добавить работника", padding=10)
        add_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(add_frame, text="ФИО:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.employee_name = ttk.Entry(add_frame, font=('Segoe UI', 11))
        self.employee_name.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(add_frame, text="Категория:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.employee_category = ttk.Combobox(add_frame, values=self.categories, 
                                            font=('Segoe UI', 11), state="readonly")
        self.employee_category.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.employee_category.set(self.categories[0] if self.categories else "Другое")
        
        ttk.Button(add_frame, text="➕ Добавить", 
                  command=self.add_employee, style='Success.TButton').grid(row=0, column=2, rowspan=2, padx=5)
        
        # Кнопка управления категориями
        ttk.Button(add_frame, text="🏷️ Управление категориями", 
                  command=self.open_categories_manager, style='Primary.TButton').grid(row=0, column=3, rowspan=2, padx=5)
        
        # Список работников
        list_frame = ttk.LabelFrame(frame, text="Список работников", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview для отображения работников
        columns = ('id', 'name', 'category', 'shifts_count', 'hours_count')
        self.employees_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        # Настройка колонок
        self.employees_tree.heading('id', text='ID')
        self.employees_tree.heading('name', text='ФИО')
        self.employees_tree.heading('category', text='Категория')
        self.employees_tree.heading('shifts_count', text='Смен')
        self.employees_tree.heading('hours_count', text='Часов')
        
        self.employees_tree.column('id', width=50, anchor=tk.CENTER)
        self.employees_tree.column('name', width=180)
        self.employees_tree.column('category', width=120)
        self.employees_tree.column('shifts_count', width=80, anchor=tk.CENTER)
        self.employees_tree.column('hours_count', width=80, anchor=tk.CENTER)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.employees_tree.yview)
        self.employees_tree.configure(yscrollcommand=scrollbar.set)
        
        self.employees_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления работниками
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="✏️ Редактировать", 
                  command=self.edit_employee, style='Primary.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🗑️ Удалить", 
                  command=self.delete_employee, style='Danger.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🔄 Обновить", 
                  command=self.update_employees_list).pack(side=tk.LEFT, padx=2)
    
    def create_shifts_tab(self, parent):
        """Вкладка управления сменами"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Форма назначения смены
        form_frame = ttk.LabelFrame(frame, text="Назначить смену", padding=15)
        form_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Работник с категорией
        ttk.Label(form_frame, text="Работник:").grid(row=0, column=0, sticky=tk.W, pady=8)
        
        # Создаем фрейм для работника и категории
        employee_frame = ttk.Frame(form_frame)
        employee_frame.grid(row=0, column=1, columnspan=2, padx=5, pady=8, sticky=tk.EW)
        
        self.employee_var = tk.StringVar()
        self.employee_cb = ttk.Combobox(employee_frame, textvariable=self.employee_var, 
                                       font=('Segoe UI', 11), state="readonly")
        self.employee_cb.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Добавляем отображение категории
        self.employee_category_label = ttk.Label(employee_frame, text="", 
                                                font=('Segoe UI', 10), foreground=self.colors['secondary'])
        self.employee_category_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Привязываем изменение выбора работника
        self.employee_cb.bind('<<ComboboxSelected>>', self.on_employee_selected)
        
        # День
        ttk.Label(form_frame, text="День:").grid(row=1, column=0, sticky=tk.W, pady=8)
        self.day_var = tk.IntVar(value=datetime.now().day)
        self.day_cb = ttk.Combobox(form_frame, textvariable=self.day_var, 
                                  font=('Segoe UI', 11), state="readonly", width=10)
        self.day_cb.grid(row=1, column=1, padx=5, pady=8, sticky=tk.W)
        
        # Тип смены
        ttk.Label(form_frame, text="Тип смены:").grid(row=2, column=0, sticky=tk.W, pady=8)
        self.shift_var = tk.StringVar()
        self.shift_cb = ttk.Combobox(form_frame, textvariable=self.shift_var, 
                                    values=self.shift_types, 
                                    font=('Segoe UI', 11), state="readonly")
        self.shift_cb.grid(row=2, column=1, padx=5, pady=8, sticky=tk.EW)
        self.shift_cb.bind('<<ComboboxSelected>>', self.on_shift_type_selected)
        
        # Время смены
        time_frame = ttk.Frame(form_frame)
        time_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.EW)
        
        ttk.Label(time_frame, text="Время:").pack(side=tk.LEFT, padx=(0, 5))
        
        # Начало
        self.start_hour_var = tk.StringVar(value="08")
        self.start_hour = ttk.Combobox(time_frame, textvariable=self.start_hour_var, 
                                      values=[f"{i:02d}" for i in range(0, 24)], 
                                      width=3, font=('Segoe UI', 11), state="readonly")
        self.start_hour.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(time_frame, text=":").pack(side=tk.LEFT)
        
        self.start_minute_var = tk.StringVar(value="00")
        self.start_minute = ttk.Combobox(time_frame, textvariable=self.start_minute_var, 
                                        values=[f"{i:02d}" for i in range(0, 60, 5)], 
                                        width=3, font=('Segoe UI', 11), state="readonly")
        self.start_minute.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(time_frame, text="—").pack(side=tk.LEFT, padx=5)
        
        # Окончание
        self.end_hour_var = tk.StringVar(value="16")
        self.end_hour = ttk.Combobox(time_frame, textvariable=self.end_hour_var, 
                                    values=[f"{i:02d}" for i in range(0, 24)], 
                                    width=3, font=('Segoe UI', 11), state="readonly")
        self.end_hour.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(time_frame, text=":").pack(side=tk.LEFT)
        
        self.end_minute_var = tk.StringVar(value="00")
        self.end_minute = ttk.Combobox(time_frame, textvariable=self.end_minute_var, 
                                      values=[f"{i:02d}" for i in range(0, 60, 5)], 
                                      width=3, font=('Segoe UI', 11), state="readonly")
        self.end_minute.pack(side=tk.LEFT, padx=2)
        
        # Кнопки
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="✅ Назначить", 
                  command=self.assign_shift, style='Success.TButton', width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📋 Копировать", 
                  command=self.copy_shift, style='Primary.TButton', width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Удалить", 
                  command=self.delete_shift, style='Danger.TButton', width=15).pack(side=tk.LEFT, padx=5)
        
        # Статистика
        stats_frame = ttk.LabelFrame(frame, text="Статистика", padding=10)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.stats_label = tk.Label(stats_frame, text="Работников: 0 | Смен: 0", 
                                   font=('Segoe UI', 10), bg=self.colors['card'])
        self.stats_label.pack()
    
    def create_shift_types_tab(self, parent):
        """Вкладка управления типами смен"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Кнопка редактирования легенды смен
        legend_frame = ttk.LabelFrame(frame, text="Управление легендой смен", padding=10)
        legend_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(legend_frame, text="✏️ Редактировать легенду смен", 
                  command=self.edit_legend, style='Primary.TButton').pack(pady=5)
        
        # Добавление нового типа смены
        add_frame = ttk.LabelFrame(frame, text="Добавить новый тип смены", padding=10)
        add_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Название смены
        ttk.Label(add_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.new_shift_name = ttk.Entry(add_frame, font=('Segoe UI', 11))
        self.new_shift_name.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Время начала
        ttk.Label(add_frame, text="Начало:").grid(row=1, column=0, sticky=tk.W, pady=5)
        time_start_frame = ttk.Frame(add_frame)
        time_start_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.new_start_hour = ttk.Combobox(time_start_frame, values=[f"{i:02d}" for i in range(0, 24)], 
                                          width=3, font=('Segoe UI', 11), state="readonly")
        self.new_start_hour.set("08")
        self.new_start_hour.pack(side=tk.LEFT)
        
        ttk.Label(time_start_frame, text=":").pack(side=tk.LEFT)
        
        self.new_start_minute = ttk.Combobox(time_start_frame, values=[f"{i:02d}" for i in range(0, 60, 5)], 
                                            width=3, font=('Segoe UI', 11), state="readonly")
        self.new_start_minute.set("00")
        self.new_start_minute.pack(side=tk.LEFT)
        
        # Время окончания
        ttk.Label(add_frame, text="Окончание:").grid(row=2, column=0, sticky=tk.W, pady=5)
        time_end_frame = ttk.Frame(add_frame)
        time_end_frame.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.new_end_hour = ttk.Combobox(time_end_frame, values=[f"{i:02d}" for i in range(0, 24)], 
                                        width=3, font=('Segoe UI', 11), state="readonly")
        self.new_end_hour.set("16")
        self.new_end_hour.pack(side=tk.LEFT)
        
        ttk.Label(time_end_frame, text=":").pack(side=tk.LEFT)
        
        self.new_end_minute = ttk.Combobox(time_end_frame, values=[f"{i:02d}" for i in range(0, 60, 5)], 
                                          width=3, font=('Segoe UI', 11), state="readonly")
        self.new_end_minute.set("00")
        self.new_end_minute.pack(side=tk.LEFT)
        
        # Цвет
        ttk.Label(add_frame, text="Цвет:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.new_shift_color = tk.StringVar(value="#3498db")
        color_frame = ttk.Frame(add_frame)
        color_frame.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Entry(color_frame, textvariable=self.new_shift_color, width=10, 
                 font=('Segoe UI', 11)).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(color_frame, text="🎨 Выбрать", 
                  command=self.choose_new_shift_color, style='Primary.TButton').pack(side=tk.LEFT)
        
        # Кнопка добавления
        ttk.Button(add_frame, text="➕ Добавить тип смены", 
                  command=self.add_shift_type, style='Success.TButton').grid(row=4, column=0, columnspan=2, pady=10)
        
        # Список типов смен
        list_frame = ttk.LabelFrame(frame, text="Список типов смен", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview для отображения типов смен
        columns = ('name', 'start', 'end', 'color', 'hours')
        self.shift_types_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        # Настройка колонок
        self.shift_types_tree.heading('name', text='Название')
        self.shift_types_tree.heading('start', text='Начало')
        self.shift_types_tree.heading('end', text='Окончание')
        self.shift_types_tree.heading('color', text='Цвет')
        self.shift_types_tree.heading('hours', text='Часы')
        
        self.shift_types_tree.column('name', width=150)
        self.shift_types_tree.column('start', width=80, anchor=tk.CENTER)
        self.shift_types_tree.column('end', width=80, anchor=tk.CENTER)
        self.shift_types_tree.column('color', width=100, anchor=tk.CENTER)
        self.shift_types_tree.column('hours', width=80, anchor=tk.CENTER)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.shift_types_tree.yview)
        self.shift_types_tree.configure(yscrollcommand=scrollbar.set)
        
        self.shift_types_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления типами смен
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="🗑️ Удалить", 
                  command=self.delete_shift_type, style='Danger.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🔄 Обновить", 
                  command=self.update_shift_types_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="✏️ Редактировать", 
                  command=self.edit_shift_type, style='Primary.TButton').pack(side=tk.LEFT, padx=2)
    
    def create_categories_tab(self, parent):
        """Вкладка управления категориями"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Добавление категории
        add_frame = ttk.LabelFrame(frame, text="Добавить категорию", padding=10)
        add_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(add_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.new_category_name = ttk.Entry(add_frame, font=('Segoe UI', 11))
        self.new_category_name.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Button(add_frame, text="➕ Добавить", 
                  command=self.add_category, style='Success.TButton').grid(row=0, column=2, padx=5)
        
        # Список категорий
        list_frame = ttk.LabelFrame(frame, text="Список категорий", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview для отображения категорий
        columns = ('name', 'employees_count', 'total_hours')
        self.categories_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        # Настройка колонок
        self.categories_tree.heading('name', text='Название категории')
        self.categories_tree.heading('employees_count', text='Кол-во работников')
        self.categories_tree.heading('total_hours', text='Всего часов')
        
        self.categories_tree.column('name', width=200)
        self.categories_tree.column('employees_count', width=150, anchor=tk.CENTER)
        self.categories_tree.column('total_hours', width=120, anchor=tk.CENTER)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.categories_tree.yview)
        self.categories_tree.configure(yscrollcommand=scrollbar.set)
        
        self.categories_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления категориями
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="✏️ Редактировать", 
                  command=self.edit_category, style='Primary.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🗑️ Удалить", 
                  command=self.delete_category, style='Danger.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🔄 Обновить", 
                  command=self.update_categories_list).pack(side=tk.LEFT, padx=2)
        
        # Статистика по категориям
        stats_frame = ttk.LabelFrame(frame, text="Статистика по категориям", padding=10)
        stats_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.categories_stats_label = tk.Label(stats_frame, text="", 
                                              font=('Segoe UI', 10), bg=self.colors['card'])
        self.categories_stats_label.pack()
    
    def create_hours_tab(self, parent):
        """Вкладка учета отработанных часов"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        header_frame = ttk.Frame(frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(header_frame, text="⏱️ Учет отработанных часов", 
                font=('Segoe UI', 16, 'bold'),
                fg=self.colors['primary'],
                bg=self.colors['card']).pack()
        
        tk.Label(header_frame, text=f"За {self.get_month_name()} {self.current_year}", 
                font=('Segoe UI', 12),
                fg=self.colors['secondary'],
                bg=self.colors['card']).pack()
        
        # Инструменты
        tools_frame = ttk.LabelFrame(frame, text="Инструменты", padding=10)
        tools_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(tools_frame, text="🔄 Пересчитать часы", 
                  command=self.recalculate_hours, style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(tools_frame, text="📊 Детальная статистика", 
                  command=self.show_detailed_hours_report, style='Info.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(tools_frame, text="📋 Экспорт в CSV", 
                  command=self.export_hours_to_csv, style='Success.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(tools_frame, text="📄 Экспорт в TXT", 
                  command=self.export_hours_to_txt, style='Success.TButton').pack(side=tk.LEFT, padx=5)
        
        # Общая статистика
        summary_frame = ttk.LabelFrame(frame, text="Общая статистика", padding=10)
        summary_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.summary_label = tk.Label(summary_frame, text="", 
                                     font=('Segoe UI', 10),
                                     bg=self.colors['card'],
                                     justify=tk.LEFT)
        self.summary_label.pack()
        
        # Таблица часов
        list_frame = ttk.LabelFrame(frame, text="Отработанные часы по сотрудникам", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview для отображения часов
        columns = ('name', 'category', 'shifts', 'total_hours', 'avg_hours', 'salary')
        self.hours_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        # Настройка колонок
        self.hours_tree.heading('name', text='Сотрудник')
        self.hours_tree.heading('category', text='Категория')
        self.hours_tree.heading('shifts', text='Смен')
        self.hours_tree.heading('total_hours', text='Часов всего')
        self.hours_tree.heading('avg_hours', text='Часов в смену')
        self.hours_tree.heading('salary', text='Зарплата (пример)')
        
        self.hours_tree.column('name', width=180)
        self.hours_tree.column('category', width=120)
        self.hours_tree.column('shifts', width=80, anchor=tk.CENTER)
        self.hours_tree.column('total_hours', width=100, anchor=tk.CENTER)
        self.hours_tree.column('avg_hours', width=120, anchor=tk.CENTER)
        self.hours_tree.column('salary', width=150, anchor=tk.CENTER)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.hours_tree.yview)
        self.hours_tree.configure(yscrollcommand=scrollbar.set)
        
        self.hours_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Настройки расчета зарплаты
        settings_frame = ttk.LabelFrame(frame, text="Настройки расчета", padding=10)
        settings_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Label(settings_frame, text="Ставка за час:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.hourly_rate_var = tk.StringVar(value="350")
        ttk.Entry(settings_frame, textvariable=self.hourly_rate_var, width=10).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(settings_frame, text="₽").pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Button(settings_frame, text="💾 Применить ставку", 
                  command=self.apply_hourly_rate, style='Success.TButton').pack(side=tk.LEFT)
        
        ttk.Button(settings_frame, text="🔄 Обновить таблицу", 
                  command=self.update_hours_table, style='Primary.TButton').pack(side=tk.LEFT, padx=(10, 0))
    
    def create_actions_tab(self, parent):
        """Вкладка быстрых действий"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Подсказка о перетаскивании
        tip_frame = ttk.LabelFrame(frame, text="💡 Подсказка", padding=10)
        tip_frame.pack(fill=tk.X, pady=(0, 10))
        
        tip_label = tk.Label(tip_frame, 
                            text="Вы можете перетаскивать смены мышью в таблице графика!\nЗажмите левую кнопку мыши на смене и перетащите в нужную ячейку.",
                            font=('Segoe UI', 10), bg=self.colors['card'], justify=tk.LEFT)
        tip_label.pack()
        
        # Горячие клавиши
        hotkeys_frame = ttk.LabelFrame(frame, text="⌨️ Горячие клавиши", padding=10)
        hotkeys_frame.pack(fill=tk.X, pady=(0, 10))
        
        hotkeys_text = """
Ctrl+D или Delete - Удалить выбранную смену
Ctrl+Delete - Удалить все смены за день
Ctrl+S - Сохранить данные
Ctrl+Shift+S - Экспорт в TXT
Ctrl+G - Сгенерировать месяц
Ctrl+C - Копировать смену
Ctrl+V - Вставить смену
Ctrl+F - Применить фильтр категории
Ctrl+H - Статистика по часам
Esc - Снять выделение
Правая кнопка мыши - Контекстное меню
"""
        
        hotkeys_label = tk.Label(hotkeys_frame, text=hotkeys_text,
                                font=('Segoe UI', 10), bg=self.colors['card'], 
                                justify=tk.LEFT, anchor=tk.W)
        hotkeys_label.pack()
        
        # Кнопки быстрых действий
        actions = [
            ("📊 Сгенерировать месяц", self.generate_month, self.colors['primary']),
            ("🏷️ Статистика по категориям", self.show_detailed_category_stats, self.colors['info']),
            ("🗑️ Очистить месяц", self.clear_month, self.colors['warning']),
            ("⏱️ Статистика по часам", self.show_hours_statistics, self.colors['info']),
            ("💾 Сохранить данные", self.save_data, self.colors['success']),
            ("📤 Экспорт в TXT", self.export_to_txt, self.colors['secondary']),
            ("🎨 Настройки цветов", self.open_color_settings, self.colors['danger']),
            ("📈 Общая статистика", self.show_statistics, self.colors['info']),
            ("🖨️ Печать графика", self.print_schedule, self.colors['primary'])
        ]
        
        for i, (text, command, color) in enumerate(actions):
            btn = tk.Button(frame, text=text, font=('Segoe UI', 11), 
                           bg=color, fg='white', bd=0, padx=20, pady=15,
                           command=command, cursor='hand2', relief=tk.RAISED)
            btn.pack(fill=tk.X, pady=5)
            btn.bind("<Enter>", lambda e, b=btn: self.on_button_hover(b))
            btn.bind("<Leave>", lambda e, b=btn, c=color: self.on_button_leave(b, c))
    
    def create_schedule_panel(self, parent):
        """Создание панели с графиком смен"""
        # Заголовок
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(header_frame, text="График смен", 
                font=('Segoe UI', 16, 'bold'),
                fg=self.colors['primary'],
                bg=self.colors['card']).pack()
        
        # Панель быстрого управления
        quick_actions_frame = ttk.Frame(header_frame)
        quick_actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(quick_actions_frame, text="🗑️ Удалить выбранную", 
                  command=self.delete_selected_shift, 
                  style='Danger.TButton', width=15).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(quick_actions_frame, text="📋 Копировать", 
                  command=self.copy_selected_shift, 
                  style='Primary.TButton', width=15).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(quick_actions_frame, text="📎 Вставить", 
                  command=self.paste_shift, 
                  style='Success.TButton', width=15).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(quick_actions_frame, text="⏱️ Часы", 
                  command=self.show_hours_statistics, 
                  style='Info.TButton', width=15).pack(side=tk.LEFT, padx=2)
        
        # Легенда смен
        legend_frame = ttk.Frame(parent)
        legend_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(legend_frame, text="Легенда смен:", 
                font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W)
        
        legend_inner_frame = ttk.Frame(legend_frame)
        legend_inner_frame.pack(fill=tk.X, pady=5)
        
        # Автоматическое создание легенды из типов смен
        for shift_type, data in self.shift_types_data.items():
            color_frame = tk.Frame(legend_inner_frame, width=20, height=20, bg=data['color'])
            color_frame.pack(side=tk.LEFT, padx=(0, 5))
            color_frame.pack_propagate(False)
            
            # Показываем часы для смены
            hours = self.calculate_shift_hours_from_data(data)
            hours_text = f" ({hours}ч)" if hours > 0 else ""
            
            tk.Label(legend_inner_frame, text=f"{shift_type}{hours_text}", 
                    font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(0, 15))
        
        # Таблица графика смен
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Создаем Treeview для графика
        self.schedule_tree = ttk.Treeview(table_frame)
        
        # Привязываем правый клик для контекстного меню
        self.schedule_tree.bind('<Button-3>', self.show_context_menu)
        
        # Скроллбары
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.schedule_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.schedule_tree.xview)
        self.schedule_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Размещаем элементы
        self.schedule_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
    
    def create_status_bar(self, parent):
        """Создание статус бара"""
        self.status_bar = tk.Label(parent, 
                                  text="Готово | Ctrl+C: Копировать, Ctrl+V: Вставить, Delete: Удалить, Ctrl+H: Часы", 
                                  bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                  bg=self.colors['light'], fg=self.colors['dark'])
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def calculate_shift_hours_from_data(self, shift_data):
        """Расчет часов из данных смены"""
        try:
            start_time = shift_data.get('start', "00:00")
            end_time = shift_data.get('end', "00:00")
            
            if start_time == "00:00" and end_time == "00:00":
                return 0
            
            start_hour, start_minute = map(int, start_time.split(":"))
            end_hour, end_minute = map(int, end_time.split(":"))
            
            start_total = start_hour * 60 + start_minute
            end_total = end_hour * 60 + end_minute
            
            if end_total < start_total:  # Смена через полночь
                end_total += 24 * 60
            
            total_minutes = end_total - start_total
            return round(total_minutes / 60, 1)
        except (ValueError, AttributeError):
            return 0
    
    def calculate_hours(self):
        """Расчет часов для всех сотрудников за текущий месяц"""
        self.hours_counter = {}
        
        # Создаем запись для каждого сотрудника
        for employee in self.employees:
            self.hours_counter[employee["id"]] = {
                "name": employee["name"],
                "total_hours": 0,
                "shifts_count": 0,
                "category": employee.get("category", "Другое")
            }
        
        # Рассчитываем часы для текущего месяца
        for shift in self.shifts:
            try:
                shift_date = datetime.strptime(shift["date"], "%Y-%m-%d").date()
                if shift_date.year == self.current_year and shift_date.month == self.current_month:
                    employee_id = shift["employee_id"]
                    hours = self.calculate_shift_hours(shift)
                    
                    if employee_id in self.hours_counter:
                        self.hours_counter[employee_id]["total_hours"] += hours
                        self.hours_counter[employee_id]["shifts_count"] += 1
                    else:
                        # Если сотрудник не был в списке (например, удален)
                        employee = next((emp for emp in self.employees if emp["id"] == employee_id), None)
                        if employee:
                            self.hours_counter[employee_id] = {
                                "name": employee["name"],
                                "total_hours": hours,
                                "shifts_count": 1,
                                "category": employee.get("category", "Другое")
                            }
            except (ValueError, KeyError):
                continue
    
    def calculate_shift_hours(self, shift):
        """Расчет часов для одной смены"""
        try:
            start_time = shift.get("start_time", "00:00")
            end_time = shift.get("end_time", "00:00")
            
            if start_time == "00:00" and end_time == "00:00":
                return 0
            
            start_hour, start_minute = map(int, start_time.split(":"))
            end_hour, end_minute = map(int, end_time.split(":"))
            
            # Учитываем переход через полночь
            start_total = start_hour * 60 + start_minute
            end_total = end_hour * 60 + end_minute
            
            if end_total < start_total:  # Смена через полночь
                end_total += 24 * 60
            
            total_minutes = end_total - start_total
            return round(total_minutes / 60, 2)  # Часы с двумя знаками после запятой
        except (ValueError, AttributeError):
            return 0
    
    def recalculate_hours(self):
        """Пересчет часов работы"""
        self.calculate_hours()
        self.update_hours_table()
        self.update_schedule_display()
        messagebox.showinfo("Успех", "Часы пересчитаны", parent=self.root)
    
    def update_hours_table(self):
        """Обновление таблицы с часами работы"""
        # Очищаем таблицу
        for item in self.hours_tree.get_children():
            self.hours_tree.delete(item)
        
        # Обновляем статистику
        total_shifts = 0
        total_hours = 0
        employees_with_shifts = 0
        
        # Получаем ставку за час
        try:
            hourly_rate = float(self.hourly_rate_var.get())
        except ValueError:
            hourly_rate = 350
        
        # Сортируем сотрудников по количеству часов
        sorted_employees = sorted(
            self.hours_counter.items(),
            key=lambda x: x[1]["total_hours"],
            reverse=True
        )
        
        for employee_id, data in sorted_employees:
            if data["shifts_count"] > 0:
                name = data["name"]
                category = data["category"]
                shifts = data["shifts_count"]
                hours = data["total_hours"]
                
                # Расчет средней продолжительности смены
                avg_hours = hours / shifts if shifts > 0 else 0
                
                # Расчет примерной зарплаты
                salary = hours * hourly_rate
                
                self.hours_tree.insert('', tk.END, values=(
                    name,
                    category,
                    shifts,
                    f"{hours:.2f} ч",
                    f"{avg_hours:.2f} ч",
                    f"{salary:.2f} ₽"
                ))
                
                total_shifts += shifts
                total_hours += hours
                employees_with_shifts += 1
        
        # Обновляем общую статистику
        avg_hours_per_employee = total_hours / employees_with_shifts if employees_with_shifts > 0 else 0
        avg_shifts_per_employee = total_shifts / employees_with_shifts if employees_with_shifts > 0 else 0
        
        summary_text = f"""
📊 Общая статистика за {self.get_month_name()} {self.current_year}:

👥 Сотрудников с сменами: {employees_with_shifts}
📅 Всего смен: {total_shifts}
⏱️ Всего часов: {total_hours:.2f}
📈 Среднее на сотрудника: {avg_shifts_per_employee:.1f} смен, {avg_hours_per_employee:.1f} часов
💰 Общие затраты (примерно): {total_hours * hourly_rate:.2f} ₽
"""
        self.summary_label.config(text=summary_text)
    
    def show_detailed_hours_report(self):
        """Показать детальный отчет по часам"""
        report_window = tk.Toplevel(self.root)
        report_window.title("📊 Детальный отчет по часам работы")
        report_window.geometry("700x600")
        report_window.transient(self.root)
        
        frame = ttk.Frame(report_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем текстовое поле с прокруткой
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        report_text = self.generate_detailed_hours_report()
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 10))
        text_widget.insert(1.0, report_text)
        text_widget.config(state=tk.DISABLED, bg=self.colors['card'])
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="📋 Копировать", 
                  command=lambda: self.copy_report_to_clipboard(report_text), 
                  style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="💾 Сохранить", 
                  command=lambda: self.save_hours_report(report_text), 
                  style='Success.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="❌ Закрыть", 
                  command=report_window.destroy, 
                  style='Danger.TButton').pack(side=tk.LEFT, padx=5)
    
    def generate_detailed_hours_report(self):
        """Генерация детального отчета по часам"""
        report = f"""
{'='*70}
                ОТЧЕТ ПО ОТРАБОТАННЫМ ЧАСАМ
                     {self.get_month_name()} {self.current_year}
{'='*70}

Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}

"""
        # Статистика по категориям
        category_stats = {}
        for data in self.hours_counter.values():
            if data["shifts_count"] > 0:
                category = data["category"]
                if category not in category_stats:
                    category_stats[category] = {
                        "employees": 0,
                        "shifts": 0,
                        "hours": 0
                    }
                category_stats[category]["employees"] += 1
                category_stats[category]["shifts"] += data["shifts_count"]
                category_stats[category]["hours"] += data["total_hours"]
        
        if category_stats:
            report += "СТАТИСТИКА ПО КАТЕГОРИЯМ:\n"
            report += "-" * 70 + "\n"
            
            for category, stats in sorted(category_stats.items(), 
                                         key=lambda x: x[1]["hours"], reverse=True):
                avg_hours = stats["hours"] / stats["employees"] if stats["employees"] > 0 else 0
                report += (f"{category:<15} | {stats['employees']:>3} чел. | "
                          f"{stats['shifts']:>4} смен | {stats['hours']:>7.2f} ч | "
                          f"Среднее: {avg_hours:>6.2f} ч/чел\n")
            
            report += "\n"
        
        # Детали по сотрудникам
        report += "ДЕТАЛИ ПО СОТРУДНИКАМ:\n"
        report += "-" * 70 + "\n"
        
        try:
            hourly_rate = float(self.hourly_rate_var.get())
        except ValueError:
            hourly_rate = 350
        
        sorted_employees = sorted(
            self.hours_counter.items(),
            key=lambda x: x[1]["total_hours"],
            reverse=True
        )
        
        for employee_id, data in sorted_employees:
            if data["shifts_count"] > 0:
                salary = data["total_hours"] * hourly_rate
                avg_hours = data["total_hours"] / data["shifts_count"] if data["shifts_count"] > 0 else 0
                
                report += (f"{data['name'][:25]:<25} | {data['category'][:15]:<15} | "
                          f"{data['shifts_count']:>3} смен | {data['total_hours']:>6.2f} ч | "
                          f"Среднее: {avg_hours:>5.2f} ч/смену | {salary:>10.2f} ₽\n")
        
        # Общая статистика
        total_shifts = sum(data["shifts_count"] for data in self.hours_counter.values())
        total_hours = sum(data["total_hours"] for data in self.hours_counter.values())
        employees_with_shifts = sum(1 for data in self.hours_counter.values() if data["shifts_count"] > 0)
        
        report += "\n" + "="*70 + "\n"
        report += "ОБЩАЯ СТАТИСТИКА:\n"
        report += f"Всего сотрудников с сменами: {employees_with_shifts}\n"
        report += f"Всего смен: {total_shifts}\n"
        report += f"Всего отработано часов: {total_hours:.2f}\n"
        
        if employees_with_shifts > 0:
            avg_shifts = total_shifts / employees_with_shifts
            avg_hours_per_emp = total_hours / employees_with_shifts
            report += f"Среднее на сотрудника: {avg_shifts:.1f} смен, {avg_hours_per_emp:.1f} часов\n"
        
        total_salary = total_hours * hourly_rate
        report += f"Общие затраты (по ставке {hourly_rate} ₽/час): {total_salary:.2f} ₽\n"
        report += "="*70
        
        return report
    
    def copy_report_to_clipboard(self, report_text):
        """Копирование отчета в буфер обмена"""
        self.root.clipboard_clear()
        self.root.clipboard_append(report_text)
        messagebox.showinfo("Успех", "Отчет скопирован в буфер обмена", parent=self.root)
    
    def save_hours_report(self, report_text):
        """Сохранение отчета в файл"""
        try:
            filename = f"отчет_часы_{self.current_year}_{self.current_month:02d}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report_text)
            messagebox.showinfo("Успех", f"Отчет сохранен в файл:\n{filename}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить отчет: {str(e)}", parent=self.root)
    
    def export_hours_to_csv(self):
        """Экспорт данных по часам в CSV"""
        try:
            filename = f"часы_{self.current_year}_{self.current_month:02d}.csv"
            
            with open(filename, 'w', encoding='utf-8-sig') as f:
                # Заголовок
                f.write("Сотрудник;Категория;Смен;Часов всего;Часов в смену;Зарплата\n")
                
                # Данные
                for employee_id, data in self.hours_counter.items():
                    if data["shifts_count"] > 0:
                        try:
                            hourly_rate = float(self.hourly_rate_var.get())
                        except ValueError:
                            hourly_rate = 350
                        
                        avg_hours = data["total_hours"] / data["shifts_count"] if data["shifts_count"] > 0 else 0
                        salary = data["total_hours"] * hourly_rate
                        
                        f.write(f"{data['name']};{data['category']};{data['shifts_count']};"
                               f"{data['total_hours']:.2f};{avg_hours:.2f};{salary:.2f}\n")
            
            messagebox.showinfo("Успех", f"Данные экспортированы в файл:\n{filename}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {str(e)}", parent=self.root)
    
    def export_hours_to_txt(self):
        """Экспорт данных по часам в TXT"""
        try:
            filename = f"часы_{self.current_year}_{self.current_month:02d}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Отчет по отработанным часам\n")
                f.write(f"{self.get_month_name()} {self.current_year}\n")
                f.write("=" * 50 + "\n\n")
                
                try:
                    hourly_rate = float(self.hourly_rate_var.get())
                except ValueError:
                    hourly_rate = 350
                
                # Данные
                f.write("Сотрудник\tКатегория\tСмен\tЧасы\tСреднее\tЗарплата\n")
                f.write("-" * 70 + "\n")
                
                for employee_id, data in self.hours_counter.items():
                    if data["shifts_count"] > 0:
                        avg_hours = data["total_hours"] / data["shifts_count"] if data["shifts_count"] > 0 else 0
                        salary = data["total_hours"] * hourly_rate
                        
                        f.write(f"{data['name'][:20]:<20}\t{data['category'][:10]:<10}\t"
                               f"{data['shifts_count']:<4}\t{data['total_hours']:<6.1f}\t"
                               f"{avg_hours:<6.1f}\t{salary:.2f}\n")
            
            messagebox.showinfo("Успех", f"Данные экспортированы в файл:\n{filename}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {str(e)}", parent=self.root)
    
    def apply_hourly_rate(self):
        """Применение новой ставки за час"""
        try:
            rate = float(self.hourly_rate_var.get())
            if rate <= 0:
                raise ValueError
            self.update_hours_table()
            messagebox.showinfo("Успех", f"Ставка установлена: {rate} ₽/час", parent=self.root)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число для ставки", parent=self.root)
            self.hourly_rate_var.set("350")
    
    def show_hours_statistics(self):
        """Показать статистику по часам (для горячей клавиши)"""
        self.update_hours_table()
        
        # Показываем всплывающее окно с краткой статистикой
        total_hours = sum(data["total_hours"] for data in self.hours_counter.values())
        employees_with_shifts = sum(1 for data in self.hours_counter.values() if data["shifts_count"] > 0)
        
        stats_text = f"⏱️ Статистика за {self.get_month_name()} {self.current_year}:\n\n"
        stats_text += f"• Сотрудников с сменами: {employees_with_shifts}\n"
        stats_text += f"• Всего отработано часов: {total_hours:.2f}\n"
        
        if employees_with_shifts > 0:
            avg_hours = total_hours / employees_with_shifts
            stats_text += f"• Среднее на сотрудника: {avg_hours:.1f} часов\n\n"
        
        # Топ-5 сотрудников по часам
        sorted_employees = sorted(
            self.hours_counter.items(),
            key=lambda x: x[1]["total_hours"],
            reverse=True
        )[:5]
        
        if sorted_employees:
            stats_text += "Топ-5 сотрудников по часам:\n"
            for i, (emp_id, data) in enumerate(sorted_employees, 1):
                if data["shifts_count"] > 0:
                    stats_text += f"{i}. {data['name']}: {data['total_hours']:.1f} ч\n"
        
        messagebox.showinfo("Статистика по часам", stats_text, parent=self.root)
    
    def generate_shift_types_list(self):
        """Генерация списка типов смен для отображения"""
        shift_types_list = []
        for shift_type, data in self.shift_types_data.items():
            start = data.get('start', '00:00')
            end = data.get('end', '00:00')
            hours = self.calculate_shift_hours_from_data(data)
            hours_text = f" ({hours}ч)" if hours > 0 else ""
            
            if start == '00:00' and end == '00:00':
                shift_types_list.append(f"{shift_type}{hours_text}")
            else:
                shift_types_list.append(f"{shift_type}{hours_text} ({start}-{end})")
        return shift_types_list
    
    def add_employee(self):
        """Добавление нового работника"""
        name = self.employee_name.get().strip()
        category = self.employee_category.get().strip()
        
        if not name:
            messagebox.showwarning("Внимание", "Введите ФИО работника", parent=self.root)
            return
        
        if not category:
            category = "Другое"
        
        if any(emp["name"] == name for emp in self.employees):
            messagebox.showwarning("Внимание", "Работник с таким ФИО уже существует", parent=self.root)
            return
        
        employee_id = len(self.employees) + 1
        self.employees.append({
            "id": employee_id,
            "name": name,
            "category": category,
            "hire_date": datetime.now().strftime("%Y-%m-%d")
        })
        
        self.employee_name.delete(0, tk.END)
        self.update_employees_list()
        self.update_schedule_display()
        
        messagebox.showinfo("Успех", f"Работник {name} добавлен в категорию '{category}'", parent=self.root)
    
    def edit_employee(self):
        """Редактирование выбранного работника"""
        selection = self.employees_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите работника для редактирования", parent=self.root)
            return
        
        item = self.employees_tree.item(selection[0])
        employee_id = item['values'][0]
        
        employee = next((emp for emp in self.employees if emp["id"] == employee_id), None)
        if not employee:
            messagebox.showwarning("Ошибка", "Работник не найден", parent=self.root)
            return
        
        # Окно редактирования
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Редактирование работника: {employee['name']}")
        edit_window.geometry("400x250")
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        main_frame = ttk.Frame(edit_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="ФИО:", font=('Segoe UI', 11)).pack(anchor=tk.W, pady=(0, 5))
        name_var = tk.StringVar(value=employee["name"])
        name_entry = ttk.Entry(main_frame, textvariable=name_var, font=('Segoe UI', 11))
        name_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Категория:", font=('Segoe UI', 11)).pack(anchor=tk.W, pady=(0, 5))
        category_var = tk.StringVar(value=employee.get("category", "Другое"))
        category_combo = ttk.Combobox(main_frame, textvariable=category_var, 
                                     values=self.categories, font=('Segoe UI', 11), state="readonly")
        category_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Дата приема
        ttk.Label(main_frame, text="Дата приема:", font=('Segoe UI', 11)).pack(anchor=tk.W, pady=(0, 5))
        hire_date_var = tk.StringVar(value=employee.get("hire_date", datetime.now().strftime("%Y-%m-%d")))
        hire_date_entry = ttk.Entry(main_frame, textvariable=hire_date_var, font=('Segoe UI', 11))
        hire_date_entry.pack(fill=tk.X, pady=(0, 10))
        
        def save_changes():
            new_name = name_var.get().strip()
            new_category = category_var.get()
            new_hire_date = hire_date_var.get()
            
            if not new_name:
                messagebox.showwarning("Внимание", "Введите ФИО работника", parent=edit_window)
                return
            
            # Проверяем уникальность имени (кроме текущего работника)
            if any(emp["name"] == new_name and emp["id"] != employee_id for emp in self.employees):
                messagebox.showwarning("Внимание", "Работник с таким ФИО уже существует", parent=edit_window)
                return
            
            # Обновляем данные работника
            employee["name"] = new_name
            employee["category"] = new_category
            employee["hire_date"] = new_hire_date
            
            # Обновляем смены работника
            for shift in self.shifts:
                if shift["employee_id"] == employee_id:
                    shift["employee_name"] = new_name
                    shift["category"] = new_category
            
            # Пересчитываем часы
            self.calculate_hours()
            
            # Обновляем отображение
            self.update_employees_list()
            self.update_schedule_display()
            self.update_hours_table()
            
            edit_window.destroy()
            messagebox.showinfo("Успех", "Данные работника обновлены", parent=self.root)
        
        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="💾 Сохранить", 
                  command=save_changes, style='Success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Отмена", 
                  command=edit_window.destroy, style='Danger.TButton').pack(side=tk.LEFT, padx=5)
    
    def delete_employee(self):
        """Удаление работника"""
        selection = self.employees_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите работника для удаления", parent=self.root)
            return
        
        item = self.employees_tree.item(selection[0])
        employee_id = item['values'][0]
        employee_name = item['values'][1]
        
        if messagebox.askyesno("Подтверждение", 
                              f"Удалить работника {employee_name}?\nВсе его смены также будут удалены.", 
                              parent=self.root):
            # Удаляем работника
            self.employees = [emp for emp in self.employees if emp["id"] != employee_id]
            
            # Удаляем смены работника
            self.shifts = [shift for shift in self.shifts if shift["employee_id"] != employee_id]
            
            # Пересчитываем часы
            self.calculate_hours()
            
            # Обновляем отображение
            self.update_employees_list()
            self.update_schedule_display()
            self.update_hours_table()
            
            messagebox.showinfo("Успех", f"Работник {employee_name} удален", parent=self.root)
    
    def update_employees_list(self):
        """Обновление списка работников"""
        # Обновляем Combobox
        employee_names = [emp["name"] for emp in self.employees]
        self.employee_cb['values'] = employee_names
        
        # Обновляем Treeview с работниками
        for item in self.employees_tree.get_children():
            self.employees_tree.delete(item)
        
        for emp in self.employees:
            # Считаем количество смен и часов у работника
            shift_count = sum(1 for s in self.shifts if s["employee_id"] == emp["id"])
            hours_count = self.hours_counter.get(emp["id"], {}).get("total_hours", 0)
            
            self.employees_tree.insert('', tk.END, values=(
                emp["id"], 
                emp["name"], 
                emp.get("category", "Другое"), 
                shift_count,
                f"{hours_count:.1f}"
            ))
    
    def on_employee_selected(self, event=None):
        """При выборе работника показываем его категорию"""
        employee_name = self.employee_var.get()
        if employee_name:
            employee = next((emp for emp in self.employees if emp["name"] == employee_name), None)
            if employee:
                category = employee.get("category", "Другое")
                self.employee_category_label.config(text=f"[{category}]")
            else:
                self.employee_category_label.config(text="")
    
    def on_shift_type_selected(self, event):
        """При выборе типа смены обновляем время"""
        selected = self.shift_var.get()
        
        # Извлекаем название смены (без времени в скобках)
        if '(' in selected:
            shift_name = selected.split('(')[0].strip().split(' ')[0]  # Убираем также часы если есть
        else:
            shift_name = selected.split(' ')[0]  # Убираем часы если есть
        
        # Находим данные смены
        shift_data = self.shift_types_data.get(shift_name)
        if shift_data:
            # Устанавливаем время
            if ':' in shift_data['start']:
                start_hour, start_minute = shift_data['start'].split(':')
                self.start_hour_var.set(start_hour)
                self.start_minute_var.set(start_minute)
            
            if ':' in shift_data['end']:
                end_hour, end_minute = shift_data['end'].split(':')
                self.end_hour_var.set(end_hour)
                self.end_minute_var.set(end_minute)
    
    def assign_shift(self):
        """Назначение смены"""
        employee_name = self.employee_var.get()
        day = self.day_var.get()
        shift_type_full = self.shift_var.get()
        
        if not employee_name or not shift_type_full:
            messagebox.showwarning("Внимание", "Выберите работника и тип смены", parent=self.root)
            return
        
        # Извлекаем название смены (без времени в скобках и часов)
        if '(' in shift_type_full:
            shift_name = shift_type_full.split('(')[0].strip()
        else:
            shift_name = shift_type_full
        
        # Убираем упоминание часов если есть
        if 'ч' in shift_name:
            shift_name = shift_name.split('ч')[0].strip()
        
        # Находим данные работника
        employee = next((emp for emp in self.employees if emp["name"] == employee_name), None)
        if not employee:
            messagebox.showwarning("Ошибка", "Работник не найден", parent=self.root)
            return
        
        # Создаем дату
        shift_date = date(self.current_year, self.current_month, day)
        
        # Проверяем, есть ли уже смена у этого работника в этот день
        existing_shift = next((s for s in self.shifts 
                              if s["employee_name"] == employee_name and 
                              s["date"] == shift_date.strftime("%Y-%m-%d")), None)
        
        if existing_shift:
            if not messagebox.askyesno("Подтверждение", 
                                      f"У работника {employee_name} уже есть смена на {day} число. Заменить?", 
                                      parent=self.root):
                return
            
            # Удаляем старую смену
            self.shifts = [s for s in self.shifts if not (
                s["employee_name"] == employee_name and 
                s["date"] == shift_date.strftime("%Y-%m-%d")
            )]
        
        # Получаем время из полей ввода
        start_time = f"{self.start_hour_var.get()}:{self.start_minute_var.get()}"
        end_time = f"{self.end_hour_var.get()}:{self.end_minute_var.get()}"
        
        # Создаем смену
        shift = {
            "id": len(self.shifts) + 1,
            "employee_id": employee["id"],
            "employee_name": employee_name,
            "date": shift_date.strftime("%Y-%m-%d"),
            "shift_type": shift_name,
            "start_time": start_time,
            "end_time": end_time,
            "category": employee.get("category", "Другое")
        }
        
        self.shifts.append(shift)
        
        # Пересчитываем часы
        self.calculate_hours()
        
        # Обновляем отображение
        self.update_schedule_display()
        
        # Показываем информацию о часах
        hours = self.calculate_shift_hours(shift)
        messagebox.showinfo("Успех", 
                          f"Смена назначена работнику {employee_name} на {day} число\n"
                          f"Продолжительность смены: {hours} часов", 
                          parent=self.root)
    
    def copy_shift(self):
        """Копирование смены из формы"""
        employee_name = self.employee_var.get()
        day = self.day_var.get()
        shift_type_full = self.shift_var.get()
        
        if not employee_name or not shift_type_full:
            messagebox.showwarning("Внимание", "Выберите работника и тип смены", parent=self.root)
            return
        
        # Сохраняем данные смены для вставки
        self.copied_shift = {
            "employee_name": employee_name,
            "day": day,
            "shift_type": shift_type_full,
            "start_time": f"{self.start_hour_var.get()}:{self.start_minute_var.get()}",
            "end_time": f"{self.end_hour_var.get()}:{self.end_minute_var.get()}"
        }
        
        messagebox.showinfo("Успех", "Смена скопирована. Теперь вы можете вставить ее в другую ячейку таблицы.", parent=self.root)
    
    def delete_shift(self):
        """Удаление смены через форму"""
        employee_name = self.employee_var.get()
        day = self.day_var.get()
        
        if not employee_name:
            messagebox.showwarning("Внимание", "Выберите работника", parent=self.root)
            return
        
        # Находим смену
        shift_date = date(self.current_year, self.current_month, day)
        shift = next((s for s in self.shifts 
                     if s["employee_name"] == employee_name and 
                     s["date"] == shift_date.strftime("%Y-%m-%d")), None)
        
        if not shift:
            messagebox.showwarning("Внимание", f"У работника {employee_name} нет смены на {day} число", 
                                 parent=self.root)
            return
        
        if messagebox.askyesno("Подтверждение", 
                              f"Удалить смену у {employee_name} на {day} число?", 
                              parent=self.root):
            self.shifts.remove(shift)
            
            # Пересчитываем часы
            self.calculate_hours()
            
            self.update_schedule_display()
            messagebox.showinfo("Успех", "Смена удалена", parent=self.root)
    
    def add_category(self):
        """Добавление новой категории"""
        category_name = self.new_category_name.get().strip()
        
        if not category_name:
            messagebox.showwarning("Внимание", "Введите название категории", parent=self.root)
            return
        
        if category_name in self.categories:
            messagebox.showwarning("Внимание", "Категория с таким названием уже существует", parent=self.root)
            return
        
        self.categories.append(category_name)
        self.new_category_name.delete(0, tk.END)
        
        # Обновляем комбобоксы
        self.update_category_widgets()
        
        messagebox.showinfo("Успех", f"Категория '{category_name}' добавлена", parent=self.root)
    
    def edit_category(self):
        """Редактирование выбранной категории"""
        selection = self.categories_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите категорию для редактирования", parent=self.root)
            return
        
        item = self.categories_tree.item(selection[0])
        old_name = item['values'][0]
        
        # Окно редактирования
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Редактирование категории: {old_name}")
        edit_window.geometry("400x200")
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        main_frame = ttk.Frame(edit_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Название категории:", 
                 font=('Segoe UI', 11)).pack(anchor=tk.W, pady=(0, 5))
        
        name_var = tk.StringVar(value=old_name)
        name_entry = ttk.Entry(main_frame, textvariable=name_var, font=('Segoe UI', 11))
        name_entry.pack(fill=tk.X, pady=(0, 15))
        
        def save_changes():
            new_name = name_var.get().strip()
            
            if not new_name:
                messagebox.showwarning("Внимание", "Введите название категории", parent=edit_window)
                return
            
            if new_name != old_name and new_name in self.categories:
                messagebox.showwarning("Внимание", "Категория с таким названием уже существует", parent=edit_window)
                return
            
            # Обновляем название категории
            index = self.categories.index(old_name)
            self.categories[index] = new_name
            
            # Обновляем работников в этой категории
            for employee in self.employees:
                if employee.get("category") == old_name:
                    employee["category"] = new_name
            
            # Обновляем смены в этой категории
            for shift in self.shifts:
                if shift.get("category") == old_name:
                    shift["category"] = new_name
            
            # Пересчитываем часы
            self.calculate_hours()
            
            # Обновляем комбобоксы
            self.update_category_widgets()
            
            edit_window.destroy()
            messagebox.showinfo("Успех", f"Категория переименована в '{new_name}'", parent=self.root)
        
        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="💾 Сохранить", 
                  command=save_changes, style='Success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Отмена", 
                  command=edit_window.destroy, style='Danger.TButton').pack(side=tk.LEFT, padx=5)
    
    def delete_category(self):
        """Удаление выбранной категории"""
        selection = self.categories_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите категорию для удаления", parent=self.root)
            return
        
        item = self.categories_tree.item(selection[0])
        category_name = item['values'][0]
        
        # Проверяем, есть ли работники в этой категории
        employees_in_category = [emp for emp in self.employees if emp.get("category") == category_name]
        
        if employees_in_category:
            messagebox.showwarning("Внимание", 
                                 f"В категории '{category_name}' есть работники. Сначала переместите их в другие категории.", 
                                 parent=self.root)
            return
        
        if messagebox.askyesno("Подтверждение", 
                              f"Удалить категорию '{category_name}'?", 
                              parent=self.root):
            self.categories.remove(category_name)
            self.update_category_widgets()
            messagebox.showinfo("Успех", f"Категория '{category_name}' удалена", parent=self.root)
    
    def update_category_widgets(self):
        """Обновление виджетов связанных с категориями"""
        # Обновляем комбобокс фильтра
        self.category_filter['values'] = ["Все категории"] + self.categories
        
        # Обновляем комбобокс добавления работника
        self.employee_category['values'] = self.categories
        if self.categories:
            self.employee_category.set(self.categories[0])
        
        # Обновляем списки
        self.update_categories_list()
        self.update_employees_list()
    
    def update_categories_list(self):
        """Обновление списка категорий"""
        # Очищаем дерево
        for item in self.categories_tree.get_children():
            self.categories_tree.delete(item)
        
        # Подсчитываем работников и часы в каждой категории
        category_stats = {}
        for category in self.categories:
            employees_in_category = [emp for emp in self.employees if emp.get("category") == category]
            category_stats[category] = {
                "employees": len(employees_in_category),
                "total_hours": 0
            }
            
            # Считаем часы по категории
            for emp in employees_in_category:
                if emp["id"] in self.hours_counter:
                    category_stats[category]["total_hours"] += self.hours_counter[emp["id"]]["total_hours"]
        
        # Добавляем категории в дерево
        for category, stats in category_stats.items():
            self.categories_tree.insert('', tk.END, values=(
                category, 
                stats["employees"], 
                f"{stats['total_hours']:.1f} ч"
            ))
        
        # Обновляем статистику
        self.update_categories_stats()
    
    def update_categories_stats(self):
        """Обновление статистики по категориям"""
        total_employees = len(self.employees)
        
        if total_employees == 0:
            self.categories_stats_label.config(text="Нет работников в системе")
            return
        
        stats_text = "📊 Распределение по категориям:\n"
        category_counts = {}
        category_hours = {}
        
        for category in self.categories:
            count = sum(1 for emp in self.employees if emp.get("category") == category)
            if count > 0:
                category_counts[category] = count
                
                # Считаем часы по категории
                hours = 0
                for emp in self.employees:
                    if emp.get("category") == category and emp["id"] in self.hours_counter:
                        hours += self.hours_counter[emp["id"]]["total_hours"]
                category_hours[category] = hours
        
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_employees) * 100
            hours = category_hours.get(category, 0)
            stats_text += f"  • {category}: {count} чел. ({percentage:.1f}%) - {hours:.1f} ч\n"
        
        self.categories_stats_label.config(text=stats_text)
    
    def open_categories_manager(self):
        """Открытие менеджера категорий"""
        # Создаем новое окно для управления категориями
        manager_window = tk.Toplevel(self.root)
        manager_window.title("🏷️ Управление категориями работников")
        manager_window.geometry("600x500")
        manager_window.transient(self.root)
        manager_window.grab_set()
        
        main_frame = ttk.Frame(manager_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="Управление категориями работников", 
                font=('Segoe UI', 16, 'bold')).pack(pady=(0, 20))
        
        # Статистика
        stats_frame = ttk.LabelFrame(main_frame, text="📈 Статистика", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        stats_label = tk.Label(stats_frame, font=('Segoe UI', 10), 
                              bg=self.colors['card'], justify=tk.LEFT)
        stats_label.pack()
        
        # Обновляем статистику
        self.update_manager_stats(stats_label)
        
        # Быстрое управление
        quick_frame = ttk.LabelFrame(main_frame, text="⚡ Быстрые действия", padding=10)
        quick_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Button(quick_frame, text="🔄 Переместить всех в категорию", 
                  command=lambda: self.move_all_to_category(manager_window), 
                  style='Primary.TButton').pack(fill=tk.X, pady=5)
        
        ttk.Button(quick_frame, text="📊 Показать детальную статистику", 
                  command=self.show_detailed_category_stats, 
                  style='Info.TButton').pack(fill=tk.X, pady=5)
        
        # Список категорий
        list_frame = ttk.LabelFrame(main_frame, text="📋 Категории", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview для категорий
        columns = ('name', 'employees_count', 'total_hours')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        tree.heading('name', text='Название категории')
        tree.heading('employees_count', text='Кол-во работников')
        tree.heading('total_hours', text='Всего часов')
        
        tree.column('name', width=250)
        tree.column('employees_count', width=150, anchor=tk.CENTER)
        tree.column('total_hours', width=120, anchor=tk.CENTER)
        
        # Заполняем данными
        for category in self.categories:
            count = sum(1 for emp in self.employees if emp.get("category") == category)
            # Считаем часы по категории
            hours = 0
            for emp in self.employees:
                if emp.get("category") == category and emp["id"] in self.hours_counter:
                    hours += self.hours_counter[emp["id"]]["total_hours"]
            
            tree.insert('', tk.END, values=(category, count, f"{hours:.1f} ч"))
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="➕ Добавить", 
                  command=lambda: self.add_category_from_manager(manager_window, tree), 
                  style='Success.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="✏️ Редактировать", 
                  command=lambda: self.edit_category_from_manager(manager_window, tree), 
                  style='Primary.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🗑️ Удалить", 
                  command=lambda: self.delete_category_from_manager(tree), 
                  style='Danger.TButton').pack(side=tk.LEFT, padx=2)
    
    def update_manager_stats(self, label):
        """Обновление статистики в менеджере"""
        total_employees = len(self.employees)
        
        if total_employees == 0:
            label.config(text="Нет работников в системе")
            return
        
        category_stats = {}
        for category in self.categories:
            count = sum(1 for emp in self.employees if emp.get("category") == category)
            if count > 0:
                # Считаем часы по категории
                hours = 0
                for emp in self.employees:
                    if emp.get("category") == category and emp["id"] in self.hours_counter:
                        hours += self.hours_counter[emp["id"]]["total_hours"]
                category_stats[category] = {"count": count, "hours": hours}
        
        stats_text = f"Всего работников: {total_employees}\n"
        stats_text += f"Категорий: {len([c for c, stats in category_stats.items() if stats['count'] > 0])}\n\n"
        stats_text += "Распределение:\n"
        
        for category, stats in sorted(category_stats.items(), key=lambda x: x[1]["count"], reverse=True):
            percentage = (stats['count'] / total_employees) * 100
            stats_text += f"  • {category}: {stats['count']} ({percentage:.1f}%) - {stats['hours']:.1f} ч\n"
        
        label.config(text=stats_text)
    
    def add_category_from_manager(self, parent_window, tree):
        """Добавление категории из менеджера"""
        add_window = tk.Toplevel(parent_window)
        add_window.title("Добавить категорию")
        add_window.geometry("300x150")
        add_window.transient(parent_window)
        add_window.grab_set()
        
        frame = ttk.Frame(add_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Название категории:", 
                 font=('Segoe UI', 11)).pack(anchor=tk.W, pady=(0, 10))
        
        name_var = tk.StringVar()
        name_entry = ttk.Entry(frame, textvariable=name_var, font=('Segoe UI', 11))
        name_entry.pack(fill=tk.X, pady=(0, 15))
        name_entry.focus()
        
        def save():
            category_name = name_var.get().strip()
            if not category_name:
                messagebox.showwarning("Внимание", "Введите название категории", parent=add_window)
                return
            
            if category_name in self.categories:
                messagebox.showwarning("Внимание", "Категория уже существует", parent=add_window)
                return
            
            self.categories.append(category_name)
            self.update_category_widgets()
            
            # Добавляем в дерево
            tree.insert('', tk.END, values=(category_name, 0, "0.0 ч"))
            
            add_window.destroy()
            self.update_manager_stats(parent_window.winfo_children()[0].winfo_children()[1])
        
        ttk.Button(frame, text="💾 Сохранить", 
                  command=save, style='Success.TButton').pack(pady=5)
    
    def edit_category_from_manager(self, parent_window, tree):
        """Редактирование категории из менеджера"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите категорию для редактирования", parent=parent_window)
            return
        
        item = tree.item(selection[0])
        old_name = item['values'][0]
        
        edit_window = tk.Toplevel(parent_window)
        edit_window.title(f"Редактирование: {old_name}")
        edit_window.geometry("300x150")
        edit_window.transient(parent_window)
        edit_window.grab_set()
        
        frame = ttk.Frame(edit_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Новое название:", 
                 font=('Segoe UI', 11)).pack(anchor=tk.W, pady=(0, 10))
        
        name_var = tk.StringVar(value=old_name)
        name_entry = ttk.Entry(frame, textvariable=name_var, font=('Segoe UI', 11))
        name_entry.pack(fill=tk.X, pady=(0, 15))
        name_entry.focus()
        
        def save():
            new_name = name_var.get().strip()
            if not new_name:
                messagebox.showwarning("Внимание", "Введите название категории", parent=edit_window)
                return
            
            if new_name != old_name and new_name in self.categories:
                messagebox.showwarning("Внимание", "Категория уже существует", parent=edit_window)
                return
            
            # Обновляем
            index = self.categories.index(old_name)
            self.categories[index] = new_name
            
            # Обновляем работников
            for employee in self.employees:
                if employee.get("category") == old_name:
                    employee["category"] = new_name
            
            # Обновляем смены
            for shift in self.shifts:
                if shift.get("category") == old_name:
                    shift["category"] = new_name
            
            self.update_category_widgets()
            self.calculate_hours()
            
            # Обновляем дерево
            tree.item(selection[0], values=(new_name, item['values'][1], item['values'][2]))
            
            edit_window.destroy()
            self.update_manager_stats(parent_window.winfo_children()[0].winfo_children()[1])
        
        ttk.Button(frame, text="💾 Сохранить", 
                  command=save, style='Success.TButton').pack(pady=5)
    
    def delete_category_from_manager(self, tree):
        """Удаление категории из менеджера"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите категорию для удаления", parent=self.root)
            return
        
        item = tree.item(selection[0])
        category_name = item['values'][0]
        
        # Проверяем, есть ли работники
        employees_in_category = [emp for emp in self.employees if emp.get("category") == category_name]
        
        if employees_in_category:
            messagebox.showwarning("Внимание", 
                                 f"В категории есть {len(employees_in_category)} работников. Переместите их перед удалением.", 
                                 parent=self.root)
            return
        
        if messagebox.askyesno("Подтверждение", f"Удалить категорию '{category_name}'?", parent=self.root):
            self.categories.remove(category_name)
            tree.delete(selection[0])
            self.update_category_widgets()
    
    def move_all_to_category(self, parent_window):
        """Перемещение всех работников в одну категорию"""
        move_window = tk.Toplevel(parent_window)
        move_window.title("Переместить всех работников")
        move_window.geometry("400x200")
        move_window.transient(parent_window)
        move_window.grab_set()
        
        frame = ttk.Frame(move_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Переместить ВСЕХ работников в категорию:", 
                font=('Segoe UI', 12)).pack(pady=(0, 20))
        
        category_var = tk.StringVar(value=self.categories[0] if self.categories else "")
        category_combo = ttk.Combobox(frame, textvariable=category_var, 
                                     values=self.categories, font=('Segoe UI', 11), state="readonly")
        category_combo.pack(fill=tk.X, pady=(0, 20))
        
        def move():
            category = category_var.get()
            if not category:
                messagebox.showwarning("Внимание", "Выберите категорию", parent=move_window)
                return
            
            if messagebox.askyesno("Подтверждение", 
                                 f"Переместить всех {len(self.employees)} работников в категорию '{category}'?", 
                                 parent=move_window):
                for employee in self.employees:
                    employee["category"] = category
                
                for shift in self.shifts:
                    employee = next((emp for emp in self.employees if emp["id"] == shift["employee_id"]), None)
                    if employee:
                        shift["category"] = category
                
                self.update_category_widgets()
                self.calculate_hours()
                move_window.destroy()
                
                messagebox.showinfo("Успех", 
                                  f"Все работники перемещены в категорию '{category}'", 
                                  parent=self.root)
        
        ttk.Button(frame, text="🚀 Переместить", 
                  command=move, style='Warning.TButton').pack(pady=10)
    
    def show_detailed_category_stats(self):
        """Показать детальную статистику по категориям"""
        if not self.employees:
            messagebox.showinfo("Статистика", "Нет работников в системе", parent=self.root)
            return
        
        # Собираем статистику
        category_stats = {}
        
        for category in self.categories:
            employees_in_category = [emp for emp in self.employees if emp.get("category") == category]
            
            if employees_in_category:
                category_shifts = 0
                category_hours = 0
                
                for emp in employees_in_category:
                    if emp["id"] in self.hours_counter:
                        category_shifts += self.hours_counter[emp["id"]]["shifts_count"]
                        category_hours += self.hours_counter[emp["id"]]["total_hours"]
                
                category_stats[category] = {
                    "employees": len(employees_in_category),
                    "shifts": category_shifts,
                    "hours": category_hours,
                    "avg_shifts": category_shifts / len(employees_in_category) if employees_in_category else 0,
                    "avg_hours": category_hours / len(employees_in_category) if employees_in_category else 0
                }
        
        # Формируем текст
        stats_text = "📊 Детальная статистика по категориям:\n\n"
        
        for category, stats in sorted(category_stats.items(), 
                                     key=lambda x: x[1]["hours"], reverse=True):
            stats_text += f"🏷️ {category}:\n"
            stats_text += f"  • Работников: {stats['employees']}\n"
            stats_text += f"  • Всего смен: {stats['shifts']}\n"
            stats_text += f"  • Всего часов: {stats['hours']:.1f}\n"
            stats_text += f"  • Среднее на работника: {stats['avg_shifts']:.1f} смен, {stats['avg_hours']:.1f} часов\n\n"
        
        # Общая статистика
        total_shifts = sum(stats["shifts"] for stats in category_stats.values())
        total_hours = sum(stats["hours"] for stats in category_stats.values())
        
        stats_text += "=" * 40 + "\n"
        stats_text += f"📈 Общая статистика:\n"
        stats_text += f"  • Всего работников: {len(self.employees)}\n"
        stats_text += f"  • Всего смен: {total_shifts}\n"
        stats_text += f"  • Всего часов: {total_hours:.1f}\n"
        stats_text += f"  • Среднее на работника: {total_shifts/len(self.employees):.1f} смен, {total_hours/len(self.employees):.1f} часов\n"
        
        # Показываем в отдельном окне
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Детальная статистика по категориям")
        stats_window.geometry("500x600")
        stats_window.transient(self.root)
        
        frame = ttk.Frame(stats_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = tk.Text(frame, font=('Consolas', 10), wrap=tk.WORD, 
                             bg=self.colors['card'], padx=10, pady=10)
        text_widget.insert(1.0, stats_text)
        text_widget.config(state=tk.DISABLED)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Button(frame, text="📋 Копировать", 
                  command=lambda: self.copy_to_clipboard(stats_text), 
                  style='Primary.TButton').pack(pady=10)
    
    def copy_to_clipboard(self, text):
        """Копирование текста в буфер обмена"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Успех", "Текст скопирован в буфер обмена", parent=self.root)
    
    def filter_by_category(self):
        """Фильтрация работников по категории"""
        self.filter_category = self.category_filter_var.get()
        self.update_schedule_display()
    
    def edit_legend(self):
        """Редактирование легенды смен"""
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редактирование легенды смен")
        edit_window.geometry("600x500")
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        frame = ttk.Frame(edit_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Редактирование типов смен", 
                font=('Segoe UI', 16, 'bold')).pack(pady=(0, 20))
        
        # Список текущих типов смен
        list_frame = ttk.LabelFrame(frame, text="Текущие типы смен", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Создаем Treeview для отображения типов смен
        columns = ('name', 'start', 'end', 'color', 'hours')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=6)
        
        tree.heading('name', text='Название')
        tree.heading('start', text='Начало')
        tree.heading('end', text='Окончание')
        tree.heading('color', text='Цвет')
        tree.heading('hours', text='Часы')
        
        tree.column('name', width=150)
        tree.column('start', width=80)
        tree.column('end', width=80)
        tree.column('color', width=100)
        tree.column('hours', width=60)
        
        # Заполняем данными
        for shift_type, data in self.shift_types_data.items():
            hours = self.calculate_shift_hours_from_data(data)
            tree.insert('', tk.END, values=(
                shift_type, 
                data.get('start', '00:00'), 
                data.get('end', '00:00'), 
                data.get('color', '#000000'),
                f"{hours}ч"
            ))
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="➕ Добавить", 
                  command=lambda: self.add_legend_item(edit_window, tree), 
                  style='Success.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="✏️ Редактировать", 
                  command=lambda: self.edit_legend_item(tree), 
                  style='Primary.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🗑️ Удалить", 
                  command=lambda: self.delete_legend_item(tree), 
                  style='Danger.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="💾 Сохранить", 
                  command=lambda: self.save_legend(tree, edit_window), 
                  style='Success.TButton').pack(side=tk.LEFT, padx=2)
    
    def add_legend_item(self, parent_window, tree):
        """Добавление нового элемента в легенду"""
        add_window = tk.Toplevel(parent_window)
        add_window.title("Добавить тип смены")
        add_window.geometry("400x350")
        add_window.transient(parent_window)
        add_window.grab_set()
        
        frame = ttk.Frame(add_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Название типа смены:", 
                 font=('Segoe UI', 11)).pack(anchor=tk.W, pady=(0, 5))
        name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=name_var, font=('Segoe UI', 11)).pack(fill=tk.X, pady=(0, 10))
        
        # Время
        time_frame = ttk.Frame(frame)
        time_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(time_frame, text="Время:").grid(row=0, column=0, padx=5)
        
        # Начало
        start_frame = ttk.Frame(time_frame)
        start_frame.grid(row=0, column=1, padx=5)
        
        start_hour_var = tk.StringVar(value="08")
        start_hour_cb = ttk.Combobox(start_frame, textvariable=start_hour_var, 
                                    values=[f"{i:02d}" for i in range(24)], width=3)
        start_hour_cb.pack(side=tk.LEFT)
        ttk.Label(start_frame, text=":").pack(side=tk.LEFT)
        
        start_minute_var = tk.StringVar(value="00")
        start_minute_cb = ttk.Combobox(start_frame, textvariable=start_minute_var, 
                                      values=[f"{i:02d}" for i in range(0, 60, 5)], width=3)
        start_minute_cb.pack(side=tk.LEFT)
        
        ttk.Label(time_frame, text="—").grid(row=0, column=2, padx=5)
        
        # Конец
        end_frame = ttk.Frame(time_frame)
        end_frame.grid(row=0, column=3, padx=5)
        
        end_hour_var = tk.StringVar(value="16")
        end_hour_cb = ttk.Combobox(end_frame, textvariable=end_hour_var, 
                                  values=[f"{i:02d}" for i in range(24)], width=3)
        end_hour_cb.pack(side=tk.LEFT)
        ttk.Label(end_frame, text=":").pack(side=tk.LEFT)
        
        end_minute_var = tk.StringVar(value="00")
        end_minute_cb = ttk.Combobox(end_frame, textvariable=end_minute_var, 
                                    values=[f"{i:02d}" for i in range(0, 60, 5)], width=3)
        end_minute_cb.pack(side=tk.LEFT)
        
        # Цвет
        ttk.Label(frame, text="Цвет:", font=('Segoe UI', 11)).pack(anchor=tk.W, pady=(10, 5))
        color_var = tk.StringVar(value="#3498db")
        color_frame = ttk.Frame(frame)
        color_frame.pack(fill=tk.X, pady=(0, 10))
        
        color_entry = ttk.Entry(color_frame, textvariable=color_var, width=10)
        color_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        def choose_color():
            color = colorchooser.askcolor(title="Выберите цвет", parent=add_window)[1]
            if color:
                color_var.set(color)
        
        ttk.Button(color_frame, text="🎨 Выбрать", command=choose_color).pack(side=tk.LEFT)
        
        def save():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Внимание", "Введите название типа смены", parent=add_window)
                return
            
            start_time = f"{start_hour_var.get()}:{start_minute_var.get()}"
            end_time = f"{end_hour_var.get()}:{end_minute_var.get()}"
            color = color_var.get()
            
            # Рассчитываем часы
            try:
                start_hour, start_minute = map(int, start_time.split(":"))
                end_hour, end_minute = map(int, end_time.split(":"))
                
                start_total = start_hour * 60 + start_minute
                end_total = end_hour * 60 + end_minute
                
                if end_total < start_total:
                    end_total += 24 * 60
                
                total_hours = round((end_total - start_total) / 60, 1)
            except:
                total_hours = 0
            
            # Добавляем в дерево
            tree.insert('', tk.END, values=(name, start_time, end_time, color, f"{total_hours}ч"))
            add_window.destroy()
        
        ttk.Button(frame, text="💾 Сохранить", command=save, style='Success.TButton').pack(pady=10)
    
    def edit_legend_item(self, tree):
        """Редактирование элемента легенды"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите элемент для редактирования", parent=self.root)
            return
        
        item = tree.item(selection[0])
        values = item['values']
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Редактирование типа смены: {values[0]}")
        edit_window.geometry("400x350")
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        frame = ttk.Frame(edit_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Название типа смены:", 
                 font=('Segoe UI', 11)).pack(anchor=tk.W, pady=(0, 5))
        name_var = tk.StringVar(value=values[0])
        ttk.Entry(frame, textvariable=name_var, font=('Segoe UI', 11)).pack(fill=tk.X, pady=(0, 10))
        
        # Время
        start_time = values[1]
        end_time = values[2]
        
        if ':' in start_time:
            start_hour, start_minute = start_time.split(':')
        else:
            start_hour, start_minute = '00', '00'
        
        if ':' in end_time:
            end_hour, end_minute = end_time.split(':')
        else:
            end_hour, end_minute = '00', '00'
        
        time_frame = ttk.Frame(frame)
        time_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(time_frame, text="Время:").grid(row=0, column=0, padx=5)
        
        # Начало
        start_frame = ttk.Frame(time_frame)
        start_frame.grid(row=0, column=1, padx=5)
        
        start_hour_var = tk.StringVar(value=start_hour)
        start_hour_cb = ttk.Combobox(start_frame, textvariable=start_hour_var, 
                                    values=[f"{i:02d}" for i in range(24)], width=3)
        start_hour_cb.pack(side=tk.LEFT)
        ttk.Label(start_frame, text=":").pack(side=tk.LEFT)
        
        start_minute_var = tk.StringVar(value=start_minute)
        start_minute_cb = ttk.Combobox(start_frame, textvariable=start_minute_var, 
                                      values=[f"{i:02d}" for i in range(0, 60, 5)], width=3)
        start_minute_cb.pack(side=tk.LEFT)
        
        ttk.Label(time_frame, text="—").grid(row=0, column=2, padx=5)
        
        # Конец
        end_frame = ttk.Frame(time_frame)
        end_frame.grid(row=0, column=3, padx=5)
        
        end_hour_var = tk.StringVar(value=end_hour)
        end_hour_cb = ttk.Combobox(end_frame, textvariable=end_hour_var, 
                                  values=[f"{i:02d}" for i in range(24)], width=3)
        end_hour_cb.pack(side=tk.LEFT)
        ttk.Label(end_frame, text=":").pack(side=tk.LEFT)
        
        end_minute_var = tk.StringVar(value=end_minute)
        end_minute_cb = ttk.Combobox(end_frame, textvariable=end_minute_var, 
                                    values=[f"{i:02d}" for i in range(0, 60, 5)], width=3)
        end_minute_cb.pack(side=tk.LEFT)
        
        # Цвет
        ttk.Label(frame, text="Цвет:", font=('Segoe UI', 11)).pack(anchor=tk.W, pady=(10, 5))
        color_var = tk.StringVar(value=values[3])
        color_frame = ttk.Frame(frame)
        color_frame.pack(fill=tk.X, pady=(0, 10))
        
        color_entry = ttk.Entry(color_frame, textvariable=color_var, width=10)
        color_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        def choose_color():
            color = colorchooser.askcolor(title="Выберите цвет", parent=edit_window)[1]
            if color:
                color_var.set(color)
        
        ttk.Button(color_frame, text="🎨 Выбрать", command=choose_color).pack(side=tk.LEFT)
        
        def save():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Внимание", "Введите название типа смены", parent=edit_window)
                return
            
            start_time = f"{start_hour_var.get()}:{start_minute_var.get()}"
            end_time = f"{end_hour_var.get()}:{end_minute_var.get()}"
            color = color_var.get()
            
            # Рассчитываем часы
            try:
                start_hour, start_minute = map(int, start_time.split(":"))
                end_hour, end_minute = map(int, end_time.split(":"))
                
                start_total = start_hour * 60 + start_minute
                end_total = end_hour * 60 + end_minute
                
                if end_total < start_total:
                    end_total += 24 * 60
                
                total_hours = round((end_total - start_total) / 60, 1)
            except:
                total_hours = 0
            
            # Обновляем дерево
            tree.item(selection[0], values=(name, start_time, end_time, color, f"{total_hours}ч"))
            edit_window.destroy()
        
        ttk.Button(frame, text="💾 Сохранить", command=save, style='Success.TButton').pack(pady=10)
    
    def delete_legend_item(self, tree):
        """Удаление элемента легенды"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите элемент для удаления", parent=self.root)
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранный тип смены?", parent=self.root):
            tree.delete(selection[0])
    
    def save_legend(self, tree, parent_window):
        """Сохранение легенды"""
        self.shift_types_data = {}
        
        # Собираем данные из дерева
        for item_id in tree.get_children():
            values = tree.item(item_id)['values']
            if len(values) >= 4:
                name, start, end, color = values[:4]
                self.shift_types_data[name] = {
                    'start': start,
                    'end': end,
                    'color': color
                }
        
        # Обновляем список типов смен
        self.shift_types = self.generate_shift_types_list()
        
        # Обновляем отображение
        self.update_schedule_display()
        
        parent_window.destroy()
        messagebox.showinfo("Успех", "Легенда смен сохранена", parent=self.root)
    
    def choose_new_shift_color(self):
        """Выбор цвета для нового типа смены"""
        color = colorchooser.askcolor(title="Выберите цвет", parent=self.root)[1]
        if color:
            self.new_shift_color.set(color)
    
    def add_shift_type(self):
        """Добавление нового типа смены"""
        name = self.new_shift_name.get().strip()
        start = f"{self.new_start_hour.get()}:{self.new_start_minute.get()}"
        end = f"{self.new_end_hour.get()}:{self.new_end_minute.get()}"
        color = self.new_shift_color.get()
        
        if not name:
            messagebox.showwarning("Внимание", "Введите название типа смены", parent=self.root)
            return
        
        if name in self.shift_types_data:
            messagebox.showwarning("Внимание", "Тип смены с таким названием уже существует", parent=self.root)
            return
        
        # Добавляем новый тип смены
        self.shift_types_data[name] = {
            'start': start,
            'end': end,
            'color': color
        }
        
        # Обновляем списки
        self.shift_types = self.generate_shift_types_list()
        self.update_shift_types_list()
        
        # Очищаем поля
        self.new_shift_name.delete(0, tk.END)
        self.new_start_hour.set("08")
        self.new_start_minute.set("00")
        self.new_end_hour.set("16")
        self.new_end_minute.set("00")
        self.new_shift_color.set("#3498db")
        
        # Обновляем отображение
        self.update_schedule_display()
        
        messagebox.showinfo("Успех", f"Тип смены '{name}' добавлен", parent=self.root)
    
    def delete_shift_type(self):
        """Удаление типа смены"""
        selection = self.shift_types_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите тип смены для удаления", parent=self.root)
            return
        
        item = self.shift_types_tree.item(selection[0])
        shift_type = item['values'][0]
        
        if messagebox.askyesno("Подтверждение", 
                              f"Удалить тип смены '{shift_type}'?\nВсе смены этого типа будут удалены.", 
                              parent=self.root):
            # Удаляем тип смены
            if shift_type in self.shift_types_data:
                del self.shift_types_data[shift_type]
            
            # Удаляем смены этого типа
            self.shifts = [s for s in self.shifts if s.get('shift_type') != shift_type]
            
            # Пересчитываем часы
            self.calculate_hours()
            
            # Обновляем списки
            self.shift_types = self.generate_shift_types_list()
            self.update_shift_types_list()
            self.update_schedule_display()
            self.update_hours_table()
            
            messagebox.showinfo("Успех", f"Тип смены '{shift_type}' удален", parent=self.root)
    
    def update_shift_types_list(self):
        """Обновление списка типов смен"""
        for item in self.shift_types_tree.get_children():
            self.shift_types_tree.delete(item)
        
        for shift_type, data in self.shift_types_data.items():
            hours = self.calculate_shift_hours_from_data(data)
            self.shift_types_tree.insert('', tk.END, values=(
                shift_type, 
                data.get('start', '00:00'), 
                data.get('end', '00:00'), 
                data.get('color', '#000000'),
                f"{hours}ч"
            ))
    
    def edit_shift_type(self):
        """Редактирование типа смены"""
        selection = self.shift_types_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите тип смены для редактирования", parent=self.root)
            return
        
        item = self.shift_types_tree.item(selection[0])
        old_name = item['values'][0]
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Редактирование типа смены: {old_name}")
        edit_window.geometry("400x350")
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        frame = ttk.Frame(edit_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Название:", font=('Segoe UI', 11)).pack(anchor=tk.W, pady=(0, 5))
        name_var = tk.StringVar(value=old_name)
        ttk.Entry(frame, textvariable=name_var, font=('Segoe UI', 11)).pack(fill=tk.X, pady=(0, 10))
        
        # Время
        data = self.shift_types_data[old_name]
        start_time = data.get('start', '00:00')
        end_time = data.get('end', '00:00')
        color = data.get('color', '#000000')
        
        if ':' in start_time:
            start_hour, start_minute = start_time.split(':')
        else:
            start_hour, start_minute = '00', '00'
        
        if ':' in end_time:
            end_hour, end_minute = end_time.split(':')
        else:
            end_hour, end_minute = '00', '00'
        
        time_frame = ttk.Frame(frame)
        time_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(time_frame, text="Время:").grid(row=0, column=0, padx=5)
        
        # Начало
        start_frame = ttk.Frame(time_frame)
        start_frame.grid(row=0, column=1, padx=5)
        
        start_hour_var = tk.StringVar(value=start_hour)
        ttk.Combobox(start_frame, textvariable=start_hour_var, 
                    values=[f"{i:02d}" for i in range(24)], width=3).pack(side=tk.LEFT)
        ttk.Label(start_frame, text=":").pack(side=tk.LEFT)
        
        start_minute_var = tk.StringVar(value=start_minute)
        ttk.Combobox(start_frame, textvariable=start_minute_var, 
                    values=[f"{i:02d}" for i in range(0, 60, 5)], width=3).pack(side=tk.LEFT)
        
        ttk.Label(time_frame, text="—").grid(row=0, column=2, padx=5)
        
        # Конец
        end_frame = ttk.Frame(time_frame)
        end_frame.grid(row=0, column=3, padx=5)
        
        end_hour_var = tk.StringVar(value=end_hour)
        ttk.Combobox(end_frame, textvariable=end_hour_var, 
                    values=[f"{i:02d}" for i in range(24)], width=3).pack(side=tk.LEFT)
        ttk.Label(end_frame, text=":").pack(side=tk.LEFT)
        
        end_minute_var = tk.StringVar(value=end_minute)
        ttk.Combobox(end_frame, textvariable=end_minute_var, 
                    values=[f"{i:02d}" for i in range(0, 60, 5)], width=3).pack(side=tk.LEFT)
        
        # Цвет
        ttk.Label(frame, text="Цвет:", font=('Segoe UI', 11)).pack(anchor=tk.W, pady=(10, 5))
        color_var = tk.StringVar(value=color)
        color_frame = ttk.Frame(frame)
        color_frame.pack(fill=tk.X, pady=(0, 10))
        
        color_entry = ttk.Entry(color_frame, textvariable=color_var, width=10)
        color_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        def choose_color():
            color = colorchooser.askcolor(title="Выберите цвет", parent=edit_window)[1]
            if color:
                color_var.set(color)
        
        ttk.Button(color_frame, text="🎨 Выбрать", command=choose_color).pack(side=tk.LEFT)
        
        def save():
            new_name = name_var.get().strip()
            if not new_name:
                messagebox.showwarning("Внимание", "Введите название типа смены", parent=edit_window)
                return
            
            new_start = f"{start_hour_var.get()}:{start_minute_var.get()}"
            new_end = f"{end_hour_var.get()}:{end_minute_var.get()}"
            new_color = color_var.get()
            
            # Обновляем данные
            if old_name != new_name:
                # Если имя изменилось, удаляем старую запись и создаем новую
                del self.shift_types_data[old_name]
                # Обновляем смены
                for shift in self.shifts:
                    if shift.get('shift_type') == old_name:
                        shift['shift_type'] = new_name
            
            self.shift_types_data[new_name] = {
                'start': new_start,
                'end': new_end,
                'color': new_color
            }
            
            # Пересчитываем часы
            self.calculate_hours()
            
            # Обновляем списки
            self.shift_types = self.generate_shift_types_list()
            self.update_shift_types_list()
            self.update_schedule_display()
            self.update_hours_table()
            
            edit_window.destroy()
            messagebox.showinfo("Успех", "Тип смены обновлен", parent=self.root)
        
        ttk.Button(frame, text="💾 Сохранить", command=save, style='Success.TButton').pack(pady=10)
    
    def update_schedule_display(self):
        """Обновление отображения графика на текущий месяц"""
        # Обновляем метку месяца
        self.update_month_label()
        
        # Пересчитываем часы
        self.calculate_hours()
        
        # Очищаем таблицу
        for item in self.schedule_tree.get_children():
            self.schedule_tree.delete(item)
        
        # Получаем количество дней в месяце
        _, num_days = monthrange(self.current_year, self.current_month)
        
        # Обновляем значения дней в Combobox
        days_list = list(range(1, num_days + 1))
        self.day_cb['values'] = days_list
        if self.day_var.get() not in days_list:
            self.day_var.set(days_list[0] if days_list else 1)
        
        # Настраиваем колонки таблицы
        columns = ['employee'] + [f'day_{i}' for i in range(1, num_days + 1)] + ['hours']
        self.schedule_tree['columns'] = tuple(columns)
        
        # Скрываем первую колонку
        self.schedule_tree.column('#0', width=0, stretch=tk.NO)
        
        # Настраиваем ширину колонок
        self.schedule_tree.column('employee', width=180, anchor=tk.W, minwidth=150)
        self.schedule_tree.column('hours', width=100, anchor=tk.CENTER, minwidth=80)
        
        # Настраиваем колонки дней
        for i in range(1, num_days + 1):
            self.schedule_tree.column(f'day_{i}', width=100, anchor=tk.CENTER, minwidth=90, stretch=True)
        
        # Заголовки колонок
        self.schedule_tree.heading('employee', text='Работник', anchor=tk.W)
        self.schedule_tree.heading('hours', text='Часы', anchor=tk.CENTER)
        
        # Русские сокращения дней недели
        russian_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        
        # Заполняем заголовки дней
        for i in range(1, num_days + 1):
            day_date = date(self.current_year, self.current_month, i)
            day_of_week = day_date.weekday()
            day_header = f"{i}\n{russian_days[day_of_week]}"
            
            if day_date.weekday() >= 5:  # Суббота и воскресенье
                day_header = f"📅 {i}\n{russian_days[day_of_week]}"
            
            self.schedule_tree.heading(f'day_{i}', text=day_header, anchor=tk.CENTER)
        
        # Сохраняем даты для справки
        self.current_month_dates = [date(self.current_year, self.current_month, i) 
                                   for i in range(1, num_days + 1)]
        
        # Создаем словарь для быстрого доступа к сменам
        shifts_dict = {}
        for shift in self.shifts:
            try:
                shift_date = datetime.strptime(shift["date"], "%Y-%m-%d").date()
                if shift_date.year == self.current_year and shift_date.month == self.current_month:
                    key = (shift["employee_name"], shift_date.day)
                    
                    # Получаем цвет для типа смены
                    shift_type = shift.get("shift_type", "")
                    color = self.shift_types_data.get(shift_type, {}).get('color', '#95a5a6')
                    
                    # Форматируем отображение смены
                    if shift.get("start_time") and shift.get("end_time"):
                        if shift["start_time"] == "00:00" and shift["end_time"] == "00:00":
                            shift_display = shift_type
                        else:
                            # Сокращаем отображение для экономии места
                            shift_display = f"{shift_type[:3]}\n{shift['start_time'][:5]}"
                    else:
                        shift_display = shift_type[:4] if len(shift_type) > 4 else shift_type
                    
                    shifts_dict[key] = (shift_display, color)
            except ValueError:
                continue
        
        # Фильтруем работников по категории
        filtered_employees = self.employees
        if self.filter_category != "Все категории":
            filtered_employees = [emp for emp in self.employees 
                                if emp.get("category") == self.filter_category]
        
        # Добавляем строки для каждого отфильтрованного работника
        for idx, employee in enumerate(filtered_employees):
            # Получаем смены на текущий месяц
            month_shifts = []
            for day in range(1, num_days + 1):
                shift_info = shifts_dict.get((employee["name"], day), ("", "#ffffff"))
                month_shifts.append(shift_info[0])
            
            # Добавляем категорию к имени (в скобках)
            employee_display = f"{employee['name']} ({employee.get('category', 'Другое')})"
            
            # Получаем часы работы за месяц
            hours_worked = self.hours_counter.get(employee["id"], {}).get("total_hours", 0)
            hours_display = f"{hours_worked:.1f}ч" if hours_worked > 0 else "0ч"
            
            values = (employee_display,) + tuple(month_shifts) + (hours_display,)
            
            item = self.schedule_tree.insert('', tk.END, values=values)
            
            # Раскрашиваем ячейки
            for i, day in enumerate(range(1, num_days + 1)):
                shift_info = shifts_dict.get((employee["name"], day), ("", "#ffffff"))
                if shift_info[0]:  # Если есть смена
                    self.schedule_tree.set(item, f'day_{day}', shift_info[0])
                    # Создаем тег с цветом если его нет
                    tag_name = f'color_{shift_info[1].replace("#", "")}'
                    if not self.schedule_tree.tag_configure(tag_name):
                        self.schedule_tree.tag_configure(tag_name, 
                                                        background=shift_info[1],
                                                        foreground='white')
                    # Применяем тег к ячейке
                    self.schedule_tree.item(item, tags=(tag_name,))
            
            # Раскрашиваем ячейку с часами в зависимости от количества
            if hours_worked > 0:
                if hours_worked >= 160:  # Полная занятость
                    hours_tag = 'hours_high'
                    hours_color = self.colors['success']
                elif hours_worked >= 80:
                    hours_tag = 'hours_medium'
                    hours_color = self.colors['warning']
                else:
                    hours_tag = 'hours_low'
                    hours_color = self.colors['secondary']
                
                if not self.schedule_tree.tag_configure(hours_tag):
                    self.schedule_tree.tag_configure(hours_tag, 
                                                    background=hours_color,
                                                    foreground='white',
                                                    font=('Segoe UI', 9, 'bold'))
                # Добавляем тег к ячейке часов
                current_tags = list(self.schedule_tree.item(item, 'tags'))
                current_tags.append(hours_tag)
                self.schedule_tree.item(item, tags=tuple(current_tags))
        
        # Обновляем статистику
        self.update_statistics()
        
        # Обновляем таблицу часов
        self.update_hours_table()
        
        # Обновляем статус бар
        month_name_rus = self.get_month_name()
        total_hours = sum(data["total_hours"] for data in self.hours_counter.values())
        filter_text = f" (фильтр: {self.filter_category})" if self.filter_category != "Все категории" else ""
        self.status_bar.config(text=f"График обновлен: {month_name_rus} {self.current_year} | Всего часов: {total_hours:.1f}{filter_text}")
    
    def update_month_label(self):
        """Обновление метки текущего месяца"""
        month_name_rus = self.get_month_name()
        self.month_label.config(text=f"{month_name_rus} {self.current_year}")
    
    def get_month_name(self):
        """Получение русского названия месяца"""
        month_names_rus = {
            1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
            5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
            9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
        }
        return month_names_rus.get(self.current_month, "")
    
    def prev_month(self):
        """Переход к предыдущему месяцу"""
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.update_schedule_display()
    
    def next_month(self):
        """Переход к следующему месяцу"""
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.update_schedule_display()
    
    def prev_year(self):
        """Переход к предыдущему году"""
        self.current_year -= 1
        self.update_schedule_display()
    
    def next_year(self):
        """Переход к следующему году"""
        self.current_year += 1
        self.update_schedule_display()
    
    def today_month(self):
        """Переход к текущему месяцу"""
        self.current_date = datetime.now()
        self.current_year = self.current_date.year
        self.current_month = self.current_date.month
        self.update_schedule_display()
    
    def search_employee(self):
        """Поиск работника"""
        search_term = self.search_var.get().strip().lower()
        if not search_term:
            return
        
        # Ищем в списке работников
        for emp in self.employees:
            if search_term in emp["name"].lower():
                # Можно выделить найденного работника в таблице
                messagebox.showinfo("Найден", f"Работник: {emp['name']}\nКатегория: {emp.get('category', 'Другое')}", 
                                  parent=self.root)
                return
        
        messagebox.showinfo("Не найден", f"Работник с именем '{search_term}' не найден", parent=self.root)
    
    def save_data(self):
        """Сохранение данных"""
        data = {
            "employees": self.employees,
            "shifts": self.shifts,
            "shift_types_data": self.shift_types_data,
            "shift_types": self.shift_types,
            "categories": self.categories,
            "hours_counter": self.hours_counter
        }
        
        try:
            with open('schedule_data_modern.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.status_bar.config(text="Данные сохранены")
            messagebox.showinfo("Успех", "Данные успешно сохранены", parent=self.root)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}", parent=self.root)
    
    def load_data(self):
        """Загрузка данных"""
        if os.path.exists('schedule_data_modern.json'):
            try:
                with open('schedule_data_modern.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.employees = data.get("employees", [])
                    self.shifts = data.get("shifts", [])
                    self.shift_types_data = data.get("shift_types_data", self.shift_types_data)
                    self.shift_types = data.get("shift_types", self.generate_shift_types_list())
                    self.categories = data.get("categories", self.categories)
                    self.hours_counter = data.get("hours_counter", {})
            except Exception as e:
                messagebox.showwarning("Внимание", f"Не удалось загрузить данные: {str(e)}", parent=self.root)
    
    def start_auto_save(self):
        """Запуск автоматического сохранения"""
        self.auto_save_id = self.root.after(300000, self.auto_save)  # 5 минут
    
    def auto_save(self):
        """Автоматическое сохранение данных"""
        self.save_data()
        self.auto_save_id = self.root.after(300000, self.auto_save)  # Повторяем через 5 минут
    
    def setup_drag_and_drop(self):
        """Настройка перетаскивания смен"""
        self.schedule_tree.bind("<ButtonPress-1>", self.on_drag_start)
        self.schedule_tree.bind("<B1-Motion>", self.on_drag_motion)
        self.schedule_tree.bind("<ButtonRelease-1>", self.on_drag_release)
    
    def on_drag_start(self, event):
        """Начало перетаскивания"""
        item = self.schedule_tree.identify_row(event.y)
        column = self.schedule_tree.identify_column(event.x)
        
        if item and column:
            self.drag_data["item"] = item
            self.drag_data["column"] = column
    
    def on_drag_motion(self, event):
        """Перетаскивание"""
        pass  # Можно добавить визуальную обратную связь
    
    def on_drag_release(self, event):
        """Завершение перетаскивания"""
        target_item = self.schedule_tree.identify_row(event.y)
        target_column = self.schedule_tree.identify_column(event.x)
        
        if (self.drag_data["item"] and target_item and 
            self.drag_data["column"] != '#0' and target_column != '#0'):
            
            source_col = int(self.drag_data["column"][1:]) - 1
            target_col = int(target_column[1:]) - 1
            
            if source_col > 0 and target_col > 0:  # 0 - колонка с именем
                source_day = source_col
                target_day = target_col
                
                source_employee = self.schedule_tree.item(self.drag_data["item"])['values'][0]
                target_employee = self.schedule_tree.item(target_item)['values'][0]
                
                # Извлекаем имя сотрудника (без категории в скобках)
                if '(' in source_employee:
                    source_employee_name = source_employee.split('(')[0].strip()
                else:
                    source_employee_name = source_employee
                
                if '(' in target_employee:
                    target_employee_name = target_employee.split('(')[0].strip()
                else:
                    target_employee_name = target_employee
                
                # Находим смену для перемещения
                source_date = date(self.current_year, self.current_month, source_day)
                target_date = date(self.current_year, self.current_month, target_day)
                
                source_shift = next((s for s in self.shifts 
                                   if s["employee_name"] == source_employee_name and 
                                   s["date"] == source_date.strftime("%Y-%m-%d")), None)
                
                if source_shift:
                    # Создаем копию смены для нового работника и дня
                    new_shift = source_shift.copy()
                    new_shift["id"] = len(self.shifts) + 1
                    new_shift["employee_name"] = target_employee_name
                    new_shift["date"] = target_date.strftime("%Y-%m-%d")
                    
                    # Находим ID нового работника
                    target_employee_obj = next((emp for emp in self.employees 
                                              if emp["name"] == target_employee_name), None)
                    if target_employee_obj:
                        new_shift["employee_id"] = target_employee_obj["id"]
                        new_shift["category"] = target_employee_obj.get("category", "Другое")
                        
                        # Удаляем старую смену
                        self.shifts = [s for s in self.shifts if s != source_shift]
                        
                        # Добавляем новую смену
                        self.shifts.append(new_shift)
                        
                        # Пересчитываем часы
                        self.calculate_hours()
                        
                        # Обновляем отображение
                        self.update_schedule_display()
        
        self.drag_data = {"item": None, "column": None}
    
    def show_context_menu(self, event):
        """Показать контекстное меню для таблицы"""
        # Определяем, на каком элементе был клик
        item = self.schedule_tree.identify_row(event.y)
        column = self.schedule_tree.identify_column(event.x)
        
        if item and column and column != '#0':
            # Создаем контекстное меню
            context_menu = tk.Menu(self.root, tearoff=0)
            
            # Добавляем пункты меню
            context_menu.add_command(label="📋 Копировать смену", 
                                   command=self.copy_selected_shift)
            context_menu.add_command(label="📎 Вставить смену", 
                                   command=self.paste_shift)
            context_menu.add_separator()
            context_menu.add_command(label="🗑️ Удалить смену", 
                                   command=self.delete_selected_shift)
            context_menu.add_command(label="🗑️ Удалить все смены за день", 
                                   command=self.delete_all_shifts_for_day)
            context_menu.add_separator()
            context_menu.add_command(label="🔍 Информация о смене", 
                                   command=self.show_shift_info)
            context_menu.add_command(label="⏱️ Часы работы", 
                                   command=self.show_hours_statistics)
            
            # Показываем меню
            context_menu.tk_popup(event.x_root, event.y_root)
            
            # Выделяем ячейку
            self.schedule_tree.selection_set(item)
    
    def clear_selection(self):
        """Снятие выделения"""
        self.schedule_tree.selection_remove(self.schedule_tree.selection())
    
    def delete_selected_shift(self):
        """Удаление выбранной смены из таблицы"""
        selection = self.schedule_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите смену для удаления", parent=self.root)
            return
        
        # Получаем информацию о выбранной ячейке
        item = selection[0]
        column = self.schedule_tree.identify_column(self.root.winfo_pointerx() - self.schedule_tree.winfo_rootx())
        
        if column and column != '#0':
            day = int(column[1:])  # day_1 -> 1
            employee_name_with_category = self.schedule_tree.item(item)['values'][0]
            
            # Извлекаем имя сотрудника (без категории в скобках)
            if '(' in employee_name_with_category:
                employee_name = employee_name_with_category.split('(')[0].strip()
            else:
                employee_name = employee_name_with_category
            
            # Находим смену
            shift_date = date(self.current_year, self.current_month, day)
            shift = next((s for s in self.shifts 
                         if s["employee_name"] == employee_name and 
                         s["date"] == shift_date.strftime("%Y-%m-%d")), None)
            
            if shift:
                if messagebox.askyesno("Подтверждение", 
                                      f"Удалить смену у {employee_name} на {day} число?", 
                                      parent=self.root):
                    self.shifts.remove(shift)
                    
                    # Пересчитываем часы
                    self.calculate_hours()
                    
                    self.update_schedule_display()
                    self.status_bar.config(text=f"Смена удалена: {employee_name}, {day} число")
            else:
                messagebox.showinfo("Информация", "Смена не найдена", parent=self.root)
    
    def copy_selected_shift(self):
        """Копирование выбранной смены из таблицы"""
        selection = self.schedule_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите смену для копирования", parent=self.root)
            return
        
        # Получаем информацию о выбранной ячейке
        item = selection[0]
        column = self.schedule_tree.identify_column(self.root.winfo_pointerx() - self.schedule_tree.winfo_rootx())
        
        if column and column != '#0':
            day = int(column[1:])  # day_1 -> 1
            employee_name_with_category = self.schedule_tree.item(item)['values'][0]
            
            # Извлекаем имя сотрудника (без категории в скобках)
            if '(' in employee_name_with_category:
                employee_name = employee_name_with_category.split('(')[0].strip()
            else:
                employee_name = employee_name_with_category
            
            # Находим смену
            shift_date = date(self.current_year, self.current_month, day)
            shift = next((s for s in self.shifts 
                         if s["employee_name"] == employee_name and 
                         s["date"] == shift_date.strftime("%Y-%m-%d")), None)
            
            if shift:
                # Сохраняем скопированную смену
                self.copied_shift = shift.copy()
                self.status_bar.config(text=f"Смена скопирована: {employee_name}, {day} число")
                messagebox.showinfo("Успех", 
                                  f"Смена скопирована.\n{employee_name}, {day} число: {shift['shift_type']}\n"
                                  f"Продолжительность: {self.calculate_shift_hours(shift)} часов\n"
                                  f"Теперь вы можете вставить ее в другую ячейку.", 
                                  parent=self.root)
            else:
                messagebox.showinfo("Информация", "Смена не найдена", parent=self.root)
    
    def paste_shift(self):
        """Вставка скопированной смены"""
        if not self.copied_shift:
            messagebox.showwarning("Внимание", "Нет скопированной смены", parent=self.root)
            return
        
        selection = self.schedule_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите ячейку для вставки", parent=self.root)
            return
        
        # Получаем информацию о целевой ячейке
        item = selection[0]
        column = self.schedule_tree.identify_column(self.root.winfo_pointerx() - self.schedule_tree.winfo_rootx())
        
        if column and column != '#0':
            target_day = int(column[1:])  # day_1 -> 1
            target_employee_with_category = self.schedule_tree.item(item)['values'][0]
            
            # Извлекаем имя целевого сотрудника (без категории в скобках)
            if '(' in target_employee_with_category:
                target_employee_name = target_employee_with_category.split('(')[0].strip()
            else:
                target_employee_name = target_employee_with_category
            
            # Проверяем, существует ли целевой работник
            target_employee = next((emp for emp in self.employees 
                                  if emp["name"] == target_employee_name), None)
            
            if not target_employee:
                messagebox.showwarning("Ошибка", "Целевой работник не найден", parent=self.root)
                return
            
            # Создаем новую дату
            target_date = date(self.current_year, self.current_month, target_day)
            
            # Проверяем, есть ли уже смена у этого работника в этот день
            existing_shift = next((s for s in self.shifts 
                                  if s["employee_name"] == target_employee_name and 
                                  s["date"] == target_date.strftime("%Y-%m-%d")), None)
            
            if existing_shift:
                if not messagebox.askyesno("Подтверждение", 
                                          f"У работника {target_employee_name} уже есть смена на {target_day} число. Заменить?", 
                                          parent=self.root):
                    return
                
                # Удаляем старую смену
                self.shifts = [s for s in self.shifts if s != existing_shift]
            
            # Создаем новую смену на основе скопированной
            new_shift = self.copied_shift.copy()
            new_shift["id"] = len(self.shifts) + 1
            new_shift["employee_id"] = target_employee["id"]
            new_shift["employee_name"] = target_employee_name
            new_shift["date"] = target_date.strftime("%Y-%m-%d")
            new_shift["category"] = target_employee.get("category", "Другое")
            
            # Добавляем новую смену
            self.shifts.append(new_shift)
            
            # Пересчитываем часы
            self.calculate_hours()
            
            # Обновляем отображение
            self.update_schedule_display()
            
            self.status_bar.config(text=f"Смена вставлена: {target_employee_name}, {target_day} число")
            messagebox.showinfo("Успех", 
                              f"Смена вставлена.\n{target_employee_name}, {target_day} число: {new_shift['shift_type']}\n"
                              f"Продолжительность: {self.calculate_shift_hours(new_shift)} часов", 
                              parent=self.root)
    
    def show_shift_info(self):
        """Показать информацию о выбранной смене"""
        selection = self.schedule_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите смену для просмотра информации", parent=self.root)
            return
        
        # Получаем информацию о выбранной ячейке
        item = selection[0]
        column = self.schedule_tree.identify_column(self.root.winfo_pointerx() - self.schedule_tree.winfo_rootx())
        
        if column and column != '#0':
            day = int(column[1:])  # day_1 -> 1
            employee_name_with_category = self.schedule_tree.item(item)['values'][0]
            
            # Извлекаем имя сотрудника (без категории в скобках)
            if '(' in employee_name_with_category:
                employee_name = employee_name_with_category.split('(')[0].strip()
            else:
                employee_name = employee_name_with_category
            
            # Находим смену
            shift_date = date(self.current_year, self.current_month, day)
            shift = next((s for s in self.shifts 
                         if s["employee_name"] == employee_name and 
                         s["date"] == shift_date.strftime("%Y-%m-%d")), None)
            
            if shift:
                hours = self.calculate_shift_hours(shift)
                info_text = f"""📋 Информация о смене:

👤 Работник: {shift['employee_name']}
📅 Дата: {shift['date']}
🔄 Тип смены: {shift.get('shift_type', 'Не указан')}
⏰ Время: {shift.get('start_time', 'Не указано')} - {shift.get('end_time', 'Не указано')}
⏱️ Продолжительность: {hours} часов
🏷️ Категория: {shift.get('category', 'Другое')}
🆔 ID смены: {shift['id']}
"""
                messagebox.showinfo("Информация о смене", info_text, parent=self.root)
            else:
                messagebox.showinfo("Информация", "В этой ячейке нет смены", parent=self.root)
    
    def delete_all_shifts_for_day(self):
        """Удаление всех смен за выбранный день"""
        selection = self.schedule_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите день для удаления смен", parent=self.root)
            return
        
        # Получаем день из выбранной колонки
        column = self.schedule_tree.identify_column(self.root.winfo_pointerx() - self.schedule_tree.winfo_rootx())
        
        if column and column != '#0':
            day = int(column[1:])
            
            if messagebox.askyesno("Подтверждение", 
                                  f"Удалить ВСЕ смены за {day} число?", 
                                  parent=self.root):
                shift_date = date(self.current_year, self.current_month, day)
                
                # Удаляем все смены за этот день
                self.shifts = [s for s in self.shifts 
                              if s["date"] != shift_date.strftime("%Y-%m-%d")]
                
                # Пересчитываем часы
                self.calculate_hours()
                
                self.update_schedule_display()
                self.status_bar.config(text=f"Все смены за {day} число удалены")
                messagebox.showinfo("Успех", f"Все смены за {day} число удалены", parent=self.root)
    
    def generate_month(self):
        """Генерация смен на месяц"""
        if not self.employees:
            messagebox.showwarning("Внимание", "Нет работников для планирования", parent=self.root)
            return
        
        # Получаем количество дней в месяце
        _, num_days = monthrange(self.current_year, self.current_month)
        
        if messagebox.askyesno("Подтверждение", 
                              f"Сгенерировать смены на {self.get_month_name()}?\nСуществующие смены будут удалены.", 
                              parent=self.root):
            # Очищаем смены за текущий месяц
            month_shifts = []
            for shift in self.shifts:
                try:
                    shift_date = datetime.strptime(shift["date"], "%Y-%m-%d").date()
                    if not (shift_date.year == self.current_year and shift_date.month == self.current_month):
                        month_shifts.append(shift)
                except ValueError:
                    month_shifts.append(shift)
            
            self.shifts = month_shifts
            
            # Генерируем смены (примерный алгоритм)
            shift_types_list = list(self.shift_types_data.keys())
            
            for day in range(1, num_days + 1):
                day_date = date(self.current_year, self.current_month, day)
                day_of_week = day_date.weekday()
                
                for employee in self.employees:
                    # Простой алгоритм распределения смен
                    # Можно сделать более сложную логику
                    if day % 3 == employee["id"] % 3:  # Примерное распределение
                        shift_type = shift_types_list[(day + employee["id"]) % len(shift_types_list)]
                        shift_data = self.shift_types_data[shift_type]
                        
                        shift = {
                            "id": len(self.shifts) + 1,
                            "employee_id": employee["id"],
                            "employee_name": employee["name"],
                            "date": day_date.strftime("%Y-%m-%d"),
                            "shift_type": shift_type,
                            "start_time": shift_data.get('start', '08:00'),
                            "end_time": shift_data.get('end', '16:00'),
                            "category": employee.get("category", "Другое")
                        }
                        
                        self.shifts.append(shift)
            
            # Пересчитываем часы
            self.calculate_hours()
            
            self.update_schedule_display()
            self.status_bar.config(text=f"Смены на {self.get_month_name()} сгенерированы")
            messagebox.showinfo("Успех", f"Смены на {self.get_month_name()} сгенерированы", parent=self.root)
    
    def export_to_txt(self):
        """Экспорт графика в текстовый файл"""
        if not self.shifts:
            messagebox.showwarning("Внимание", "Нет данных для экспорта", parent=self.root)
            return
        
        try:
            filename = f"график_{self.current_year}_{self.current_month:02d}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"График смен - {self.get_month_name()} {self.current_year}\n")
                f.write("=" * 50 + "\n\n")
                
                # Группируем смены по сотрудникам
                employees_shifts = {}
                for shift in self.shifts:
                    try:
                        shift_date = datetime.strptime(shift["date"], "%Y-%m-%d")
                        if shift_date.year == self.current_year and shift_date.month == self.current_month:
                            emp_name = shift["employee_name"]
                            if emp_name not in employees_shifts:
                                employees_shifts[emp_name] = []
                            employees_shifts[emp_name].append(shift)
                    except ValueError:
                        continue
                
                # Записываем по сотрудникам
                for emp_name, shifts in employees_shifts.items():
                    f.write(f"\n{emp_name}:\n")
                    shifts.sort(key=lambda x: x["date"])
                    
                    total_hours = 0
                    for shift in shifts:
                        shift_date = datetime.strptime(shift["date"], "%Y-%m-%d")
                        hours = self.calculate_shift_hours(shift)
                        total_hours += hours
                        
                        f.write(f"  {shift_date.day:2d} - {shift['shift_type']}")
                        if shift.get('start_time') and shift.get('end_time'):
                            f.write(f" ({shift['start_time']}-{shift['end_time']})")
                        f.write(f" - {hours} ч\n")
                    
                    # Добавляем итог по сотруднику
                    f.write(f"  Всего: {len(shifts)} смен, {total_hours:.1f} часов\n")
                
                # Статистика
                f.write("\n" + "=" * 50 + "\n")
                total_shifts = sum(len(shifts) for shifts in employees_shifts.values())
                total_hours = 0
                for shifts in employees_shifts.values():
                    for shift in shifts:
                        total_hours += self.calculate_shift_hours(shift)
                
                f.write(f"Всего сотрудников: {len(employees_shifts)}\n")
                f.write(f"Всего смен: {total_shifts}\n")
                f.write(f"Всего часов: {total_hours:.1f}\n")
                f.write(f"Дата экспорта: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            
            self.status_bar.config(text=f"График экспортирован в {filename}")
            messagebox.showinfo("Успех", f"График экспортирован в файл:\n{filename}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {str(e)}", parent=self.root)
    
    def clear_month(self):
        """Очистка всех смен за текущий месяц"""
        if not self.shifts:
            messagebox.showinfo("Информация", "Нет смен для очистки", parent=self.root)
            return
        
        if messagebox.askyesno("Подтверждение", 
                              f"Очистить ВСЕ смены за {self.get_month_name()} {self.current_year}?", 
                              parent=self.root):
            # Фильтруем смены, оставляя только не из текущего месяца
            filtered_shifts = []
            for shift in self.shifts:
                try:
                    shift_date = datetime.strptime(shift["date"], "%Y-%m-%d").date()
                    if not (shift_date.year == self.current_year and shift_date.month == self.current_month):
                        filtered_shifts.append(shift)
                except ValueError:
                    filtered_shifts.append(shift)
            
            self.shifts = filtered_shifts
            
            # Пересчитываем часы
            self.calculate_hours()
            
            self.update_schedule_display()
            self.status_bar.config(text=f"Все смены за {self.get_month_name()} очищены")
            messagebox.showinfo("Успех", f"Все смены за {self.get_month_name()} очищены", parent=self.root)
    
    def open_color_settings(self):
        """Открыть настройки цветов"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки цветов")
        settings_window.geometry("400x500")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        frame = ttk.Frame(settings_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Настройки цветов приложения", 
                font=('Segoe UI', 16, 'bold')).pack(pady=(0, 20))
        
        # Показываем текущие цвета
        colors_frame = ttk.LabelFrame(frame, text="Текущая цветовая схема", padding=10)
        colors_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        for name, color in self.colors.items():
            color_frame = tk.Frame(colors_frame)
            color_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(color_frame, text=name, width=15, anchor=tk.W).pack(side=tk.LEFT)
            color_display = tk.Frame(color_frame, width=100, height=25, bg=color)
            color_display.pack(side=tk.LEFT, padx=10)
            color_display.pack_propagate(False)
            
            tk.Label(color_frame, text=color).pack(side=tk.LEFT)
        
        # Кнопка сброса цветов
        ttk.Button(frame, text="🔄 Сбросить цвета", 
                  command=self.reset_colors, style='Warning.TButton').pack(pady=10)
    
    def reset_colors(self):
        """Сброс цветов к значениям по умолчанию"""
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'light': '#ecf0f1',
            'dark': '#2c3e50',
            'background': '#f5f7fa',
            'card': '#ffffff',
            'border': '#dcdde1',
            'info': '#17a2b8'
        }
        
        self.setup_styles()
        self.update_schedule_display()
        messagebox.showinfo("Успех", "Цвета сброшены к значениям по умолчанию", parent=self.root)
    
    def show_statistics(self):
        """Показать общую статистику"""
        total_employees = len(self.employees)
        total_shifts = len(self.shifts)
        total_hours = sum(data["total_hours"] for data in self.hours_counter.values())
        
        if total_employees == 0:
            stats_text = "📊 Общая статистика:\n\n👥 Работников: 0\n📅 Смен: 0\n⏱️ Часов: 0"
        else:
            stats_text = f"""📊 Общая статистика:

👥 Работников: {total_employees}
📅 Смен: {total_shifts}
⏱️ Часов: {total_hours:.1f}
🏷️ Категорий: {len(self.categories)}
🔄 Типов смен: {len(self.shift_types_data)}

📈 Среднее на работника: {total_shifts/total_employees:.1f} смен, {total_hours/total_employees:.1f} часов"""
        
        messagebox.showinfo("Общая статистика", stats_text, parent=self.root)
    
    def print_schedule(self):
        """Печать графика"""
        messagebox.showinfo("Печать", "Функция печати графика", parent=self.root)
        # Здесь можно добавить логику печати или экспорта в PDF
    
    def on_button_hover(self, button):
        """Эффект при наведении на кнопку"""
        button.config(relief=tk.SUNKEN)
    
    def on_button_leave(self, button, color):
        """Эффект при уходе с кнопки"""
        button.config(relief=tk.RAISED, bg=color)
    
    def update_statistics(self):
        """Обновление статистики"""
        total_shifts_this_month = 0
        total_hours_this_month = 0
        
        for shift in self.shifts:
            try:
                shift_date = datetime.strptime(shift["date"], "%Y-%m-%d").date()
                if shift_date.year == self.current_year and shift_date.month == self.current_month:
                    total_shifts_this_month += 1
                    total_hours_this_month += self.calculate_shift_hours(shift)
            except ValueError:
                continue
        
        stats_text = f"Работников: {len(self.employees)} | "
        stats_text += f"Смен в этом месяце: {total_shifts_this_month} | "
        stats_text += f"Часов в этом месяце: {total_hours_this_month:.1f}"
        
        # Фильтр по категории
        if self.filter_category != "Все категории":
            filtered_employees = [emp for emp in self.employees 
                                if emp.get("category") == self.filter_category]
            stats_text += f" | Фильтр: {self.filter_category} ({len(filtered_employees)} чел.)"
        
        self.stats_label.config(text=stats_text)

def main():
    root = tk.Tk()
    
    # Иконка приложения
    try:
        root.iconbitmap('schedule_icon.ico')
    except:
        pass
    
    app = ModernEmployeeScheduler(root)
    
    def on_closing():
        if app.auto_save_id:
            root.after_cancel(app.auto_save_id)
        
        if messagebox.askokcancel("Выход", "Сохранить данные перед выходом?", parent=root):
            app.save_data()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()