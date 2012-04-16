#!/bin/sh
PRODUCTNAME='ploneformgen'
I18NDOMAIN='ploneformgen'

# Synchronise the .pot with the templates.
/opt/python/python-2.6/bin/i18ndude rebuild-pot --pot locales/${PRODUCTNAME}.pot --create ${I18NDOMAIN} .

# Synchronise the resulting .pot with the .po files
/opt/python/python-2.6/bin/i18ndude sync --pot locales/${PRODUCTNAME}.pot locales/*/LC_MESSAGES/${PRODUCTNAME}.po


