import gtk


__all__ = ('get_contrast_color',)


def get_contrast_color(color):
	"""Return a :class:`gdk.Color` to use as a readable text color for the
	given background color.

	http://stackoverflow.com/questions/1855884/determine-font-color-based-on-background-color
	"""
	if not isinstance(color, gtk.gdk.Color):
		color = gtk.gdk.Color(color)

	# Gdk uses some strange scale. What is fucked up about it is the terrible
	# fucking documentation. At this point, I'm quite sick of scouring the
	# web for information and samples of things, and finding nothing.
	max = 65535

	# Counting the perceptive luminance - human eye favors green color...
	a = 1 - ( 0.299 * color.red + 0.587 * color.green + 0.114 * color.blue)/max

	if a < 0.5:
		# bright colors - black font
		d = 0
	else:
		# dark colors - white font
		d = 255*max

	return gtk.gdk.Color(d, d, d)
