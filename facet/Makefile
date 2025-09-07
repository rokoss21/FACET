.PHONY: help install fmt lint validate examples json clean

PY=python
PKG=facet
EXAMPLES=$(shell ls ../examples/*.facet 2>/dev/null || true)

help:
	@echo "FACET Makefile targets:"
	@echo "  make install     - install package in editable mode"
	@echo "  make fmt         - format all .facet files"
	@echo "  make lint        - lint all .facet files"
	@echo "  make validate    - validate all .facet files"
	@echo "  make json        - generate JSON for examples"
	@echo "  make examples    - same as json"
	@echo "  make clean       - remove generated JSON in examples"

install:
	$(PY) -m pip install -e .

fmt:
	@if [ -n "$(EXAMPLES)" ]; then \
	  for f in $(EXAMPLES); do echo "fmt $$f"; python3 -m facet.cli fmt $$f; done; \
	else echo "No examples/*.facet found."; fi

lint:
	@if [ -n "$(EXAMPLES)" ]; then \
	  for f in $(EXAMPLES); do echo "lint $$f"; python3 -m facet.cli lint $$f; done; \
	else echo "No examples/*.facet found."; fi

validate:
	@if [ -n "$(EXAMPLES)" ]; then \
	  for f in $(EXAMPLES); do echo "validate $$f"; python3 -m facet.cli validate $$f; done; \
	else echo "No examples/*.facet found."; fi

json examples:
	@if [ -n "$(EXAMPLES)" ]; then \
	  for f in $(EXAMPLES); do \
	    out=$${f%.facet}.json; \
	    echo "to-json $$f -> $$out"; \
	    python3 -m facet.cli to-json $$f > $$out; \
	  done; \
	else echo "No examples/*.facet found."; fi

clean:
	@find ../examples -name '*.json' -delete 2>/dev/null || true
	@echo "Cleaned generated JSON in examples/"
