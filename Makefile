.PHONY: dev check seed clean

dev:
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

check:
	ruff check . && pytest -q

seed:
	python -m jobs.seed

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; rm -f livewire.db
