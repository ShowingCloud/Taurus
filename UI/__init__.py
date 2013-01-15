#!/usr/bin/python

from config import USE_THEIR_UI

if USE_THEIR_UI:
	from UI.UI_theirs import *
else:
	from UI.UI_ours import *
