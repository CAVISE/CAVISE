# Build documentation for CAVISE project.

SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

DOXYFILE := doxyfile

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile auto-generate-doxygen clean

auto-generate-doxygen:
	@echo "auto-generating doxygen docs for Artery..."
	@mkdir -p source/doxygen/cavise
	@cd ..; doxygen docs/$(DOXYFILE)
	@cd ..; doxysphinx build docs/$(SOURCEDIR) docs/$(BUILDDIR) docs/$(DOXYFILE)

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	@rm -r source/doxygen
	@echo "removed source/doxygen"
	@$(SPHINXBUILD) -M clean "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# TODO: fix resources location, should be /build/html/doxygen/... instead of /build/doxygen...
html:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@cp -r $(BUILDDIR)/doxygen $(BUILDDIR)/html