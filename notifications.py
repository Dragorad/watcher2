# notifications.py

from plyer import notification

def show_notification(title, message, timeout=10):
    """
    Показва нотификация на десктопа.

    :param title: Заглавие на нотификацията
    :param message: Съдържание на нотификацията
    :param timeout: Продължителност на нотификацията в секунди (по подразбиране 10)
    """
    notification.notify(
        title=title,
        message=message,
        timeout=timeout
    )
