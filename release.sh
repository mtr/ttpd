#! /bin/bash
#

#export COMMIT_BEFORE_RELEASE=0

hg update

# Update ChangeLog
#svn2cl --break-before-msg --group-by-day --authors=AUTHORS

automake
autoconf

./configure --prefix=/usr && \
make deb_sign && \
sudo dpkg --purge ttpd && \
sudo dpkg --install $(ls -1 --sort=version dist/*.deb |tail -1)
