#! /bin/bash
#
# Written by Martin Thorsen Ranang, 2002.
#
file=$1

cat /dev/null > $file;

for a in `grep "\acrodef" *.tex \
	  | cut -d ':' -f 2 \
	  | cut -d '{' -f 2 \
	  | sed 's/}//g' \
	  | grep -v "\(^IDI$\|^IME$\|^NTNU$\|^UNM$\|^MF$\)" \
	  |sort | uniq`; do
    echo "\acs{$a}&\acl{$a}\\\\" >> $file;
done
