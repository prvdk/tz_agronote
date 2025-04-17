# Извлечение телефонных номеров

Утилита для извлечения телефонных номеров из текста в формате +7(YYY)XXX-XX-XX.

## Описание

Программа обрабатывает текстовые данные и извлекает все уникальные телефонные номера, приводя их к единому формату +7(YYY)XXX-XX-XX. Поддерживаются различные форматы записи номеров, начинающихся с +7 или 8.

## Требования

- Python 3.11+
- click
- loguru
- aiofiles
- asyncio

## Установка

```bash
# Клонирование репозитория
git clone https://github.com/prvdk/tz_agronote.git
cd tz_agronote

# Установка зависимостей
pip install click loguru aiofiles
```

## Использование

Программа поддерживает три режима работы:

### 1. Извлечение номеров из файла

```bash
python phone_extractor.py from-file test_phones.txt
```

С сохранением результатов в файл:

```bash
python phone_extractor.py from-file test_phones.txt --output results.txt
```

### 2. Извлечение номеров из нескольких файлов

```bash
python phone_extractor.py from-files file1.txt file2.txt file3.txt
```

С сохранением результатов в файл:

```bash
python phone_extractor.py from-files file1.txt file2.txt file3.txt --output results.txt
```

### 3. Извлечение номеров из введенного текста

```bash
python phone_extractor.py from-text
```

С сохранением результатов в файл:

```bash
python phone_extractor.py from-text --output results.txt
```

## Примеры

Исходный текст:
```
Связаться с нами можно по телефону +7 912-345-67-89 или 8 (495) 123 45 67.
Также работает WhatsApp: +7(903) 456 78 90.
```

Результат:
```
+7(912)345-67-89
+7(495)123-45-67
+7(903)456-78-90
```

## Особенности

- Извлечение номеров в различных форматах
- Приведение к единому формату +7(YYY)XXX-XX-XX
- Сохранение только уникальных номеров
- Сохранение порядка появления номеров в тексте
- Асинхронная обработка файлов
- Параллельная обработка нескольких файлов
