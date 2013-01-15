#!/usr/bin/python


class MediaTypes (object):

	@staticmethod
	def operation (x, y, op):
		if op == 'not':
			return x is not y
		elif op == 'is':
			return x is y
		elif op == 'gt':
			return x > y
		elif op == 'ge':
			return x >= y
		elif op == 'eq':
			return x == y
		elif op == 'lt':
			return x < y
		elif op == 'le':
			return x <= y

	thresholdop = {'muxer': ('is',), 'videooutcaps': ('is',), 'audiooutcaps': ('is',), 'videowidth': ('is', 'lt'),
			'videoheight': ('is', 'lt'), 'length': ('is', 'le'), 'videoframerate': ('is', 'lt'),
			'videobitrate': ('not', 'lt'), 'audiobitrate': ('not', 'lt')}

	thresholdvalue = {'muxer': (None,), 'videooutcaps': (None,), 'audiooutcaps': (None,), 'videowidth': (None, 640),
			'videoheight': (None, 480), 'length': (None, 0), 'videoframerate': (None, 25),
			'videobitrate': (None, 3500000), 'audiobitrate': (None, 120000)}

	thresholdrela = {'muxer': None, 'videooutcaps': None, 'audiooutcaps': None, 'videowidth': False,
			'videoheight': False, 'length': False, 'videoframerate': True,
			'videobitrate': True, 'audiobitrate': True} # True for ALL, False for ANY (to get a FALSE return)

	encapsulation = {
			'video/mpeg': {'muxer': 'mpegtsmux', 'demuxer': 'ffdemux_mpeg', 'videoencoder': 'ffenc_mpeg2video', 'audioencoder': 'ffenc_mp2'},
			'video/x-mpeg': {'muxer': 'mpegtsmux', 'demuxer': 'ffdemux_mpeg', 'videoencoder': 'ffenc_mpeg2video', 'audioencoder': 'ffenc_mp2'},
			'video/mpegts': {'muxer': 'mpegtsmux', 'demuxer': 'ffdemux_mpeg', 'videoencoder': 'ffenc_mpeg2video', 'audioencoder': 'ffenc_mp2'},
			'video/x-ms-asf': {'muxer': 'asfmux', 'demuxer': 'asfdemux', 'videoencoder': 'ffenc_wmv2', 'audioencoder': 'ffenc_wmav2'},
			'video/x-msvideo': {'muxer': 'avimux', 'demuxer': 'avidemux', 'videoencoder': 'xvidenc', 'audioencoder': 'faac'},
			'video/quicktime': {'muxer': 'qtmux', 'demuxer': 'qtdemux', 'videoencoder': 'xvidenc', 'audioencoder': 'faac'},
			'default': {'muxer': 'mp4mux', 'demuxer': 'mp4demux', 'videoencoder': 'x264enc', 'audioencoder': 'faac'}}

	highestbitrate = {
			'ffenc_mpeg2video': 15000000,
			'ffenc_mp2': 384000,
			'ffenc_wmv2': 15000000,
			'ffenc_wmav2': 384000,
			'ffenc_mjpeg': 15000000,
			'xvidenc': 15000000,
			'x264enc': 15000,
			'faac': 320000}

	availbitrates = {}

	@staticmethod
	def validate (params):

		for key in MediaTypes.thresholdop.keys():

			if MediaTypes.thresholdrela[key]:
				if all ([
					MediaTypes.operation (params.get (key), MediaTypes.thresholdvalue[key][op], MediaTypes.thresholdop[key][op])
					for op in xrange (len (MediaTypes.thresholdop[key]))
					]):
					return False
			else:
				if any ([
					MediaTypes.operation (params.get (key), MediaTypes.thresholdvalue[key][op], MediaTypes.thresholdop[key][op])
					for op in xrange (len (MediaTypes.thresholdop[key]))
					]):
					return False

		return True

	@staticmethod
	def propertymap (discover):
		src = discover.__dict__
		dst = dict()

		if src.get ('videocaps'):
			dst['videooutcaps'] = src.get ('videocaps')[0]
		if src.get ('audiocaps'):
			dst['audiooutcaps'] = src.get ('audiocaps')[0]
		dst['videocodec'] = src.get ('videocodec')
		dst['audiocodec'] = src.get ('audiocodec')
		dst['videowidth'] = src.get ('videowidth')
		dst['videoheight'] = src.get ('videoheight')
		dst['length'] = src.get ('segmentlength')
		if not dst['length']:
			dst['length'] = max (src.get ('videolength'), src.get ('audiolength'))
		if src.get ('videorate'):
			dst['videoframerate'] = src.get ('videorate').__float__()
		dst['videobitrate'] = src.get ('videobitrate')
		dst['audiobitrate'] = src.get ('audiobitrate')

		dst['muxer'] = src.get ('muxer')
		encapsop = MediaTypes.encapsulation.get (src.get ('muxer'))
		if encapsop:
			encapsop.update ({'highestvideobitrate': MediaTypes.highestbitrate.get (encapsop.get ('videoencoder')),
				'highestaudiobitrate': MediaTypes.highestbitrate.get (encapsop.get ('audioencoder'))})
			dst.update (encapsop)

		return dst
