#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import re
from pathlib import Path
from typing import List, Set, Union

import aiofiles
import click
from loguru import logger


class PhoneExtractor:
    """Класс для извлечения и форматирования телефонных номеров в формат +7(YYY)XXX-XX-XX."""

    PHONE_PATTERN = re.compile(
        r"(?:(?:\+7|8)[\s\-.()\"]*)(?:\d[\s\-.()\"]*)(?:\d[\s\-.()\"]*)(?:\d[\s\-.()\"]*)(?:\d[\s\-.()\"]*)(?:\d[\s\-.()\"]*)(?:\d[\s\-.()\"]*)(?:\d[\s\-.()\"]*)(?:\d[\s\-.()\"]*)(?:\d[\s\-.()\"]*)(?:\d[\s\-.()\"]*)|(?:7|8)?\d{10}"
    )
    DIGITS_PATTERN = re.compile(r"\d")

    def __init__(self):
        # Множество для хранения уникальных номеров
        self._seen_phones: Set[str] = set()

    def _format_phone(self, digits: str) -> str:
        """Форматирует 11-значный номер в +7(YYY)XXX-XX-XX."""
        return f"+7({digits[1:4]}){digits[4:7]}-{digits[7:9]}-{digits[9:11]}"

    def extract_phones(self, text: str) -> List[str]:
        """Извлекает уникальные телефонные номера из текста."""
        self._seen_phones.clear()
        formatted_phones = []

        for match in self.PHONE_PATTERN.finditer(text):
            # Удаляем все нецифровые символы
            digits = "".join(self.DIGITS_PATTERN.findall(match.group()))

            # Обработка номеров без кода страны (добавляем 7)
            if len(digits) == 10:
                digits = "7" + digits

            if len(digits) == 11 and digits[0] in "78":
                formatted = self._format_phone(digits)
                if formatted not in self._seen_phones:
                    formatted_phones.append(formatted)
                    self._seen_phones.add(formatted)

        return formatted_phones

    async def process_file(self, file_path: Union[str, Path]) -> List[str]:
        file_path = Path(file_path)
        try:
            # Асинхронное чтение текстового файла
            async with aiofiles.open(file_path, encoding="utf-8") as file:
                text = await file.read()
            return self.extract_phones(text)
        except Exception as e:
            logger.error(f"Ошибка обработки файла {file_path}: {e}")
            return []

    async def save_to_file(self, phones: List[str], output_file: Union[str, Path]) -> None:
        try:
            async with aiofiles.open(output_file, "w", encoding="utf-8") as file:
                await file.write("\n".join(phones) + "\n")
            logger.info(f"Результаты сохранены в {output_file}")
        except Exception as e:
            logger.error(f"Ошибка сохранения в {output_file}: {e}")


async def process_files(input_files: List[Path]) -> List[str]:
    extractor = PhoneExtractor()

    # Создаем задачи для параллельной обработки всех файлов
    tasks = [extractor.process_file(file) for file in input_files]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Собираем уникальные номера
    unique_phones = []
    seen = set()
    for result in results:
        if isinstance(result, list):
            for phone in result:
                if phone not in seen:
                    unique_phones.append(phone)
                    seen.add(phone)

    return unique_phones


@click.group()
def cli():
    """Утилита для извлечения телефонных номеров из текста."""
    pass


@cli.command()
@click.argument("input_files", type=click.Path(exists=True, path_type=Path), nargs=-1)
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Файл для сохранения результатов")
def from_files(input_files, output):
    """Извлекает телефонные номера из нескольких файлов."""
    if not input_files:
        click.echo("Файлы для обработки не указаны.")
        return

    phones = asyncio.run(process_files(input_files))

    if not phones:
        click.echo("Телефонные номера не найдены.")
        return

    if output:
        asyncio.run(PhoneExtractor().save_to_file(phones, output))
    else:
        click.echo(f"Найдено {len(phones)} уникальных номеров:")
        for phone in phones:
            click.echo(phone)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Файл для сохранения результатов")
def from_file(input_file, output):
    """Извлекает телефонные номера из текстового файла."""
    phones = asyncio.run(process_files([input_file]))

    if not phones:
        click.echo("Телефонные номера не найдены.")
        return

    if output:
        asyncio.run(PhoneExtractor().save_to_file(phones, output))
    else:
        click.echo("Найденные номера:")
        for phone in phones:
            click.echo(phone)


@cli.command()
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Файл для сохранения результатов")
def from_text(output):
    """Извлекает телефонные номера из введенного текста."""
    click.echo("Введите текст (Ctrl+D для завершения):")
    text = click.get_text_stream("stdin").read()

    phones = PhoneExtractor().extract_phones(text)

    if not phones:
        click.echo("Телефонные номера не найдены.")
        return

    if output:
        asyncio.run(PhoneExtractor().save_to_file(phones, output))
    else:
        click.echo("Найденные номера:")
        for phone in phones:
            click.echo(phone)


if __name__ == "__main__":
    cli()
