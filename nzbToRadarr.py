#!/usr/bin/env python2
# coding=utf-8

import sys

import nzbToMedia

section = 'Radarr'
result = nzbToMedia.main(sys.argv, section)
sys.exit(result)
