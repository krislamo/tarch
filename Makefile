.PHONY: default venv install dev clean

default: dev

venv:
	@[ ! -d ./venv ] && python3 -m venv venv || true

require: venv
	@bash -c "source venv/bin/activate && pip install -r requirements.txt"

dev: require
	@bash -c "source venv/bin/activate && pip install -e ."

clean:
	rm -rf venv dist tarc.egg-info
