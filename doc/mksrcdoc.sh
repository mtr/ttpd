#! /bin/bash
#
# $Id$
#
# Copyright (C) 2002 by Martin Thorsen Ranang
#

docdir="src_doc"
modules="../TTP/ SocketServer"
includefile="include_src.tex"

epydoc --latex --output $docdir $modules

cat $docdir/api.tex |grep '\include' - |grep -v "Options-module" |sed "s/\\include{/\\input{$docdir\//g" - > $includefile


cat /dev/null > include_src_src.tex; 

for f in `cat lst_src.txt |grep -v "^#" |tr '\n' ' '`; do
    g=`echo $f |sed 's/^src\///g' -`; 
    lgrind -i -c -lpy ../$f > src_doc/$g.tex;
    h=`echo $g |sed 's/\_/\\\_/g' - `;
    echo "\\section{$h}\\lgrindfile{src_doc/$g.tex}" >> include_src_src.tex;
done
