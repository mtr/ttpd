#! /bin/bash
#
# $Id: mksrcdoc.sh,v 1.2 2002/05/23 14:17:51 mtr Exp $
#
# Copyright (C) 2002 by Martin Thorsen Ranang
#

cat /dev/null > include_src.tex; 

for f in `cat lst_src.txt |grep -v "^#" |tr '\n' ' '`; do
    g=`echo $f |sed 's/^src\///g' -`; 
    lgrind -i -c -lpy src/$f > doc_src/$g.tex;
    h=`echo $g |sed 's/\_/\\\_/g' - `;
    echo "\\section{$h}\\lgrindfile{doc_src/$g.tex}" >> include_src.tex;
done
