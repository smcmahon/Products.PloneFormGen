#!/bin/sh
# Compile .po files present in locales directory

find ./locales/ -name *.po | sed -e 's/\(.*\)\.po/\/usr\/bin\/msgfmt -o \1.mo \1.po/' | xargs --replace=cmd /bin/sh -c "cmd"

