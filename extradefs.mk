## $Id$
##
## File to be included by other Automake files.
##
## Copyright (C) 2009 by Martin Thorsen Ranang

initdir = /etc/init.d
statedir = /var

tuc_command = /home/tore/export/buster/busestuc
tuc_encoding = utf-8
tuc_user = ttpd
tuc_group = ttpd
originating_phone_number = 1939
trans_id = LINGSMSIN

lingit_web_site = busstuc.lingit.no
www_document_root = ${pkglibdir}/www/${lingit_web_site}
statistics_dir = ${pkglibdir}/statistics
sms_statistics_dir = ${statistics_dir}/sms
sms_statistics_export_dir = ${www_document_root}/sms_stats
web_statistics_dir = ${statistics_dir}/web
web_statistics_export_dir = ${www_document_root}/web_stats

lockdir = ${statedir}/lock
logdir = ${statedir}/log
rundir = ${statedir}/run

pkginitdir = ${initdir}

pkglockdir = ${lockdir}/${PACKAGE_TARNAME}
pkglogdir = ${logdir}/${PACKAGE_TARNAME}
pkgrundir = ${rundir}/${PACKAGE_TARNAME}

edit = sed \
	-e 's|@PACKAGE[@]|$(PACKAGE)|g' \
	-e 's|@PACKAGE_NAME[@]|$(PACKAGE_NAME)|g' \
	-e 's|@PACKAGE_TARNAME[@]|$(PACKAGE_TARNAME)|g' \
	-e 's|@PACKAGE_VERSION[@]|$(PACKAGE_VERSION)|g' \
	-e 's|@PYTHON[@]|$(PYTHON)|g' \
	-e 's|@VERSION[@]|$(VERSION)|g' \
	-e 's|@bindir[@]|$(bindir)|g' \
	-e 's|@initdir[@]|$(initdir)|g' \
        -e 's|@lingit_web_site[@]|$(lingit_web_site)|g' \
        -e 's|@originating_phone_number[@]|$(originating_phone_number)|g' \
	-e 's|@pkginitdir[@]|$(pkginitdir)|g' \
        -e 's|@pkglibdir[@]|$(pkglibdir)|g' \
	-e 's|@pkglockdir[@]|$(pkglockdir)|g' \
	-e 's|@pkglogdir[@]|$(pkglogdir)|g' \
	-e 's|@pkgrundir[@]|$(pkgrundir)|g' \
        -e 's|@pkgdatadir[@]|$(pkgdatadir)|g' \
        -e 's|@prefix[@]|$(prefix)|g' \
        -e 's|@pythondir[@]|$(pythondir)|g' \
        -e 's|@sbindir[@]|$(sbindir)|g' \
        -e 's|@statistics_dir[@]|$(statistics_dir)|g' \
        -e 's|@statistics_export_dir[@]|$(statistics_export_dir)|g' \
        -e 's|@trans_id[@]|$(trans_id)|g' \
        -e 's|@tuc_command[@]|$(tuc_command)|g' \
        -e 's|@tuc_encoding[@]|$(tuc_encoding)|g' \
        -e 's|@tuc_group[@]|$(tuc_group)|g' \
        -e 's|@tuc_user[@]|$(tuc_user)|g' \
        -e 's|@www_document_root[@]|$(www_document_root)|g'
