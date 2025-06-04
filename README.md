## Разработан сервис на FastAPI, который:
1.	Дообучит DistilBERT на датасете отзывов (IMDB)
2.	Сохранит векторные представления текстов в PostgreSQL
3.	Реализует асинхронный pipeline через Celery + Redis
4.	Предоставит REST API для поиска похожих отзывов по смыслу

## Список эндпоинтов:
- POST http://localhost:8000/api/find_similar - поиск похожих отзывов по смыслу
  Формат запроса: {"text": "similar_review"}

- POST http://localhost:8000/api/add_review - добавление отзыва
    Формат запроса: {"text": "new_review"}

- GET http://localhost:8000/api/status/{task_id} - проверка статуса задачи

## Запуск проекта:
1. pip install -r requirements.txt
2. docker-compose up -d
3. celery -A app.celery_app worker --loglevel=info -P solo
4. uvicorn main:app --reload
