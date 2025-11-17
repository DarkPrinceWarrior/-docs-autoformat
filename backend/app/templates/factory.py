from typing import Dict, List
from app.templates.base import BaseTemplate
from app.templates.gost_vkr import GOSTVKRTemplate
from app.templates.gost_coursework import GOSTCourseworkTemplate


class TemplateFactory:
    """Фабрика для создания шаблонов форматирования"""

    _templates = {
        "gost_vkr": GOSTVKRTemplate,
        "gost_coursework": GOSTCourseworkTemplate,
    }

    @classmethod
    def create_template(cls, template_name: str) -> BaseTemplate:
        """
        Создает экземпляр шаблона по имени

        Args:
            template_name: Название шаблона

        Returns:
            Экземпляр шаблона

        Raises:
            ValueError: Если шаблон не найден
        """

        template_class = cls._templates.get(template_name)

        if not template_class:
            raise ValueError(
                f"Шаблон '{template_name}' не найден. "
                f"Доступные шаблоны: {', '.join(cls._templates.keys())}"
            )

        return template_class()

    @classmethod
    def get_available_templates(cls) -> List[Dict[str, str]]:
        """
        Возвращает список доступных шаблонов с описаниями

        Returns:
            Список словарей с информацией о шаблонах
        """

        templates_info = []

        for name, template_class in cls._templates.items():
            template_instance = template_class()
            templates_info.append(template_instance.get_template_info())

        return templates_info

    @classmethod
    def register_template(cls, name: str, template_class: type):
        """
        Регистрирует новый шаблон в фабрике

        Args:
            name: Название шаблона
            template_class: Класс шаблона (должен наследовать BaseTemplate)
        """

        if not issubclass(template_class, BaseTemplate):
            raise ValueError(
                f"Класс {template_class.__name__} должен наследовать BaseTemplate"
            )

        cls._templates[name] = template_class
