# PySide6 App Template

Универсальный шаблон для быстрого создания приложений на **PySide6**  
с поддержкой многопроцессности, логирования, графиков и расширяемой архитектуры.

---

## Возможности

- [x] Модульная структура проекта.
- [x] Многопроцессность через `multiprocessing.Queue`.
- [x] Связка Qt $\leftrightarrow$ Worker№1 Worker№2 и т.д. через "Bridge"-мост и 2 очереди.
- [x] Гибкий логгер с авто-созданием папки в AppData.
- [x] Поддержка **matplotlib**.
- [x] Поддержка от 1 до n количества процессов.
- [x] Простое добавление контекстного меню на виджеты (через `attach_context_menu`).
- [x] Сохранение графика через контекстное меню.
- [x] Базовые классы для быстрого наследования (`BaseWindow`, `BaseWorker`, `BaseGraph`).

---

## Как создать свое приложение по шаблону

1. Скопируй шаблон.
2. Используй стандартный воркер (Worker) если тебе нужен 1 Worker-процесс.
3. Создай свое окно, наследуя `BaseWindow`.
4. Создай свой график, наследуя `BaseGraph`, и подключи его к интерфейсу.
5. Настрой callback для отправки задачи и выполнения действий после/во время ее выполнения:
    - Создай метод в `MainWindow` для отображения конечных расчетов (и если надо промежуточных).
    - Просто отправляй задачу через
      `self.bridge.send_task(Task(..., progress_handler='name_method', done_handler='name_done_method'))` в методе
      подключенном например к кнопке.

---

## Примеры:

### Чтобы отправить задачу в стандартный воркер:

В `MainWindow` создаем методы для отображения конечного и промежуточного результата (если надо).
Создаем задачу для стандартного воркера (Worker):

```python
# Код работает при использовании стандартного класса Worker.
from gui.base_window import BaseWindow
from config.config import Task, Result


class MainWindow(BaseWindow):
    ...

    def _click_btn_1(self):
        self.bridge.send_task(
            Task('calc', 100,
                 # метод для промежуточных данных (можно не создавать).
                 progress_handler='_show_process_graph',
                 # метод для итоговых данных.
                 done_handler='_done_graph')
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
      from config.config import Task, TaskType
      
      task = Task(
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
       number = self.item.num # Данные которые пришли в Task
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
               time.sleep(0.05)  # видимость нагрузки
            return res
    
       result = calc(number)
    
       self.logger.debug('result: %s', result)
       # Кидаем конечный результат.
       self.send_result(result=(number, result), status=Status.DONE, progress=100)w
   ```
4. Обращаемся в Task(...) по переданному в `register_task('calc')` имени,
   если метод был создан не в WORKER то, смотрим пункт 2 - Если у вас 2 и более воркеров.

### Как работает получение и отправка задач

1. Отправка: `MainWindow (self.bridge.send_task)` $\to$
   `Bridge` $\to$ `Queue` $\to$
   `Worker (если название класса и task_type совпадают)`
2. Получение: `Worker (self.send_result())` $\to$ `Queue` $\to$
   `Bridge` $\to$ `MainWindow (выполняются методы если их имена были переданы в Task)`

---

## Будущие улучшения

- [ ] Поддержка Linux и macOS путей для логов.
- [ ] Добавить пример асинхронного воркера.
