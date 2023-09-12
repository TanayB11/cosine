run:
	(trap 'kill 0' SIGINT; cd server && make prod & python cosine_ui.py)
