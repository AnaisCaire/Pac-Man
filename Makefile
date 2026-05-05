
install:
	uv sync

run:
	UV_SKIP_WHEEL_FILENAME_CHECK=1 uv run pac-man.py config.json