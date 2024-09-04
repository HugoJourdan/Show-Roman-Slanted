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
from GlyphsApp import Glyphs
from GlyphsApp.plugins import ReporterPlugin
from AppKit import NSColor, NSPoint, NSAffineTransform, NSColor, NSPoint,NSMinX, NSMaxX, NSMinY, NSMaxY
import math



class ShowRomanSlanted(ReporterPlugin):

	@objc.python_method
	def settings(self):
		self.menuName = "Roman Slanted"

	@objc.python_method
	def background(self, layer):

		
				
		Font = Glyphs.font
		selected_master = Font.selectedFontMaster
		scale = Glyphs.font.currentTab.scale

		if selected_master.italicAngle and layer.bezierPath :

			roman_master = self.find_corresponding_roman_italic(layer).master
			roman_layer = layer.parent.layers[roman_master.id].copyDecomposedLayer()
			roman_layer.parent = layer.parent

			layer_compareStringNoAnchors = layer.compareString().rsplit('_', 1)[0]
			roman_layer_compareStringNoAnchors = roman_layer.compareString().rsplit('_', 1)[0]


			if layer_compareStringNoAnchors == roman_layer_compareStringNoAnchors :


				roman_layer.associatedMasterId = layer.associatedMasterId
				self.slant_layer(roman_layer , layer.italicAngle)

				layer.font().disableUndo()

				roman_layer.LSB = layer.LSB

				layer_true_bound = self.getTrueBoundingxBox(layer, layer.bounds)
				roman_true_bound = self.getTrueBoundingxBox(roman_layer, roman_layer.bounds)
				
				roman_width = roman_true_bound[2].x - roman_true_bound[0].x
				layer_width = layer_true_bound[2].x - layer_true_bound[0].x

				roman_layer.LSB -= roman_true_bound[0].x - layer_true_bound[0].x + (roman_width - layer_width) /2

				layer.font().enableUndo()

				bp = roman_layer.bezierPath
			
				NSColor.blueColor().colorWithAlphaComponent_(0.1).set()
				bp.fill()

				bp.setLineWidth_(1/scale)
				NSColor.blueColor().colorWithAlphaComponent_(0.3).set()
				bp.stroke()


	@objc.python_method
	def italicize(self, thisPoint, italicAngle=0.0, pivotalY=0.0):
		"""
		Returns the italicized position of an NSPoint 'thisPoint'
		for a given angle 'italicAngle' and the pivotal height 'pivotalY',
		around which the italic slanting is executed, usually half x-height.
		Usage: myPoint = italicize(myPoint,10,xHeight*0.5)
		"""
		x = thisPoint.x
		yOffset = thisPoint.y - pivotalY  # calculate vertical offset
		italicAngle = math.radians(italicAngle)  # convert to radians
		tangens = math.tan(italicAngle)  # math.tan needs radians
		horizontalDeviance = tangens * yOffset  # vertical distance from pivotal point
		x += horizontalDeviance  # x of point that is yOffset from pivotal point
		return NSPoint(int(x), int(thisPoint.y))

	@objc.python_method
	def getTrueBoundingxBox(self, layer, bounds):

		angle = layer.italicAngle

		if angle == 0:
			# If no italic angle, return the bounding box corners as they are
			bottom_left = bounds.origin
			top_left = NSPoint(NSMinX(bounds), NSMaxY(bounds))
			top_right = NSPoint(NSMaxX(bounds), NSMaxY(bounds))
			bottom_right = NSPoint(NSMaxX(bounds), NSMinY(bounds))
			return (bottom_left, top_left, top_right, bottom_right)

		slantHeight = layer.slantHeight()

		# Create a copy of the layer to apply transformations
		layer.font().disableUndo()
		layer_copy = layer.copy()
		layer_copy.parent = layer.parent

		# Apply the skew transformation based on the italic angle
		transform = NSAffineTransform.new()
		transform.skew(math.tan(math.radians(-angle)), (0, slantHeight))
		layer_copy.applyTransform(transform)
		layer.font().enableUndo()

		# Calculate the new bounding box corners
		def get_new_point(x, y):
			pos = NSPoint(x, y)
			return self.italicize(pos, angle, slantHeight)

		bounds = layer_copy.bounds
		bottom_left = get_new_point(NSMinX(bounds), NSMinY(bounds))
		top_left = get_new_point(NSMinX(bounds), NSMaxY(bounds))
		top_right = get_new_point(NSMaxX(bounds), NSMaxY(bounds))
		bottom_right = get_new_point(NSMaxX(bounds), NSMinY(bounds))

		return (bottom_left, top_left, top_right, bottom_right)



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

	@objc.python_method
	def italicSkew(self, x, y, angle=10.0 ):
		"""Skews x/y along the x axis and returns skewed x value."""
		new_angle = ( angle / 180.0 ) * math.pi
		return x + y * math.tan( new_angle )


	#@objc.python_method
	def slant_layer(self, layer, degree):
		layer.font().disableUndo()

		skewAngle = degree
		skewRadians = round(math.radians(skewAngle),2)
		thisMasterXHeight = layer.master.xHeight
		italicCorrection = self.italicSkew( 0.0, thisMasterXHeight/2.0, skewAngle )
		
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
