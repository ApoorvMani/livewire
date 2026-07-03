.PHONY: dev web check seed seed-city clean install build

install:
	cd web && npm install

dev:
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

web:
	cd web && npm run dev

check:
	ruff check . && pytest -q -v

seed:
	python -m jobs.seed

seed-city:
	python -m jobs.seed
	python -m jobs.seed

e2e:
	cd web && npx playwright test

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; rm -f livewire.db
