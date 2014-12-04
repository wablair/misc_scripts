#!/bin/sh
# Also needs to be set in repo:
# git config --bool core.bare true
# git config core.sharedRepository group
cd /git
chgrp -R git .
chmod -R g+rwX .
find . -type d -exec chmod g+s '{}' +
