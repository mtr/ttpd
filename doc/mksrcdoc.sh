#! /bin/bash
#
# $Id$
#
# Copyright (C) 2002 by Martin Thorsen Ranang
#

cat /dev/null > include_src.tex; 

for f in `cat lst_src.txt |grep -v "^#" |tr '\n' ' '`; do
    g=`echo $f |sed 's/^src\///g' -`; 
    lgrind -i -c -lpy src/$f > src_doc/$g.tex;
    h=`echo $g |sed 's/\_/\\\_/g' - `;
    echo "\\section{$h}\\lgrindfile{src_doc/$g.tex}" >> include_src.tex;
done
