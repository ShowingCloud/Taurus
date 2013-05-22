#!/usr/bin/python


class MediaTypes (object):

	@staticmethod
	def operation (x, y, op):
		ret = False

		if op == 'not':
			ret = x is not y
		elif op == 'is':
			ret = x is y
		elif op == 'gt':
			ret = x > y
		elif op == 'ge':
			ret = x >= y
		elif op == 'eq':
			ret = x == y
		elif op == 'lt':
			ret = x < y
		elif op == 'le':
			ret = x <= y

		return ret

	@staticmethod
	def multioper (x, y, op):
		ret = []

		for i, _ in enumerate (op):
			ret.append (MediaTypes.operation (x, y[i], op[i]))

		return ret

	thresholds = (
			{'name': 'muxer',			'op': ('is',),			'value': (None,),			'relation': all},
			{'name': 'videooutcaps',	'op': ('is',),			'value': (None,),			'relation': all},
			{'name': 'audiooutcaps',	'op': ('is',),			'value': (None,),			'relation': all},
			{'name': 'videowidth',		'op': ('is', 'lt'),		'value': (None, 640),		'relation': any},
			{'name': 'videoheight',		'op': ('is', 'lt'),		'value': (None, 480),		'relation': any},
			{'name': 'length',			'op': ('is', 'le'),		'value': (None, 0),			'relation': any},
			{'name': 'videoframerate',	'op': ('is', 'lt'),		'value': (None, 25),		'relation': all},
			{'name': 'videobitrate',	'op': ('not', 'lt'),	'value': (None, 3500000),	'relation': all},
			{'name': 'audiobitrate',	'op': ('not', 'lt'),	'value': (None, 120000),	'relation': all}
			)

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

		for dic in MediaTypes.thresholds:
			if dic['relation'] (MediaTypes.multioper (params.get (dic['name']), dic['value'], dic['op'])):
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
