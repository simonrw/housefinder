all: help

help:
	@echo "Commands: package test"

test:
	tox

package:
	@-rm dist/* 2>/dev/null
	python setup.py sdist bdist_wheel
	for file in dist/*; do gpg --detach-sign -a $$file; done

.PHONY: all help test package
