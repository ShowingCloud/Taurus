#!/usr/bin/python

import re


def time2str (t):
	ms, ns = divmod (t, 1000000)
	s, ms = divmod (ms, 1000)
	m, s = divmod (s, 60)

	if m < 60:
		return "%02i:%02i.%03i" % (m, s, ms)
	else:
		h, m = divmod (m, 60)
		return "%i:%02i:%02i.%03i" % (h, m, s, ms)


def str2time (s):
	multi = 1000000000L
	ns = 0L

	lst = re.findall (r'\d+', s)

	if not re.findall (r'\d+\.\d+$', s) == []:
		ns = long (lst.pop().ljust (9, '0') [0 : 10])

	while len (lst) > 0:
		ns += long (lst.pop()) * multi
		multi *= 60L

	return ns
