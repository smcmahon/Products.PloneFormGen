#!/bin/sh
# Compile .po files present in locales directory

find ./locales -name *.po | sed -e 's/\(.*\)\.po/-o \1.mo \1.po/' | xargs -t -n 3 msgfmt

