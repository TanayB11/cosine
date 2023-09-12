run:
	. env/bin/activate
	(trap 'kill 0' SIGINT; cd server && make prod & python cosine_ui.py)

env:
	python3 -m venv env
	. env/bin/activate
	pip install -r requirements.txt
