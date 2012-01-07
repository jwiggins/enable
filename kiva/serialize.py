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
    'lines' : 'lns-',
    'rect' : 'rect',
    'rects' : 'rcts',

    # GraphicsContext
    'scale_ctm' : 'smtx',
    'translate_ctm' : 'tmtx',
    'rotate_ctm' : 'rmtx',
    'concat_ctm' : 'cmtx',
    'save_state' : 'push',
    'restore_state' : 'pop-',
    'set_antialias' : 'staa',
    'set_line_width' : 'stlw',
    'set_line_join' : 'stlj',
    'set_miter_limit' : 'stml',
    'set_line_cap' : 'stlc',
    'set_line_dash' : 'stld',
    'set_flatness' : 'stfl',
    'flush' : 'flsh',
    'synchronize' : 'sync',
    'begin_page' : 'bpge',
    'end_page' : 'epge',
    'line_set' : 'lnst',
    'draw_rect' : 'drwr',
    'stroke_rect' : 'stkr',
    'stroke_rect_with_width' : 'srww',
    'fill_rect' : 'frct',
    'fill_rects' : 'frts',
    'clip' : 'clip',
    'even_odd_clip' : 'eocl',
    'clip_to_rect' : 'clrt',
    'clip_to_rects' : 'clrs',
    'stroke_path' : 'spth',
    'fill_path' : 'fpth',
    'eof_fill_path' : 'efpt',
    'draw_path' : 'drpt',
    'draw_path_at_points' : 'dpap',
    'draw_image' : 'dimg',
    'clear_rect' : 'clrr',
    'clear' : 'clr-',
    'set_fill_color_space' : 'sfcs',
    'set_stroke_color_space' : 'sscs',
    'set_rendering_intent' : 'srin',
    'set_fill_color' : 'sfcr',
    'set_stroke_color' : 'sscr',
    'set_alpha' : 'salp',
    'linear_gradient' : 'ling',
    'radial_gradient' : 'radg',
    'select_font' : 'slft',
    'set_font' : 'stft',
    'set_font_size' : 'sfsz',
    'set_character_spacing' : 'schs',
    'set_text_drawing_mode' : 'stdm',
    'set_text_position' : 'stps',
    'set_text_matrix' : 'stmt',
    'show_text' : 'shtx',
    'show_text_at_point' : 'stap',
    'show_glyphs' : 'shgl',
}
# Make sure the opcodes are unique
assert len(KIVA_OPCODES.values()) == len(set(KIVA_OPCODES.values()))

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
        # XXX: Additionally, the arc will rarely intersect p1.
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
        self.transform = (1.0,0.0,0.0,1.0,0.0,0.0)
        self.text_pos = (0.0, 0.0)
        self.text_transform = (1.0,0.0,0.0,1.0,0.0,0.0)
        self.uid = rand_uid()
        self.backing_store = StringIO()

    def _add_op(self, op):
        json.dump(op, self.backing_store)

    #----------------------------------------------------------------
    # Size info
    #----------------------------------------------------------------

    def height(self):
        """ Returns the height of the context.
        """
        return self._height

    def width(self):
        """ Returns the width of the context.
        """
        return self._width

    #----------------------------------------------------------------
    # Coordinate Transform Matrix Manipulation
    #----------------------------------------------------------------

    def scale_ctm(self, sx, sy):
        """ Set the coordinate system scale to the given values, (sx,sy).

            sx:float -- The new scale factor for the x axis
            sy:float -- The new scale factor for the y axis
        """
        self.transform
        
        op = dict(op=KIVA_OPCODES['scale_ctm'], scale=(sx,sy))
        self._add_op(op)

    def translate_ctm(self, tx, ty):
        """ Translate the coordinate system by the given value by (tx,ty)

            tx:float --  The distance to move in the x direction
            ty:float --   The distance to move in the y direction
        """
        self.transform
        
        op = dict(op=KIVA_OPCODES['translate_ctm'], offset=(tx,ty))
        self._add_op(op)

    def rotate_ctm(self, angle):
        """ Rotates the coordinate space for drawing by the given angle.

            angle:float -- the angle, in radians, to rotate the coordinate
                           system
        """
        self.transform
        
        op = dict(op=KIVA_OPCODES['rotate_ctm'], angle=angle)
        self._add_op(op)

    def concat_ctm(self, transform):
        """ Concatenate the transform to current coordinate transform matrix.

            transform:affine_matrix -- the transform matrix to concatenate with
                                       the current coordinate matrix.
        """
        self.transform
        
        op = dict(op=KIVA_OPCODES['concat_ctm'], transform=transform)
        self._add_op(op)

    def get_ctm(self):
        """ Return the current coordinate transform matrix.
        """
        return self.transform

    #----------------------------------------------------------------
    # Save/Restore graphics state.
    #----------------------------------------------------------------

    def save_state(self):
        """ Save the current graphic's context state.

            This should always be paired with a restore_state
        """
        # XXX: actually push the current state onto a stack
        op = dict(op=KIVA_OPCODES['save_state'])
        self._add_op(op)

    def restore_state(self):
        """ Restore the previous graphics state.
        """
        # XXX: actually pop the current state off the stack
        op = dict(op=KIVA_OPCODES['restore_state'])
        self._add_op(op)

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
        op = dict(op=KIVA_OPCODES['set_antialias'], value=value)
        self._add_op(op)

    def set_line_width(self,width):
        """ Set the line width for drawing

            width:float -- The new width for lines in user space units.
        """
        op = dict(op=KIVA_OPCODES['set_line_width'], width=width)
        self._add_op(op)

    def set_line_join(self,style):
        """ Set style for joining lines in a drawing.

            style:join_style -- The line joining style.  The available
                                styles are JOIN_ROUND, JOIN_BEVEL, JOIN_MITER.
        """
        op = dict(op=KIVA_OPCODES['set_line_join'], style=style)
        self._add_op(op)

    def set_miter_limit(self,limit):
        """ Specifies limits on line lengths for mitering line joins.

            If line_join is set to miter joins, the limit specifies which
            line joins should actually be mitered.  If lines aren't mitered,
            they are joined with a bevel.  The line width is divided by
            the length of the miter.  If the result is greater than the
            limit, the bevel style is used.

            limit:float -- limit for mitering joins.
        """
        op = dict(op=KIVA_OPCODES['set_miter_limit'], limit=limit)
        self._add_op(op)

    def set_line_cap(self,style):
        """ Specify the style of endings to put on line ends.

            style:cap_style -- the line cap style to use. Available styles
                               are CAP_ROUND,CAP_BUTT,CAP_SQUARE
        """
        op = dict(op=KIVA_OPCODES['set_line_cap'], style=style)
        self._add_op(op)

    def set_line_dash(self,lengths,phase=0):
        """

            lengths:float array -- An array of floating point values
                                   specifing the lengths of on/off painting
                                   pattern for lines.
            phase:float -- Specifies how many units into dash pattern
                           to start.  phase defaults to 0.
        """
        op = dict(op=KIVA_OPCODES['set_line_dash'],
                  lengths=lengths, phase=phase)
        self._add_op(op)

    def set_flatness(self,flatness):
        """ Not implemented

            It is device dependent and therefore not recommended by
            the PDF documentation.
        """
        op = dict(op=KIVA_OPCODES['set_flatness'], flatness=flatness)
        self._add_op(op)

    #----------------------------------------------------------------
    # Sending drawing data to a device
    #----------------------------------------------------------------

    def flush(self):
        """ Send all drawing data to the destination device.
        """
        op = dict(op=KIVA_OPCODES['flush'])
        self._add_op(op)

    def synchronize(self):
        """ Prepares drawing data to be updated on a destination device.
        """
        op = dict(op=KIVA_OPCODES['synchronize'])
        self._add_op(op)

    #----------------------------------------------------------------
    # Page Definitions
    #----------------------------------------------------------------

    def begin_page(self):
        """ Create a new page within the graphics context.
        """
        op = dict(op=KIVA_OPCODES['begin_page'])
        self._add_op(op)

    def end_page(self):
        """ End drawing in the current page of the graphics context.
        """
        op = dict(op=KIVA_OPCODES['end_page'])
        self._add_op(op)

    #----------------------------------------------------------------
    # Building paths
    #----------------------------------------------------------------

    def begin_path(self):
        """ Clear the current drawing path and begin a new one.
        """
        self.path = CompiledPath()

    def move_to(self,x,y):
        """ Start a new drawing subpath at place the current point at (x,y).
        """
        self.path.move_to(x,y)

    def line_to(self,x,y):
        """ Add a line from the current point to the given point (x,y).

            The current point is moved to (x,y).
        """
        self.path.line_to(x,y)

    def lines(self,points):
        """ Add a series of lines as a new subpath.

            Currently implemented by calling line_to a zillion times.

            Points is an Nx2 array of x,y pairs.
        """
        self.path.lines(points)

    def line_set(self, starts, ends):
        """ Draw multiple disjoint line segments.
        """
        for start, end in izip(starts, ends):
            self.path.path.moveTo(start[0], start[1])
            self.path.path.lineTo(end[0], end[1])

    def rect(self,x,y,sx,sy):
        """ Add a rectangle as a new subpath.
        """
        self.path.rect(x,y,sx,sy)

    def rects(self,rects):
        """ Add multiple rectangles as separate subpaths to the path.
        """
        self.path.rects(rects)

    def draw_rect(self, rect, mode=constants.FILL_STROKE):
        """ Draw a rect.
        """
        op = dict(op=KIVA_OPCODES['draw_rect'], rect=rect, mode=mode)
        self._add_op(op)

    def add_path(self, path):
        """ Add a subpath to the current path.
        """
        self.path.add_path(path)

    def close_path(self):
        """ Close the path of the current subpath.
        """
        self.path.close_path()

    def curve_to(self, cp1x, cp1y, cp2x, cp2y, x, y):
        """
        """
        self.path.curve_to(cp1x, cp1y, cp2x, cp2y, x, y)

    def quad_curve_to(self, cpx, cpy, x, y):
        """
        """
        self.path.quad_curve_to(cpx, cpy, x, y)

    def arc(self, x, y, radius, start_angle, end_angle, clockwise=False):
        """
        """
        self.path.arc(x, y, radius, start_angle, end_angle, clockwise)

    def arc_to(self, x1, y1, x2, y2, radius):
        """
        """
        self.path.arc_to(x1, y1, x2, y2, radius)

    #----------------------------------------------------------------
    # Getting infomration on paths
    #----------------------------------------------------------------

    def is_path_empty(self):
        """ Test to see if the current drawing path is empty
        """
        return self.path.is_empty()

    def get_path_current_point(self):
        """ Return the current point from the graphics context.
        """
        return self.path.get_current_point()

    def get_path_bounding_box(self):
        """ Return the bounding box for the current path object.
        """
        return self.path.get_bounding_box()

    #----------------------------------------------------------------
    # Clipping path manipulation
    #----------------------------------------------------------------

    def clip(self):
        """
        """
        op = dict(op=KIVA_OPCODES['clip'])
        self._add_op(op)

    def even_odd_clip(self):
        """
        """
        op = dict(op=KIVA_OPCODES['even_odd_clip'])
        self._add_op(op)

    def clip_to_rect(self, x, y, w, h):
        """ Clip context to the given rectangular region.

            Region should be a 4-tuple or a sequence.
        """
        op = dict(op=KIVA_OPCODES['clip_to_rect'], rect=(x,y,w,h))
        self._add_op(op)

    def clip_to_rects(self, rects):
        """
        """
        op = dict(op=KIVA_OPCODES['clip_to_rects'], rects=rects)
        self._add_op(op)

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
        raise NotImplementedError

    def set_stroke_color_space(self):
        """
        """
        raise NotImplementedError

    def set_rendering_intent(self):
        """
        """
        raise NotImplementedError

    #----------------------------------------------------------------
    # Color manipulation
    #----------------------------------------------------------------

    def set_fill_color(self, color):
        """
        """
        op = dict(op=KIVA_OPCODES['set_fill_color'], color=color)
        self._add_op(op)

    def set_stroke_color(self, color):
        """
        """
        op = dict(op=KIVA_OPCODES['set_stroke_color'], color=color)
        self._add_op(op)

    def set_alpha(self, alpha):
        """
        """
        op = dict(op=KIVA_OPCODES['set_alpha'], alpha=alpha)
        self._add_op(op)

    #----------------------------------------------------------------
    # Gradients
    #----------------------------------------------------------------

    def linear_gradient(self, x1, y1, x2, y2, stops, spread_method,
                        units='userSpaceOnUse'):
        """ Sets a linear gradient as the current brush.
        """
        op = dict(op=KIVA_OPCODES['linear_gradient'],
                  start=(x1,y1), end=(x2,y2), stops=stops,
                  spread=spread_method, units=units)
        self._add_op(op)

    def radial_gradient(self, cx, cy, r, fx, fy, stops, spread_method,
                        units='userSpaceOnUse'):
        """ Sets a radial gradient as the current brush.
        """
        op = dict(op=KIVA_OPCODES['radial_gradient'],
                  center=(cx,cy), focus=(fx,fy), radius=r,
                  stops=stops, spread=spread_method, units=units)
        self._add_op(op)

    #----------------------------------------------------------------
    # Drawing Images
    #----------------------------------------------------------------

    def draw_image(self, img, rect=None):
        """
        img is either a N*M*3 or N*M*4 numpy array, or a Kiva image

        rect - a tuple (x,y,w,h)
        """
        # XXX: Make sure the client has the image before drawing it
        op = dict(op=KIVA_OPCODES['draw_image'], img=img)
        if rect:
            op['rect'] = rect
        self._add_op(op)

    #----------------------------------------------------------------
    # Drawing Text
    #----------------------------------------------------------------

    def select_font(self, name, size, textEncoding):
        """ Set the font for the current graphics context.
        """
        op = dict(op=KIVA_OPCODES['select_font'], face=name, size=size,
                  textEncoding=textEncoding)
        self._add_op(op)

    def set_font(self, font):
        """ Set the font for the current graphics context.
        """
        # XXX: Handle passing font objects to the client
        op = dict(op=KIVA_OPCODES['set_font'], font=font)
        self._add_op(op)

    def set_font_size(self, size):
        """
        """
        op = dict(op=KIVA_OPCODES['set_font_size'], size=size)
        self._add_op(op)

    def set_character_spacing(self, spacing):
        """
        """
        op = dict(op=KIVA_OPCODES['set_character_spacing'], spacing=spacing)
        self._add_op(op)

    def set_text_drawing_mode(self):
        """
        """
        op = dict(op=KIVA_OPCODES['set_text_drawing_mode'])
        self._add_op(op)

    def set_text_position(self,x,y):
        """
        """
        self.text_pos = (x,y)

        op = dict(op=KIVA_OPCODES['set_text_position'], pos=(x,y))
        self._add_op(op)

    def get_text_position(self):
        """
        """
        return self.text_pos

    def set_text_matrix(self,ttm):
        """
        """
        self.text_transform = ttm

        op = dict(op=KIVA_OPCODES['set_text_matrix'], matrix=ttm)
        self._add_op(op)

    def get_text_matrix(self):
        """
        """
        return self.text_transform

    def show_text(self, text, point=None):
        """ Draw text on the device at current text position.

            This is also used for showing text at a particular point
            specified by x and y.
        """
        op = dict(op=KIVA_OPCODES['show_text'], text=text)
        if point:
            op['pos'] = point
        self._add_op(op)

    def show_text_at_point(self, text, x, y):
        """ Draw text at some point (x,y).
        """
        op = dict(op=KIVA_OPCODES['show_text_at_point'], text=text, pos=(x,y))
        self._add_op(op)

    def show_glyphs(self):
        """
        """
        op = dict(op=KIVA_OPCODES['show_glyphs'])
        self._add_op(op)

    def get_text_extent(self, text):
        """ Returns the bounding rect of the rendered text
        """
        return 0.0, 0.0, 1.0, 1.0

    def get_full_text_extent(self, text):
        """ Backwards compatibility API over .get_text_extent() for Enable
        """
        x1, y1, x2, y2 = self.get_text_extent(text)
        return x2, y2, y1, x1

    #----------------------------------------------------------------
    # Painting paths (drawing and filling contours)
    #----------------------------------------------------------------
    # XXX: Make sure the path is on the client first!

    def stroke_path(self):
        """
        """
        op = dict(op=KIVA_OPCODES['stroke_path'])
        self._add_op(op)

        self.begin_path()

    def fill_path(self):
        """
        """
        op = dict(op=KIVA_OPCODES['fill_path'])
        self._add_op(op)

        self.begin_path()

    def eof_fill_path(self):
        """
        """
        self.begin_path()

        op = dict(op=KIVA_OPCODES['eof_fill_path'])
        self._add_op(op)

    def stroke_rect(self,rect):
        """
        """
        op = dict(op=KIVA_OPCODES['stroke_rect'], rect=rect)
        self._add_op(op)

    def stroke_rect_with_width(self,rect,width):
        """
        """
        op = dict(op=KIVA_OPCODES['stroke_rect_with_width'], rect=rect,
                  width=width)
        self._add_op(op)

    def fill_rect(self,rect):
        """
        """
        op = dict(op=KIVA_OPCODES['fill_rect'], rect=rect)
        self._add_op(op)

    def fill_rects(self):
        """
        """
        raise NotImplementedError

    def clear_rect(self, rect):
        """
        """
        op = dict(op=KIVA_OPCODES['clear_rect'], rect=rect)
        self._add_op(op)

    def clear(self, clear_color=(1.0,1.0,1.0,1.0)):
        """
        """
        op = dict(op=KIVA_OPCODES['clear'], color=clear_color)
        self._add_op(op)

    def draw_path(self, mode):
        """ Walk through all the drawing subpaths and draw each element.

            Each subpath is drawn separately.
        """
        self.begin_path()

        op = dict(op=KIVA_OPCODES['draw_path'], mode=mode)
        self._add_op(op)

    def get_empty_path(self):
        """ Return a path object that can be built up and then reused.
        """
        return CompiledPath()

    def draw_path_at_points(self, points, path, mode):
        op = dict(op=KIVA_OPCODES['draw_path_at_points'], path=path, mode=mode,
                  points=points)
        self._add_op(op)

    def save(self, filename, file_format=None):
        """ Save the contents of the context to a file
        """
        pass

def font_metrics_provider():
    return GraphicsContext()

