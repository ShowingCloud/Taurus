#!/usr/bin/python

import gobject, gst

gobject.threads_init()

def on_message (bus, message):
	t = message.type
	if t == gst.MESSAGE_EOS:
		pipeline.set_state(gst.STATE_NULL)
		mainloop.quit()
	elif t == gst.MESSAGE_ERROR:
		pipeline.set_state(gst.STATE_NULL)
		err, debug = message.parse_error()
		print 'Error: %s' % err, debug
		mainloop.quit()
	elif t == gst.MESSAGE_ELEMENT:
		print message.structure.get_name()
		print message.structure['percent']
		print message.structure['total']
		print message.structure['current']

def on_sync_message (bus, message):
	if message.structure is None:
		return
	message_name = message.structure.get_name()

def cb_pad_added (element, pad, islast):
	caps = pad.get_caps()
	name = caps[0].get_name()
	if 'audio' in name:
		if not __apad.is_linked(): # Only link once
			pad.link (__apad)
	elif 'video' in name:
		if not __vpad.is_linked():
			pad.link (__vpad)

mainloop = gobject.MainLoop()

pipeline = gst.Pipeline ("pipeline")
source = gst.element_factory_make ("filesrc")
source.set_property ("location", "test.mp4")
decoder = gst.element_factory_make ("decodebin2")
decoder.connect ("new-decoded-pad", cb_pad_added)
queuea = gst.element_factory_make ("queue")
queuev = gst.element_factory_make ("queue")
videoscale = gst.element_factory_make ("videoscale")
videorate = gst.element_factory_make ("videorate")
colorspace = gst.element_factory_make ("ffmpegcolorspace")
colorspace2 = gst.element_factory_make ("ffmpegcolorspace")
caps = gst.element_factory_make ("capsfilter")
caps.set_property ('caps', gst.caps_from_string ("video/x-raw-rgb, width=640, height=480, framerate=25/1"))
audioconv = gst.element_factory_make ("audioconvert")
audioenc = gst.element_factory_make ("ffenc_aac")
audioenc.set_property ('bitrate', 128000)
videoenc = gst.element_factory_make ("ffenc_mpeg4")
videoenc.set_property ('bitrate', 1024000)
muxer = gst.element_factory_make ("mp4mux")
sink = gst.element_factory_make ("filesink")
sink.set_property ("location", "out.mp4")
progress = gst.element_factory_make ("progressreport")
progress.set_property ('silent', True)
progress.set_property ('update-freq', 1)

__apad = queuea.get_pad ("sink")
__vpad = queuev.get_pad ("sink")

pipeline.add (source, decoder, queuea, queuev, audioenc, videoenc, muxer, progress, sink, colorspace, caps, videoscale, colorspace2, videorate, audioconv)
gst.element_link_many (source, decoder)
gst.element_link_many (queuev, colorspace, videoscale, videorate, caps, colorspace2, videoenc, muxer)
gst.element_link_many (queuea, audioconv, audioenc, muxer)
gst.element_link_many (muxer, progress, sink)

bus = pipeline.get_bus()
bus.add_signal_watch()
bus.connect ("message", on_message)
bus.connect ("sync-message::element", on_sync_message)

pipeline.set_state (gst.STATE_PLAYING)

mainloop.run()

pipeline.set_state (gst.STATE_NULL)
