#!/usr/bin/sed -r
/^# ==== (.*) ====/{
    s|# *=+ (.*) =+|cat redhat/\1|
    e
}

#eof