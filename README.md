# PySide6 App Template

Универсальный шаблон для быстрого создания приложений на **PySide6**  
с поддержкой многопроцессности, логирования, графиков и расширяемой архитектуры.

---

## Возможности

- [x] Модульная структура проекта.
- [x] Многопроцессность через `multiprocessing.Queue`.
- [x] Связка Qt $\leftrightarrow$ Worker№1 Worker№2 и т.д. через "Bridge"-мост и 2 очереди.
- [x] Гибкий логгер с авто-созданием папки в AppData.
- [x] Поддержка **matplotlib-графиков** с обновлением в реальном времени.
- [x] Поддержка нескольких процессов или одного (в зависимости от нужды).
- [x] Простое добавление контекстного меню на виджеты (через ).
- [x] Сохранение графика через контекстное меню.
- [x] Базовые классы для быстрого наследования (`BaseWindow`, `BaseBridge`, `BaseWorker`, `BaseGraph`).

---

## Как создать свое приложение по шаблону

1. Скопируй шаблон.
2. Используй стандартный воркер (Worker) если тебе нужен 1 процесс.
3. Создай свое окно, наследуя `BaseWindow`.
4. Создай свой график, наследуя `BaseGraph`, и подключи его к интерфейсу.
5. Настрой callback для отправки задачи и выполнения действий после/во время ее выполнения:
    - Создай метод в `MainWindow` для отображения конечных расчетов (и если надо промежуточных).
    - Просто отправляй задачу через `self.bridge.send_task(Task(...))` в методе подключенном например к кнопке.

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
```

### Если у вас 2 и более воркеров, то:

1. Добавляем в класс `TaskType` в `config/config` их название:
    - ```python
      class TaskType:
        WORKER = 'Worker'
        WRITER = 'Writer'
        WORKER_1 = 'NAME_WORKER_1' 
        # ВАЖНО: имена обязательно должны совпадать
        # с названием класса вашего воркера.
      ```
2. Чтобы отправить задачу определенному воркеру надо:
    - Уточнить его название при отправке задачи:
      ```python
      from config.config import Task, TaskType
      
      task = Task(
        'calc', 100, 
        task_type=TaskType.NAME_WORKER # По умолчанию = TaskType.WORKER
      )
      ```

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
