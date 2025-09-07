# FACET MCP Server

**Agent-First AI Tooling** - Преобразование AI-агентов из "талантливых но неряшливых стажеров" в "высокопроизводительных менеджеров"

## 🚀 Что такое FACET MCP Server?

FACET MCP Server предоставляет AI-агентам три мощных инструмента для решения проблем с данными:

### 🛠️ Инструменты

#### 1. **execute** - Полное выполнение FACET документов
```json
{
  "name": "execute",
  "description": "Выполняет полный FACET-документ с SIMD оптимизациями",
  "parameters": {
    "facet_source": "string - Полный текст .facet документа",
    "variables": "object - Опциональные переменные для шаблонизации"
  }
}
```

#### 2. **apply_lenses** - Атомарные текстовые трансформации
```json
{
  "name": "apply_lenses",
  "description": "Применяет линзы для очистки и нормализации текста",
  "parameters": {
    "input_string": "string - Текст для обработки",
    "lenses": "array - Список линз ['dedent', 'trim', 'squeeze_spaces']"
  }
}
```

#### 3. **validate_schema** - Валидация данных
```json
{
  "name": "validate_schema",
  "description": "Проверяет JSON на соответствие схеме",
  "parameters": {
    "json_object": "object - JSON для валидации",
    "json_schema": "object - JSON Schema"
  }
}
```

## 🎯 Решаемые Проблемы

### ❌ Проблемы AI-агентов:
- Ненадежный JSON-вывод
- Сложность многошаговых задач
- "Галлюцинации" при форматировании
- Ошибки в типах данных

### ✅ Решения FACET MCP:
- **execute**: Декларативное описание пайплайнов
- **apply_lenses**: 100% надежная очистка текста
- **validate_schema**: Гарантия корректности данных

## 🚀 Быстрый Старт

### Установка
```bash
# Установка с серверными зависимостями
pip install facet-lang[server]

# Или из исходников
git clone https://github.com/rokoss21/FACET.git
cd FACET
pip install -e .[server]
```

### Запуск сервера
```bash
# Базовый запуск
facet-mcp start

# С кастомными настройками
MCP_HOST=0.0.0.0 MCP_PORT=3001 facet-mcp start
```

### Проверка инструментов
```bash
# Список доступных инструментов
facet-mcp tools

# Список линз
facet-mcp lenses

# Примеры использования
facet-mcp examples
```

## 📡 Подключение AI-агентов

### Python (LangChain)
```python
from langchain.tools import Tool
from facet_mcp import MCPClient

# Подключение к MCP серверу
client = MCPClient()
await client.connect("ws://localhost:3000")

# Создание инструментов для агента
tools = [
    Tool(
        name="execute_facet",
        description="Execute FACET documents with SIMD optimizations",
        func=lambda facet_code: asyncio.run(
            client.call_tool("execute", {"facet_source": facet_code})
        )
    ),
    Tool(
        name="apply_lenses",
        description="Clean and transform text with FACET lenses",
        func=lambda text, lenses: asyncio.run(
            client.call_tool("apply_lenses", {
                "input_string": text,
                "lenses": lenses
            })
        )
    ),
    Tool(
        name="validate_data",
        description="Validate JSON against schema",
        func=lambda data, schema: asyncio.run(
            client.call_tool("validate_schema", {
                "json_object": data,
                "json_schema": schema
            })
        )
    )
]
```

### TypeScript/JavaScript
```typescript
import { MCPClient } from 'facet-mcp-client';

const client = new MCPClient();
await client.connect('ws://localhost:3000');

// Использование инструментов
const result = await client.callTool('apply_lenses', {
  input_string: '  Hello   World  ',
  lenses: ['trim', 'squeeze_spaces']
});
```

## 🔧 Конфигурация

### Переменные окружения
```bash
# Сервер
MCP_HOST=localhost
MCP_PORT=3000
MCP_MAX_CONNECTIONS=100

# Производительность
MCP_ENABLE_SIMD=true
MCP_MAX_TEXT_SIZE_KB=1024
MCP_WORKER_THREADS=4

# Безопасность
MCP_ENABLE_RATE_LIMITING=true
MCP_MAX_REQUESTS_PER_MINUTE=60

# Логирование
MCP_LOG_LEVEL=INFO
MCP_ENABLE_FILE_LOGGING=true
```

### Конфигурационный файл
```python
from facet_mcp.config import config

# Просмотр текущей конфигурации
facet-mcp config --json

# Детальная конфигурация
facet-mcp config --verbose
```

## 📋 Примеры Использования

### 1. Очистка пользовательского ввода
```python
# Перед обработкой агент очищает текст
cleaned = await client.call_tool('apply_lenses', {
    'input_string': user_input,
    'lenses': ['trim', 'squeeze_spaces', 'normalize_newlines']
})
```

### 2. Валидация API ответов
```python
# Агент проверяет свой собственный вывод
validation = await client.call_tool('validate_schema', {
    'json_object': generated_response,
    'json_schema': api_contract_schema
})
```

### 3. Комплексная обработка данных
```python
# Полный пайплайн в одном FACET документе
result = await client.call_tool('execute', {
    'facet_source': '''
@workflow
  description: "Process user data pipeline"

@input
  raw_data: "{{user_input}}"

@processing
  steps: [
    {"lens": "normalize_newlines"},
    {"lens": "squeeze_spaces"},
    {"validate": "user_data_schema"}
  ]

@output(format="json")
  schema: {
    "type": "object",
    "required": ["processed_data", "validation_status"]
  }
''',
    'variables': {'user_input': user_provided_data}
})
```

## 🏗️ Архитектура

```
┌─────────────────┐    ┌─────────────────┐
│   AI Agent      │◄──►│  MCP Protocol   │
│                 │    │  (WebSocket)    │
└─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐
│ MCP Transport   │◄──►│ FACET MCP      │
│   Layer         │    │   Server        │
└─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐
│ FACET Engine    │    │ Schema          │
│ (SIMD Opt.)     │    │ Validator       │
└─────────────────┘    └─────────────────┘
```

## 📊 Производительность

### SIMD Оптимизации
- **dedent**: 3.72x быстрее для больших текстов
- **squeeze_spaces**: 3.55x быстрее для больших текстов
- **Автоматическое переключение**: Маленькие строки используют стандартные методы

### Масштабируемость
- **WebSocket connections**: До 100 одновременных соединений
- **Worker threads**: 4 потока для параллельной обработки
- **Memory pooling**: Эффективное управление памятью

## 🔒 Безопасность

### Rate Limiting
- Ограничение запросов: 60/min по умолчанию
- Настраиваемые лимиты через переменные окружения

### Валидация Запросов
- Проверка размера запросов (макс 1MB)
- Валидация JSON схем
- Защита от malformed данных

### Resource Limits
- Максимальный размер текста: 1MB
- Ограничение длины цепочек линз: 10
- Таймауты на все операции

## 🔧 Разработка и Тестирование

### Локальная разработка
```bash
# Установка в режиме разработки
pip install -e .[server]

# Запуск с отладкой
MCP_LOG_LEVEL=DEBUG facet-mcp start

# Тестирование инструментов
facet-mcp tools --verbose
facet-mcp examples all --verbose
```

### Docker
```dockerfile
FROM python:3.11-slim

COPY . /app
WORKDIR /app
RUN pip install -e .[server]

EXPOSE 3000
CMD ["facet-mcp", "start"]
```

## 📚 Документация

- **API Reference**: Подробное описание всех инструментов
- **Examples**: Реальные примеры использования
- **Configuration**: Полная конфигурационная документация
- **Troubleshooting**: Решение типичных проблем

## 🤝 Сообщество

- **GitHub Issues**: Сообщения об ошибках и предложения
- **GitHub Discussions**: Обсуждение идей
- **Examples Repository**: Реальные кейсы использования

---

**FACET MCP Server** - это не просто инструмент, это **новая парадигма** взаимодействия AI-агентов с данными. От "галлюцинаций и ошибок" к "детерминированности и надежности".

**Присоединяйтесь к революции AI-инструментов!** 🚀
