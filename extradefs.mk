## $Id$
##
## File to be included by other Automake files.
##
## Copyright (C) 2009 by Lingit AS

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
	-e 's|@account_number[@]|$(account_number)|g' \
	-e 's|@bindir[@]|$(bindir)|g' \
	-e 's|@db_host[@]|$(db_host)|g' \
	-e 's|@db_name[@]|$(db_name)|g' \
	-e 's|@db_password[@]|$(db_password)|g' \
	-e 's|@db_user[@]|$(db_user)|g' \
	-e 's|@encryption_key[@]|$(encryption_key)|g' \
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
        -e 's|@sms_statistics_dir[@]|$(sms_statistics_dir)|g' \
        -e 's|@sms_statistics_export_dir[@]|$(sms_statistics_export_dir)|g' \
        -e 's|@web_statistics_dir[@]|$(web_statistics_dir)|g' \
        -e 's|@web_statistics_export_dir[@]|$(web_statistics_export_dir)|g' \
	-e 's|@test_account_number[@]|$(test_account_number)|g' \
	-e 's|@test_encryption_key[@]|$(test_encryption_key)|g' \
        -e 's|@trans_id[@]|$(trans_id)|g' \
        -e 's|@tuc_command[@]|$(tuc_command)|g' \
        -e 's|@tuc_encoding[@]|$(tuc_encoding)|g' \
        -e 's|@tuc_group[@]|$(tuc_group)|g' \
        -e 's|@tuc_user[@]|$(tuc_user)|g' \
        -e 's|@www_document_root[@]|$(www_document_root)|g'
