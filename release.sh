#! /bin/bash
#

#export COMMIT_BEFORE_RELEASE=0

# Update ChangeLog
svn2cl --break-before-msg --group-by-day --authors=AUTHORS

./configure --prefix=/usr && \
make deb_sign && \
sudo dpkg --purge ttpd && \
sudo dpkg --install $(ls -1 dist/*.deb |tail -1)
