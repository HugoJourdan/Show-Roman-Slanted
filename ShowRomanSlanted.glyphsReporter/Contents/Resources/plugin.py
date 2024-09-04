# encoding: utf-8

###########################################################################################################
#
#
# Reporter Plugin
#
# Read the docs:
# https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Reporter
#
#
###########################################################################################################


from __future__ import division, print_function, unicode_literals
import objc
from GlyphsApp import Glyphs, GSAnchor
from GlyphsApp.plugins import ReporterPlugin
from AppKit import NSColor, NSPoint, NSBezierPath
import math



class ShowRomanSlanted(ReporterPlugin):

	@objc.python_method
	def settings(self):
		self.menuName = "Roman Slanted"

	@objc.python_method
	def background(self, layer):

		
				
		Font = Glyphs.font
		scale = Glyphs.font.currentTab.scale
		selected_master = Font.selectedFontMaster

		

		if selected_master.italicAngle and layer.bezierPath :

			roman_master = self.find_corresponding_roman_italic(layer).master
			roman_layer = layer.parent.layers[roman_master.id].copyDecomposedLayer()

			layer_compareStringNoAnchors = layer.compareString().rsplit('_', 1)[0]
			roman_layer_compareStringNoAnchors = roman_layer.compareString().rsplit('_', 1)[0]


			if layer_compareStringNoAnchors == roman_layer_compareStringNoAnchors :

				roman_layer = layer.parent.layers[0].copyDecomposedLayer()

				layer_compareStringNoAnchors = layer.compareString().rsplit('_', 1)[0]
				roman_layer_compareStringNoAnchors = roman_layer.compareString().rsplit('_', 1)[0]

				roman_layer = layer.parent.layers[0].copyDecomposedLayer()
				roman_layer.parent = layer.parent.layers[0].parent
				self.slant_layer(roman_layer , layer.italicAngle)


				layer.font().disableUndo()
				roman_layer.LSB = layer.bounds.origin.x + (layer.bounds.size.width - roman_layer.bounds.size.width)/2
				layer.font().enableUndo()
				
				bp = roman_layer.bezierPath
    
				NSColor.blueColor().colorWithAlphaComponent_(0.1).set()
				bp.fill()
    
				bp.setLineWidth_(1/scale)
				NSColor.blueColor().colorWithAlphaComponent_(0.3).set()
				bp.stroke()



	def find_corresponding_roman_italic(self, layer):
		font_axes_tags = [axe.axisTag for axe in layer.font().axes]
		italic_tag = next((tag for tag in ["slnt", "ital"] if tag in font_axes_tags), None)

		# Check if italic_tag was found before trying to get the index
		if italic_tag is not None:
			italic_axis_i = font_axes_tags.index(italic_tag)

		layer_master = layer.master

		# Convert layer master's internal axis values to a list and remove the italic axis
		layer_master_internal = list(layer_master.internalAxesValues)
		layer_master_internal.pop(italic_axis_i)

		# Iterate over all masters in the font, skipping the layer's master
		for m in layer.font().masters:
			if m == layer_master:
				continue

			# Convert master's internal axis values to a list and remove the italic axis
			m_internal = list(m.internalAxesValues)
			m_internal.pop(italic_axis_i)

			# Compare the remaining axes values
			if m_internal == layer_master_internal:
				return layer.parent.layers[m.id]

		return None

	#@objc.python_method
	def italic_skew(self, x, y, angle):
		"""Skews x/y along the x axis and returns skewed x value."""
		new_angle = ( angle / 180.0 ) * math.pi
		return x + y * math.tan( new_angle )

	#@objc.python_method
	def slant_layer(self, layer, italicAngle):
		layer.font().disableUndo()

		skewAngle = italicAngle
		skewRadians = round(math.radians(skewAngle),2)
		thisMasterXHeight = layer.master.xHeight
		italicCorrection = self.italic_skew( 0.0, thisMasterXHeight/2.0, skewAngle )
		
		layer.applyTransform([
								1, # x scale factor
								0, # x skew factor
								skewRadians, # y skew factor
								1, # y scale factor
								-italicCorrection, # x position
								0  # y position
								])
		layer.font().enableUndo()



	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
