lint:
	ruff *.py; \
	exit 0;

lint_and_fix:
	ruff *.py --fix; \
	black *.py; \
	exit 0;