# $Id$
#

figures: ttpdarchitecture.ps

%.ps: %.mp
	TEX=latex mpost $< && tex mproof.tex $*.[0-9] && dvips -o $*.ps mproof.dvi

$(figures):

LATEX = latex
MAKEINDEX = makeindex
DVIPS = dvips
BIBTEX = bibtex

#SUBDIRS = statistics macros src

PS_DOCS = ttpd_documentation.ps
INDICES = ttpd_documentation.dnd ttpd_documentation.snd
BIBS = ttpd_documentation.bbl #bu1.bbl bu2.bbl

docs: figures helpdoc srcdoc dvi $(BIBS) $(INDICES)

%.dnd: %.ddx
	./mkalist.sh alist.txt; \
	$(MAKEINDEX) -o $@ $<

%.snd: %.sdx
	$(MAKEINDEX) -o $@ $<

dvi: ttpd_documentation.tex 
	echo "Running LaTeX ..." ; \
	$(LATEX) $< ; \
	base=`echo $< |sed 's/\.tex//' ` ; \
	latex_count=5 ; \
	while egrep -s 'Rerun (LaTeX|to get cross-references right)' \
		$$base.log && [ $$latex_count -gt 0 ] ; \
		do \
			echo "Rerunning LaTeX ..." ; \
			$(LATEX) $< ;\
	    		latex_count=`expr $$latex_count - 1` ; \
		done

srcdoc:
	./mksrcdoc.sh

helpdoc:
	./mkhelpdoc.sh

%.ps: %.dvi
	$(DVIPS) -o $@ $<

%.bbl: %.aux
	$(BIBTEX) $<

pkgdata_DATA = docs

ps: $(PS_DOCS)

clean:
	for f in `echo "$(figures)" |sed 's/\.ps//g' -` mproof; do \
		rm -f $$f.dvi $$f.[0-9] $$f.ps $$f.log $$f.mpx; \
	done; \
	rm -f *~ ttpd_documentation.dvi \
	*.lof *.log *.lot \
	*.idx *.ilg *.ind *.ist \
	*.ndx *.nnd \
	*.toc *.aux \
	*.bbl *.blg \
	*.cdx *.cnd *.ddx *.dnd *.sdx \
	rm -f $(PS_DOCS) $(INDICES)
