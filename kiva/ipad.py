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
""" This is the remote iPad backend for kiva. """

# These are the symbols that a backend has to define.
__all__ = ["CompiledPath", "Font", "font_metrics_provider", "GraphicsContext"]

# Local imports.
from fonttools import Font

class CompiledPath(object):
    def __init__(self, path=None):
        self.empty = True
        self.current_point = (0.0, 0.0)
        print "CompiledPath.__init__"

    def begin_path(self):
        print "CompiledPath.begin_path"
        return

    def move_to(self, x, y, transform=None):
        self.current_point = (x, y)
        print "CompiledPath.move_to"

    def arc(self, x, y, r, startAngle, endAngle, clockwise=False, transform=None):
        self.current_point = (x, y)
        self.empty = False
        print "CompiledPath.arc"

    def arc_to(self, x1, y1, x2, y2, r, transform=None):
        self.current_point = (x, y)
        self.empty = False
        print "CompiledPath.arc_to"

    def curve_to(self, cx1, cy1, cx2, cy2, x, y, transform=None):
        self.current_point = (x, y)
        self.empty = False
        print "CompiledPath.curve_to"

    def line_to(self, x, y, transform=None):
        self.current_point = (x, y)
        self.empty = False
        print "CompiledPath.line_to"

    def lines(self, points, transform=None):
        self.current_point = tuple(points[-1])
        self.empty = False
        print "CompiledPath.lines"

    def add_path(self, other_path, transform=None):
        self.empty = False
        print "CompiledPath.add_path"

    def quad_curve_to(self, cx, cy, x, y, transform=None):
        self.current_point = (x, y)
        self.empty = False
        print "CompiledPath.quad_curve_to"

    def rect(self, x, y, sx, sy, transform=None):
        self.current_point = (x, y)
        self.empty = False
        print "CompiledPath.rect"

    def rects(self, rects, transform=None):
        self.empty = False
        print "CompiledPath.rects"

    def close_path(self):
        print "CompiledPath.close_path"

    def is_empty(self):
        print "CompiledPath.is_empty"
        return self.empty

    def get_current_point(self):
        print "CompiledPath.get_current_point"
        return self.current_point

    def get_bounding_box(self):
        print "CompiledPath.get_bounding_box"
        return (self.current_point[0], self.current_point[1], 1.0, 1.0)


class GraphicsContext(object):
    def __init__(self, size, *args, **kwargs):
        pass

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
        pass

    def translate_ctm(self, tx, ty):
        """ Translate the coordinate system by the given value by (tx,ty)

            tx:float --  The distance to move in the x direction
            ty:float --   The distance to move in the y direction
        """
        pass

    def rotate_ctm(self, angle):
        """ Rotates the coordinate space for drawing by the given angle.

            angle:float -- the angle, in radians, to rotate the coordinate
                           system
        """
        pass

    def concat_ctm(self, transform):
        """ Concatenate the transform to current coordinate transform matrix.

            transform:affine_matrix -- the transform matrix to concatenate with
                                       the current coordinate matrix.
        """
        pass

    def get_ctm(self):
        """ Return the current coordinate transform matrix.
        """
        t = self.gc.transform()
        return (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)

    #----------------------------------------------------------------
    # Save/Restore graphics state.
    #----------------------------------------------------------------

    def save_state(self):
        """ Save the current graphic's context state.

            This should always be paired with a restore_state
        """
        pass

    def restore_state(self):
        """ Restore the previous graphics state.
        """
        pass

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
        pass

    def set_line_width(self,width):
        """ Set the line width for drawing

            width:float -- The new width for lines in user space units.
        """
        pass

    def set_line_join(self,style):
        """ Set style for joining lines in a drawing.

            style:join_style -- The line joining style.  The available
                                styles are JOIN_ROUND, JOIN_BEVEL, JOIN_MITER.
        """
        pass

    def set_miter_limit(self,limit):
        """ Specifies limits on line lengths for mitering line joins.

            If line_join is set to miter joins, the limit specifies which
            line joins should actually be mitered.  If lines aren't mitered,
            they are joined with a bevel.  The line width is divided by
            the length of the miter.  If the result is greater than the
            limit, the bevel style is used.

            limit:float -- limit for mitering joins.
        """
        pass

    def set_line_cap(self,style):
        """ Specify the style of endings to put on line ends.

            style:cap_style -- the line cap style to use. Available styles
                               are CAP_ROUND,CAP_BUTT,CAP_SQUARE
        """
        pass

    def set_line_dash(self,lengths,phase=0):
        """

            lengths:float array -- An array of floating point values
                                   specifing the lengths of on/off painting
                                   pattern for lines.
            phase:float -- Specifies how many units into dash pattern
                           to start.  phase defaults to 0.
        """
        pass

    def set_flatness(self,flatness):
        """ Not implemented

            It is device dependent and therefore not recommended by
            the PDF documentation.
        """
        raise NotImplementedError

    #----------------------------------------------------------------
    # Sending drawing data to a device
    #----------------------------------------------------------------

    def flush(self):
        """ Send all drawing data to the destination device.
        """
        pass

    def synchronize(self):
        """ Prepares drawing data to be updated on a destination device.
        """
        pass

    #----------------------------------------------------------------
    # Page Definitions
    #----------------------------------------------------------------

    def begin_page(self):
        """ Create a new page within the graphics context.
        """
        pass

    def end_page(self):
        """ End drawing in the current page of the graphics context.
        """
        pass

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
        pass

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
        pass

    def even_odd_clip(self):
        """
        """
        pass

    def clip_to_rect(self, x, y, w, h):
        """ Clip context to the given rectangular region.

            Region should be a 4-tuple or a sequence.
        """
        pass

    def clip_to_rects(self, rects):
        """
        """
        pass

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
        msg = "set_fill_color_space not implemented on Qt yet."
        raise NotImplementedError, msg

    def set_stroke_color_space(self):
        """
        """
        msg = "set_stroke_color_space not implemented on Qt yet."
        raise NotImplementedError, msg

    def set_rendering_intent(self):
        """
        """
        msg = "set_rendering_intent not implemented on Qt yet."
        raise NotImplementedError, msg

    #----------------------------------------------------------------
    # Color manipulation
    #----------------------------------------------------------------

    def set_fill_color(self, color):
        """
        """
        pass

    def set_stroke_color(self, color):
        """
        """
        pass

    def set_alpha(self, alpha):
        """
        """
        pass

    #----------------------------------------------------------------
    # Gradients
    #----------------------------------------------------------------

    def linear_gradient(self, x1, y1, x2, y2, stops, spread_method,
                        units='userSpaceOnUse'):
        """ Sets a linear gradient as the current brush.
        """
        pass

    def radial_gradient(self, cx, cy, r, fx, fy, stops, spread_method,
                        units='userSpaceOnUse'):
        """ Sets a radial gradient as the current brush.
        """
        pass

    #----------------------------------------------------------------
    # Drawing Images
    #----------------------------------------------------------------

    def draw_image(self, img, rect=None):
        """
        img is either a N*M*3 or N*M*4 numpy array, or a Kiva image

        rect - a tuple (x,y,w,h)
        """
        pass

    #----------------------------------------------------------------
    # Drawing Text
    #----------------------------------------------------------------

    def select_font(self, name, size, textEncoding):
        """ Set the font for the current graphics context.
        """
        pass

    def set_font(self, font):
        """ Set the font for the current graphics context.
        """
        pass

    def set_font_size(self, size):
        """
        """
        pass

    def set_character_spacing(self, spacing):
        """
        """
        pass

    def set_text_drawing_mode(self):
        """
        """
        pass

    def set_text_position(self,x,y):
        """
        """
        self.text_pos = (x,y)

    def get_text_position(self):
        """
        """
        return self.text_pos

    def set_text_matrix(self,ttm):
        """
        """
        self.text_transform = ttm

    def get_text_matrix(self):
        """
        """
        return self.text_transform

    def show_text(self, text, point=None):
        """ Draw text on the device at current text position.

            This is also used for showing text at a particular point
            specified by x and y.
        """
        pass

    def show_text_at_point(self, text, x, y):
        """ Draw text at some point (x,y).
        """
        pass

    def show_glyphs(self):
        """
        """
        raise NotImplementedError

    def get_text_extent(self, text):
        """ Returns the bounding rect of the rendered text
        """
        return rect.left(), -fm.descent(), rect.right(), fm.height()

    def get_full_text_extent(self, text):
        """ Backwards compatibility API over .get_text_extent() for Enable
        """
        x1, y1, x2, y2 = self.get_text_extent(text)
        return x2, y2, y1, x1

    #----------------------------------------------------------------
    # Painting paths (drawing and filling contours)
    #----------------------------------------------------------------

    def stroke_path(self):
        """
        """
        self.begin_path()

    def fill_path(self):
        """
        """
        self.begin_path()

    def eof_fill_path(self):
        """
        """
        self.begin_path()

    def stroke_rect(self,rect):
        """
        """
        pass

    def stroke_rect_with_width(self,rect,width):
        """
        """
        pass

    def fill_rect(self,rect):
        """
        """
        pass

    def fill_rects(self):
        """
        """
        raise NotImplementedError

    def clear_rect(self, rect):
        """
        """
        pass

    def clear(self, clear_color=(1.0,1.0,1.0,1.0)):
        """
        """
        pass

    def draw_path(self, mode):
        """ Walk through all the drawing subpaths and draw each element.

            Each subpath is drawn separately.
        """
        self.begin_path()

    def get_empty_path(self):
        """ Return a path object that can be built up and then reused.
        """
        return CompiledPath()

    def draw_path_at_points(self, points, path, mode):
        pass

    def save(self, filename, file_format=None):
        """ Save the contents of the context to a file
        """
        pass

def font_metrics_provider():
    return GraphicsContext()

