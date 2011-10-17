## $Id$
##
## Copyright (C) 2009 by Lingit AS
##

doc_root = ttpd_documentation

ltx_src = $(doc_root).tex
itx_src = $(doc_root).itx
internal = $(doc_root).rix
index = $(doc_root).rid
pdf_doc = $(doc_root).pdf
bib = $(doc_root).bbl
aux = $(doc_root).aux

ignore_mp = taocparrows.mp
mp_src = $(filter-out $(ignore_mp),$(wildcard *.mp))
ps_figures = $(mp_src:.mp=.ps)

LATEX = pdflatex
MAKEINDEX = makeindex
MKINTEX = mkintex
#MKINTEX_FLAGS = --debug --index-file=$(internal)
MKINTEX_FLAGS = --index-file=$(internal)
BIBTEX = bibtex

all: figures $(pdf_doc) $(bib) $(pdf_doc) 

figures: $(ps_figures)

%.ps: %.mp
	TEX=latex mpost $*
	tex mproof.tex $*.[0-9]* && dvips -o $*.ps mproof.dvi
	mptopdf $*.*[0-9]*
	for f in $*-[0-9]*.pdf; do g=$$(echo $$f |sed 's/-/_/g' -); mv $$f $$g; done
	for i in $*.*[0-9]*; do mv $$i `echo $$i | sed 's/\./_/g'`.eps; done

$(pdf_doc): $(ltx_src) $(itx_src)
	echo "Autogenerating some documentation..."
	./mksrcdoc.sh
	./mkhelpdoc.sh
	echo "Running LaTeX ..." ; \
	$(LATEX) $< ; \
	$(MKINTEX) $(MKINTEX_FLAGS) $(doc_root) ; \
	$(MAKEINDEX) $(doc_root) ; \
	$(MAKEINDEX) -o $(index) $(internal) ; \
	base=`echo $< |sed 's/\.tex//' ` ; \
	latex_count=5 ; \
	while egrep -s 'Rerun (LaTeX|to get cross-references right)' \
		$$base.log && [ $$latex_count -gt 0 ] ; \
		do \
			echo "Rerunning LaTeX ..." ; \
			$(LATEX) $< ; \
			$(MKINTEX) $(MKINTEX_FLAGS) $(doc_root) ; \
			$(MAKEINDEX) $(doc_root) ; \
			$(MAKEINDEX) -o $(index) $(internal) ; \
	    		latex_count=`expr $$latex_count - 1` ; \
		done

$(aux): $(pdf_doc)

$(bib): $(aux)
	$(BIBTEX) $<

clean:
	for f in `echo "$(ps_figures)" |sed 's/\.ps//g' -` mproof; do \
		rm -f $$f.dvi $$f_[0-9].eps $$f_[0-9].pdf $$f.ps $$f.log $$f.mpx; \
	done; \
	rm -rf src_doc/ ; \
	rm -f include_src_src.tex \
	usage_ttpdctl.txt \
	$(doc_root).rid \
	$(doc_root).snd \
	$(doc_root).brf \
	$(doc_root).ito \
	include_src_src.tex \
	$(doc_root).rix \
	$(doc_root).out \
	usage_ttpc.txt \
	usage_ttpd.txt \
	*~ $(pdf_doc) \
	*.lof *.log *.lot \
	*.idx *.ilg *.ind *.ist \
	*.ndx *.nnd \
	*.toc *.aux \
	*.bbl *.blg \
	*.cdx *.cnd *.ddx *.dnd *.sdx