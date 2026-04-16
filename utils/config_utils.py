def check_handler(handler) -> None:
    if handler is not None and not isinstance(handler, str):
        raise ValueError(f"Неверный тип handler: {type(handler)}")