#! /bin/bash
#
# $Id$
#
# Copyright (C) 2002, 2009 by Lingit AS
#

. ../bin/config.sh

docdir="src_doc"
modules="$top_srcdir/lib/TTP/ SocketServer"
includefile="include_src.tex"

epydoc --latex --output $docdir $modules

cat $docdir/api.tex |grep '\include' - |grep -v "Options-module" |sed "s/\\include{/\\input{$docdir\//g" - > $includefile


cat /dev/null > include_src_src.tex; 

for f in $(cat lst_src.txt |grep -v "^#" |tr '\n' ' '); do
    g=$(echo $f \
	|sed 's/^src\///g' - \
	|sed 's/^lib\///g' - \
	|sed 's/TTP\//TTP./g' - \
	|sed 's/payex_prod\//payex_prod./g' - \
	|sed 's/payex_test\//payex_test./g' -); 
    #echo "looking for $top_srcdir/$f"
    #echo "            src_doc/$g.tex"
    lgrind -i -c -lpy $top_srcdir/$f > src_doc/$g.tex;
    h=$(echo $g |sed 's/\_/\\\_/g' - );
    echo "\\section{$h}\\lgrindfile{src_doc/$g.tex}" >> include_src_src.tex;
done
