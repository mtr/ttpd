#!/bin/sh -e
# Compile D. J. Bernstein's daemontools on Cygwin

# Need curl, tar, sed, make, patch, gcc installed

curl -LO http://cr.yp.to/daemontools/daemontools-0.76.tar.gz
sha1sum daemontools-0.76.tar.gz | grep 70a1be67e7dbe0192a887905846acc99ad5ce5b7
tar xf daemontools-0.76.tar.gz
rm -f daemontools-0.76.tar.gz
cd admin/daemontools-0.76
patch -uNp1 << 'EOF'
--- a/package/compile
+++ b/package/compile
@@ -4,7 +4,7 @@ umask 022
 test -d package || ( echo 'Wrong working directory.'; exit 1 )
 test -d src || ( echo 'Wrong working directory.'; exit 1 )

-here=`env - PATH=$PATH pwd`
+here=`env - PATH="$PATH" pwd`

 mkdir -p compile command
 test -r compile/home || echo $here > compile/home
--- a/src/error.h
+++ b/src/error.h
@@ -3,7 +3,8 @@
 #ifndef ERROR_H
 #define ERROR_H

-extern int errno;
+#include <errno.h>
+//extern int errno;

 extern int error_intr;
 extern int error_nomem;

EOF

package/compile

# http://www.tatsuyoshi.net/toyota/tech/201004.html