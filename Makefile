lint:
	ruff check src; \
	exit 0;

lint_and_fix:
	ruff check src --fix; \
	black src; \
	exit 0;