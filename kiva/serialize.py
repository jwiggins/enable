#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#------------------------------------------------------------------------------
""" A development backend for kiva that serializes all drawing to JSON. """

# These are the symbols that a backend has to define.
__all__ = ["CompiledPath", "Font", "font_metrics_provider", "GraphicsContext"]

import json
import numpy as np
from StringIO import StringIO
from uuid import uuid4 as rand_uid

# Local imports.
from fonttools import Font

KIVA_OPCODES = {
    # CompiledPath
    'begin_path' : 'bpth',
    'close_path' : 'cpth',
    'add_path' : 'apth',
    'arc' : 'arc-',
    'arc_to' : 'arct',
    'curve_to' : 'crvt',
    'quad_curve_to' : 'qcrv',
    'move_to' : 'mvto',
    'line_to' : 'lnto',
    'lines' : 'lnst',
    'rect' : 'rect',
    'rects' : 'rcts',
    # GraphicsContext
    
}

def _arc_extent(self, x, y, r, startAngle, endAngle, clockwise):
    """ Calculates the bounding box of an arc given the center (x, y),
        radius r, and angles startAngle, endAngle. Angles should be in the
        range [0, 2*pi].
    """
    axes = [0., np.pi*.5, np.pi, np.pi*1.5, np.pi*2.]
    bound_angles = [startAngle, endAngle]
    start_quad, end_quad = np.searchsorted(axes, (startAngle, endAngle))
    assert start_quad > 0 and start_quad < len(axes)
    assert end_quad > 0 and end_quad < len(axes)
    
    if start_quad != end_quad:
        increment = -1 if clockwise else 1
        quad = start_quad
        while quad != end_quad:
            axis_idx = quad-1 if clockwise else quad
            bound_angles.append(axes[axis_idx])
            quad += increment
            if quad <= 0:
                quad = 4
            elif quad > 4:
                quad = 1
    
    xs = [x+r*np.cos(t) for t in bound_angles] + [x,]
    ys = [y+r*np.sin(t) for t in bound_angles] + [y,]
    return [(min(xs), min(ys)), (max(xs), max(ys))]


class CompiledPath(object):
    def __init__(self, path=None):
        self.uid = rand_uid()
        self.dirty = True
        self.begin_path()

    ##############################
    # Serialization related bits

    def _add_op(self, op):
        json.dump(op, self.path)
        
        # Create a new UID if we've been flushed before
        if not self.dirty:
            self.uid = rand_uid()
        
        self.dirty = True
        self.empty = False

    def _flush(self):
        """ Flushes the path to the output file.
        """
        if self._needs_flush():
            # XXX: Implement
        self.dirty = False

    def _needs_flush(self):
        return self.dirty

    ##############################
    # CompiledPath interface

    def begin_path(self):
        """ Initialize to a pristine state """
        self.path = StringIO()
        self.empty = True
        self.start_point = self.current_point = (0.0, 0.0)
        self._extent = (0.0,0.0, 0.0,0.0)

    def close_path(self):
        if not self.empty and self.current_point != self.start_point:
            self.line_to(*self.start_point)

    def move_to(self, x, y):
        self.current_point = (x, y)
        self._expand_extent([(x,y),])
        
        op = dict(op=KIVA_OPCODES['move_to'], pnt=(x,y))
        self._add_op(op)

    def arc(self, x, y, r, startAngle, endAngle, clockwise=False):
        self.current_point = (x+r*cos(endAngle), y+r*sin(endAngle))
        extent = _arc_extent(x, y, r, startAngle, endAngle, clockwise)
        self._expand_extent(extent)

        op = dict(op=KIVA_OPCODES['arc'],
                  cntr=(x,y), rad=r, start=startAngle, end=endAngle,
                  clock=clockwise)
        self._add_op(op)

    def arc_to(self, x1, y1, x2, y2, r):
        # XXX: this calculation assumes that the radius fits inside the points
        x0, y0 = self.current_point
        xs = (min(x0,x1,x2), max(x0,x1,x2))
        ys = (min(y0,y1,y2), max(y0,y1,y2))
        self._expand_extent([(xs[0],ys[0]), (xs[1],ys[1])])
        self.current_point = (x2, y2)
        
        op = dict(op=KIVA_OPCODES['arc_to'],
                  p1=(x1,y1), p2=(x2,y2), rad=r)
        self._add_op(op)

    def curve_to(self, cx1, cy1, cx2, cy2, x, y):
        self.current_point = (x, y)
        self._expand_extent([(cx1,cy1), (cx2,cy2), (x,y)])
        
        op = dict(op=KIVA_OPCODES['curve_to'],
                  cp1=(c1x,c1y), cp2=(cx2,cy2), to=(x,y))
        self._add_op(op)

    def quad_curve_to(self, cx, cy, x, y):
        self.current_point = (x, y)
        self._expand_extent([(cx,cy), (x,y)])
        
        op = dict(op=KIVA_OPCODES['quad_curve_to'],
                  cp=(cx,cy), to=(x,y))
        self._add_op(op)

    def line_to(self, x, y):
        self.current_point = (x, y)
        self._expand_extent([(x,y),])
        
        op = dict(op=KIVA_OPCODES['line_to'],
                  to=(x,y))
        self._add_op(op)

    def lines(self, points):
        self.current_point = tuple(points[-1])
        self._expand_extent(points)
        
        op = dict(op=KIVA_OPCODES['lines'],
                  pnts=points)
        self._add_op(op)

    def add_path(self, other_path):
        ex,ey,ew,eh = other_path.get_bounding_box()
        self._expand_extent([(ex,ey), (ex+ew,ey+eh)])
        
        if not other_path._needs_flush():
            other_path._flush()
        
        op = dict(op=KIVA_OPCODES['add_path'],
                  pth=other_path.uid)
        self._add_op(op)

    def rect(self, x, y, sx, sy):
        self.current_point = (x, y)
        self._expand_extent([(x,y), (x+sx,y+sy)])
        
        op = dict(op=KIVA_OPCODES['rect'],
                  rect=(x,y,sx,sy))
        self._add_op(op)

    def rects(self, rects):
        # Calculate the extent of all the rects
        xs, ys, ws, hs = zip(*rects)
        ll = zip(xs, ys)
        ur = zip([x+w for x,w in zip(xs,ws)],
                 [y+h for y,h in zip(ys,hs)])
        self._expand_extent(ll+ur)

        op = dict(op=KIVA_OPCODES['rects'],
                  rects=rects)
        self._add_op(op)

    def is_empty(self):
        return self.empty

    def get_current_point(self):
        return self.current_point

    def get_bounding_box(self):
        return self._extent

    def _expand_extent(self, points):
        """ Expand the bounds of the extent if any points lay outside it.
        """
        x0,y0,x1,y1 = self._extent
        x1 += x0
        y1 += y0
        for px, py in points:
            x0 = min(px, x0)
            x1 = max(px, x1)
            y0 = min(py, y0)
            y1 = max(py, y1)
        # Reset the extent
        self._extent = (x0, y0, x1-x0, y1-y0)


class GraphicsContext(object):
    def __init__(self, size, *args, **kwargs):
        print "GraphicsContext.__init__()"
        self._width, self._height = size
        self.text_pos = (0.0, 0.0)
        self.text_transform = (1.0,0.0,0.0,1.0,0.0,0.0)

    #----------------------------------------------------------------
    # Size info
    #----------------------------------------------------------------

    def height(self):
        """ Returns the height of the context.
        """
        print "GraphicsContext.height()"
        return self._height

    def width(self):
        """ Returns the width of the context.
        """
        print "GraphicsContext.width()"
        return self._width

    #----------------------------------------------------------------
    # Coordinate Transform Matrix Manipulation
    #----------------------------------------------------------------

    def scale_ctm(self, sx, sy):
        """ Set the coordinate system scale to the given values, (sx,sy).

            sx:float -- The new scale factor for the x axis
            sy:float -- The new scale factor for the y axis
        """
        print "GraphicsContext.scale_ctm()"

    def translate_ctm(self, tx, ty):
        """ Translate the coordinate system by the given value by (tx,ty)

            tx:float --  The distance to move in the x direction
            ty:float --   The distance to move in the y direction
        """
        print "GraphicsContext.translate_ctm()"

    def rotate_ctm(self, angle):
        """ Rotates the coordinate space for drawing by the given angle.

            angle:float -- the angle, in radians, to rotate the coordinate
                           system
        """
        print "GraphicsContext.rotate_ctm()"

    def concat_ctm(self, transform):
        """ Concatenate the transform to current coordinate transform matrix.

            transform:affine_matrix -- the transform matrix to concatenate with
                                       the current coordinate matrix.
        """
        print "GraphicsContext.concat_ctm()"

    def get_ctm(self):
        """ Return the current coordinate transform matrix.
        """
        print "GraphicsContext.get_ctm()"
        return (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)

    #----------------------------------------------------------------
    # Save/Restore graphics state.
    #----------------------------------------------------------------

    def save_state(self):
        """ Save the current graphic's context state.

            This should always be paired with a restore_state
        """
        print "GraphicsContext.save_state()"

    def restore_state(self):
        """ Restore the previous graphics state.
        """
        print "GraphicsContext.restore_state()"

    #----------------------------------------------------------------
    # context manager interface
    #----------------------------------------------------------------

    def __enter__(self):
        self.save_state()

    def __exit__(self, type, value, traceback):
        self.restore_state()

    #----------------------------------------------------------------
    # Manipulate graphics state attributes.
    #----------------------------------------------------------------

    def set_antialias(self,value):
        """ Set/Unset antialiasing
        """
        print "GraphicsContext.set_antialias()"

    def set_line_width(self,width):
        """ Set the line width for drawing

            width:float -- The new width for lines in user space units.
        """
        print "GraphicsContext.set_line_width()"

    def set_line_join(self,style):
        """ Set style for joining lines in a drawing.

            style:join_style -- The line joining style.  The available
                                styles are JOIN_ROUND, JOIN_BEVEL, JOIN_MITER.
        """
        print "GraphicsContext.set_line_join()"

    def set_miter_limit(self,limit):
        """ Specifies limits on line lengths for mitering line joins.

            If line_join is set to miter joins, the limit specifies which
            line joins should actually be mitered.  If lines aren't mitered,
            they are joined with a bevel.  The line width is divided by
            the length of the miter.  If the result is greater than the
            limit, the bevel style is used.

            limit:float -- limit for mitering joins.
        """
        print "GraphicsContext.set_miter_limit()"

    def set_line_cap(self,style):
        """ Specify the style of endings to put on line ends.

            style:cap_style -- the line cap style to use. Available styles
                               are CAP_ROUND,CAP_BUTT,CAP_SQUARE
        """
        print "GraphicsContext.set_line_cap()"

    def set_line_dash(self,lengths,phase=0):
        """

            lengths:float array -- An array of floating point values
                                   specifing the lengths of on/off painting
                                   pattern for lines.
            phase:float -- Specifies how many units into dash pattern
                           to start.  phase defaults to 0.
        """
        print "GraphicsContext.set_line_dash()"

    def set_flatness(self,flatness):
        """ Not implemented

            It is device dependent and therefore not recommended by
            the PDF documentation.
        """
        print "GraphicsContext.set_flatness()"
        raise NotImplementedError

    #----------------------------------------------------------------
    # Sending drawing data to a device
    #----------------------------------------------------------------

    def flush(self):
        """ Send all drawing data to the destination device.
        """
        print "GraphicsContext.flush()"

    def synchronize(self):
        """ Prepares drawing data to be updated on a destination device.
        """
        print "GraphicsContext.synchronize()"

    #----------------------------------------------------------------
    # Page Definitions
    #----------------------------------------------------------------

    def begin_page(self):
        """ Create a new page within the graphics context.
        """
        print "GraphicsContext.begin_page()"

    def end_page(self):
        """ End drawing in the current page of the graphics context.
        """
        print "GraphicsContext.end_page()"

    #----------------------------------------------------------------
    # Building paths
    #----------------------------------------------------------------

    def begin_path(self):
        """ Clear the current drawing path and begin a new one.
        """
        print "GraphicsContext.begin_path()"
        self.path = CompiledPath()

    def move_to(self,x,y):
        """ Start a new drawing subpath at place the current point at (x,y).
        """
        print "GraphicsContext.move_to()"
        self.path.move_to(x,y)

    def line_to(self,x,y):
        """ Add a line from the current point to the given point (x,y).

            The current point is moved to (x,y).
        """
        print "GraphicsContext.line_to()"
        self.path.line_to(x,y)

    def lines(self,points):
        """ Add a series of lines as a new subpath.

            Currently implemented by calling line_to a zillion times.

            Points is an Nx2 array of x,y pairs.
        """
        print "GraphicsContext.lines()"
        self.path.lines(points)

    def line_set(self, starts, ends):
        """ Draw multiple disjoint line segments.
        """
        print "GraphicsContext.line_set()"
        for start, end in izip(starts, ends):
            self.path.path.moveTo(start[0], start[1])
            self.path.path.lineTo(end[0], end[1])

    def rect(self,x,y,sx,sy):
        """ Add a rectangle as a new subpath.
        """
        print "GraphicsContext.rect()"
        self.path.rect(x,y,sx,sy)

    def rects(self,rects):
        """ Add multiple rectangles as separate subpaths to the path.
        """
        print "GraphicsContext.rects()"
        self.path.rects(rects)

    def draw_rect(self, rect, mode=constants.FILL_STROKE):
        """ Draw a rect.
        """
        print "GraphicsContext.draw_rect()"

    def add_path(self, path):
        """ Add a subpath to the current path.
        """
        print "GraphicsContext.add_path()"
        self.path.add_path(path)

    def close_path(self):
        """ Close the path of the current subpath.
        """
        print "GraphicsContext.close_path()"
        self.path.close_path()

    def curve_to(self, cp1x, cp1y, cp2x, cp2y, x, y):
        """
        """
        print "GraphicsContext.curve_to()"
        self.path.curve_to(cp1x, cp1y, cp2x, cp2y, x, y)

    def quad_curve_to(self, cpx, cpy, x, y):
        """
        """
        print "GraphicsContext.quad_curve_to()"
        self.path.quad_curve_to(cpx, cpy, x, y)

    def arc(self, x, y, radius, start_angle, end_angle, clockwise=False):
        """
        """
        print "GraphicsContext.arc()"
        self.path.arc(x, y, radius, start_angle, end_angle, clockwise)

    def arc_to(self, x1, y1, x2, y2, radius):
        """
        """
        print "GraphicsContext.arc_to()"
        self.path.arc_to(x1, y1, x2, y2, radius)

    #----------------------------------------------------------------
    # Getting infomration on paths
    #----------------------------------------------------------------

    def is_path_empty(self):
        """ Test to see if the current drawing path is empty
        """
        print "GraphicsContext.is_path_empty()"
        return self.path.is_empty()

    def get_path_current_point(self):
        """ Return the current point from the graphics context.
        """
        print "GraphicsContext.get_path_current_point()"
        return self.path.get_current_point()

    def get_path_bounding_box(self):
        """ Return the bounding box for the current path object.
        """
        print "GraphicsContext.get_path_bounding_box()"
        return self.path.get_bounding_box()

    #----------------------------------------------------------------
    # Clipping path manipulation
    #----------------------------------------------------------------

    def clip(self):
        """
        """
        print "GraphicsContext.clip()"

    def even_odd_clip(self):
        """
        """
        print "GraphicsContext.even_odd_clip()"

    def clip_to_rect(self, x, y, w, h):
        """ Clip context to the given rectangular region.

            Region should be a 4-tuple or a sequence.
        """
        print "GraphicsContext.clip_to_rect()"

    def clip_to_rects(self, rects):
        """
        """
        print "GraphicsContext.clip_to_rects()"

    #----------------------------------------------------------------
    # Color space manipulation
    #
    # I'm not sure we'll mess with these at all.  They seem to
    # be for setting the color system.  Hard coding to RGB or
    # RGBA for now sounds like a reasonable solution.
    #----------------------------------------------------------------

    def set_fill_color_space(self):
        """
        """
        msg = "set_fill_color_space not implemented yet."
        raise NotImplementedError, msg

    def set_stroke_color_space(self):
        """
        """
        msg = "set_stroke_color_space not implemented yet."
        raise NotImplementedError, msg

    def set_rendering_intent(self):
        """
        """
        msg = "set_rendering_intent not implemented yet."
        raise NotImplementedError, msg

    #----------------------------------------------------------------
    # Color manipulation
    #----------------------------------------------------------------

    def set_fill_color(self, color):
        """
        """
        print "GraphicsContext.set_fill_color()"

    def set_stroke_color(self, color):
        """
        """
        print "GraphicsContext.set_stroke_color()"

    def set_alpha(self, alpha):
        """
        """
        print "GraphicsContext.set_alpha()"

    #----------------------------------------------------------------
    # Gradients
    #----------------------------------------------------------------

    def linear_gradient(self, x1, y1, x2, y2, stops, spread_method,
                        units='userSpaceOnUse'):
        """ Sets a linear gradient as the current brush.
        """
        print "GraphicsContext.linear_gradient()"

    def radial_gradient(self, cx, cy, r, fx, fy, stops, spread_method,
                        units='userSpaceOnUse'):
        """ Sets a radial gradient as the current brush.
        """
        print "GraphicsContext.radial_gradient()"

    #----------------------------------------------------------------
    # Drawing Images
    #----------------------------------------------------------------

    def draw_image(self, img, rect=None):
        """
        img is either a N*M*3 or N*M*4 numpy array, or a Kiva image

        rect - a tuple (x,y,w,h)
        """
        print "GraphicsContext.draw_image()"

    #----------------------------------------------------------------
    # Drawing Text
    #----------------------------------------------------------------

    def select_font(self, name, size, textEncoding):
        """ Set the font for the current graphics context.
        """
        print "GraphicsContext.select_font()"

    def set_font(self, font):
        """ Set the font for the current graphics context.
        """
        print "GraphicsContext.set_font()"

    def set_font_size(self, size):
        """
        """
        print "GraphicsContext.set_font_size()"

    def set_character_spacing(self, spacing):
        """
        """
        print "GraphicsContext.set_character_spacing()"

    def set_text_drawing_mode(self):
        """
        """
        print "GraphicsContext.set_text_drawing_mode()"

    def set_text_position(self,x,y):
        """
        """
        print "GraphicsContext.set_text_position()"
        self.text_pos = (x,y)

    def get_text_position(self):
        """
        """
        print "GraphicsContext.get_text_position()"
        return self.text_pos

    def set_text_matrix(self,ttm):
        """
        """
        print "GraphicsContext.set_text_matrix()"
        self.text_transform = ttm

    def get_text_matrix(self):
        """
        """
        print "GraphicsContext.get_text_matrix()"
        return self.text_transform

    def show_text(self, text, point=None):
        """ Draw text on the device at current text position.

            This is also used for showing text at a particular point
            specified by x and y.
        """
        print "GraphicsContext.show_text()"

    def show_text_at_point(self, text, x, y):
        """ Draw text at some point (x,y).
        """
        print "GraphicsContext.show_text_at_point()"

    def show_glyphs(self):
        """
        """
        raise NotImplementedError

    def get_text_extent(self, text):
        """ Returns the bounding rect of the rendered text
        """
        print "GraphicsContext.get_text_extent()"
        return 0.0, 0.0, 1.0, 1.0

    def get_full_text_extent(self, text):
        """ Backwards compatibility API over .get_text_extent() for Enable
        """
        print "GraphicsContext.get_full_text_extent()"
        x1, y1, x2, y2 = self.get_text_extent(text)
        return x2, y2, y1, x1

    #----------------------------------------------------------------
    # Painting paths (drawing and filling contours)
    #----------------------------------------------------------------

    def stroke_path(self):
        """
        """
        print "GraphicsContext.stroke_path()"
        self.begin_path()

    def fill_path(self):
        """
        """
        print "GraphicsContext.fill_path()"
        self.begin_path()

    def eof_fill_path(self):
        """
        """
        print "GraphicsContext.eof_fill_path()"
        self.begin_path()

    def stroke_rect(self,rect):
        """
        """
        print "GraphicsContext.stroke_rect()"

    def stroke_rect_with_width(self,rect,width):
        """
        """
        print "GraphicsContext.stroke_rect_with_width()"

    def fill_rect(self,rect):
        """
        """
        print "GraphicsContext.fill_rect()"

    def fill_rects(self):
        """
        """
        raise NotImplementedError

    def clear_rect(self, rect):
        """
        """
        print "GraphicsContext.clear_rect()"

    def clear(self, clear_color=(1.0,1.0,1.0,1.0)):
        """
        """
        print "GraphicsContext.clear()"

    def draw_path(self, mode):
        """ Walk through all the drawing subpaths and draw each element.

            Each subpath is drawn separately.
        """
        print "GraphicsContext.draw_path()"
        self.begin_path()

    def get_empty_path(self):
        """ Return a path object that can be built up and then reused.
        """
        print "GraphicsContext.get_empty_path()"
        return CompiledPath()

    def draw_path_at_points(self, points, path, mode):
        print "GraphicsContext.draw_path_at_points()"

    def save(self, filename, file_format=None):
        """ Save the contents of the context to a file
        """
        print "GraphicsContext.save()"

def font_metrics_provider():
    return GraphicsContext()

