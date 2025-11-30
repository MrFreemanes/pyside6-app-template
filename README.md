# PySide6 App Template

Универсальный шаблон для быстрого создания приложений на **PySide6**  
с поддержкой многопроцессности, логирования, графиков и расширяемой архитектуры.

---

## Возможности

- [x] Модульная структура проекта.
- [x] Многопроцессность через `multiprocessing.Queue`.
- [x] Связка Qt $\leftrightarrow$ Worker№1 Worker№2 и т.д. через "Bridge" (мост) и 2 очереди.
- [x] Гибкий логгер с авто-созданием папки в `AppData\Roaming`.
- [x] Поддержка **matplotlib**.
- [x] Поддержка от 1 до n количества процессов.
- [x] Простое добавление контекстного меню на виджеты (через `attach_context_menu`).
- [x] Сохранение графика через контекстное меню.
- [x] Базовые классы для быстрого наследования (`BaseBridge`, `BaseWindow`, `BaseWorker`, `BaseGraph`).
- [x] Простое создание приложения по шаблону, достаточно реализовать метод с "вычислениями" в `Worker` и
  взаимодействовать с ним в
  `MainWindow` через `Bridge`.

---

## Как создать свое приложение по шаблону

1. Скопируй шаблон.
2. Используй стандартный воркер `Worker` если тебе нужен 1 Worker-процесс или создай свой наследуя `BaseWorker`.
3. Используй стандартный `Bridge` или создай совой наследуя `BaseBridge`.
4. Создай свое окно, наследуя `BaseWindow`.
5. Если нужно, создай свой график, наследуя `BaseGraph`, и подключи его к интерфейсу.
6. Настрой callback для отправки задачи и выполнения действий после/во время ее выполнения:
    - Создай метод в `MainWindow` для отображения конечных расчетов (и если надо промежуточных).
    - Просто отправляй задачу через
      `self.bridge.send_task(name_task='calc', params=Any, progress_handler=self.name_method, done_handler=self.name_done_method)` в методе
      подключенном например к кнопке.

---

## Примеры:

### Чтобы отправить задачу в стандартный воркер:

В `MainWindow` создаем методы для отображения конечного и промежуточного результата (если надо).
Создаем задачу для стандартного воркера (Worker):

```python
# Код работает при использовании стандартного класса Worker.
from gui.base_window import BaseWindow
from config.config import Result


class MainWindow(BaseWindow):
    ...

    def _click_btn_1(self):
        self.bridge.send_task(
            'calc', params=100,
            # метод для промежуточных данных (можно не создавать).
            progress_handler=self._show_process_graph,
            # метод для итоговых данных.
            done_handler=self._done_graph
        )

    def _done_graph(self, result: Result):
        self.ui.progress_bar.setValue(100)
        ...

    def _show_process_graph(self, result: Result):
        self.ui.progress_bar.setValue(result.progress)
        ...


"""
В этом коде, Worker будет выполнять задачу 
и если он возвращает промежуточные значения,
то будет выполняться self._show_process_graph(result).
На последней итерации будут получены конечные данные
и выполниться метод self._done_graph(result).
Это возможно благородя Status.RUN, Status.DONE
при передаче значений из Worker.
"""
```

### Если у вас 2 и более воркеров:

1. Добавляем в класс `TaskType` в `config\config.py` их название:
    - ```python
      class TaskType:
        WORKER = 'Worker'
        WRITER = 'Writer'
        WORKER_1 = 'NAME_WORKER_1' 
        # ВАЖНО: имена обязательно должны совпадать
        # с названием класса вашего воркера.
      ```
2. Добавляем его в `logs\logger_cfg.py` в виде `'log_worker_{NAME_WORKER}''`, если нужны логи.
3. Чтобы отправить задачу определенному воркеру надо:
    - Уточнить его название с помощью `TaskType` при отправке задачи:
      ```python
      from config.config import TaskType
      from gui.base_window import BaseWindow 
      
      class MainWindow(BaseWindow):
        ...
        def _run(self):
          self.bridge.send_task(
            'calc', 100, 
            task_type=TaskType.NAME_WORKER # По умолчанию = TaskType.WORKER
          )
      ```
    - Если нужны callback методы, то передаем их название как в первом примере.

### Как создать еще один воркер-процесс:

1. Создаем класс-наследник от `BaseWorker`.
2. Создаем метод нагрузки и подключаем его через `@BaseWorker.register_task('calc')`
   (можно несколько методов, но с разными именами).
3. Пример метода:
   ```python
   @BaseWorker.register_task('calc') # название которое будет в Task(...)
   def calc(self) -> None:
       """
       :self.item: Task from config/config.py
       """
       number = self.item.num # Данные которые пришли вместе с Task
       check_list = {1, 2}
    
       @lru_cache(maxsize=32)
       def calc(num):
           if num in (1, 2):
               return 1
           res = calc(num - 1) + calc(num - 2)
           if num not in check_list:
               # Кидаем промежуточный результат.
               self.send_result(result=(num, res), status=Status.RUN, progress=int(num / number * 100))
               check_list.add(num)
               time.sleep(0.05)  # Видимость нагрузки
           return res
    
       result = calc(number)
    
       self.logger.debug('result: %s', result)
       # Кидаем конечный результат.
       self.send_result(result=(number, result), status=Status.DONE, progress=100)w
   ```
4. Обращаемся в `self.bridge.send_task(name_task='calc')` по переданному в `register_task('calc')` имени,
   если метод был создан не в Worker то, смотрим пункт 2 - Если у вас 2 и более воркеров или другое имя класса.

### Как создать Bridge:

1. Наследуемся от `BaseBridge` и реализуем `_handle_result()`.
2. Пример реализации:
    ```python
    def _handle_result(self, result: Result) -> None:
        match result.status:
            case Status.RUN:
                self.result_signal.emit(result)
            case Status.DONE:
                self.result_signal.emit(result)
                self.logger.debug('Получены последние данные')
            case Status.ERROR:
                self.error_signal.emit(result.text_error)
                self.logger.debug('Получена ошибка: %s', result.text_error)
            case _:
                self.error_signal.emit(f'Статус не определен: {result.status}')
                self.logger.warning('Статус не определен: %s', result.status)
    ```
3. В `main.py` при создании `MainWindow` передаем созданный Bridge.

### Как создать график:

1. Реализуем класс наследник от `BaseGraph` и реализуем 2 метода для отрисовки во время/после выполнения расчетов.
2. Создаем объект графика в `MainWindow` и передаем в него widget на котором будет строиться график
   (если на нем есть layout он будет использован, если нет то будет создан новый)
3. В методах callback которые принимают результат выполнения задачи нужно использовать методы класса-графика для
   своевременной отрисовки.
4. Пример реализации:
   ```python
   from PySide6.QtWidgets import QWidget

   from gui.widgets.graphs.base_graph import BaseGraph
   from gui.helpers.widget_overrides import attach_context_menu

   
   class Graph(BaseGraph):
    def __init__(self, target_widget: QWidget, *, title: str = 'График'):
        super().__init__(target_widget, title)

        self.x = []
        self.y = []

        (self.line,) = self.ax.plot([], [], color='blue')

        self.show_grid()
        
        # Создание контекстного меню (правой кнопкой мыши по графику).
        attach_context_menu(self.canvas, {'Сохранить график': self.save_graph})

    def plot_realtime(self, new_x: int, new_y: int) -> None:
        """Отрисовка графика при получении промежуточных данных"""
        self.x.append(new_x)
        self.y.append(new_y)

        if len(self.x) % 2 == 0:
            self.ax.relim()
            self.ax.autoscale()

        self.line.set_data(self.x, self.y)
        self.canvas.draw_idle()

    def plot_final(self, x: int, y: int) -> None:
        """Отрисовка финального графика"""
        self.x.append(x)
        self.y.append(y)

        self.line.set_data(self.x, self.y)
        self.autoscale()

        self.x.clear()
        self.y.clear()
   ```

### Как работает получение и отправка задач

1. Отправка: `MainWindow (self.bridge.send_task(...))` $\to$
   `Bridge` $\to$ `Queue` $\to$
   `Worker (если название класса и task_type совпадают)`
2. Получение: `Worker (self.send_result(...))` $\to$ `Queue` $\to$
   `Bridge` $\to$ `MainWindow (выполняются методы если их имена были переданы в Task)`

---

## Будущие улучшения

- [ ] Поддержка Linux и macOS путей для логов.
- [ ] Добавить пример асинхронного воркера.
