#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license.
#------------------------------------------------------------------------------

# Enthought library imports.
from enable.abstract_window import AbstractWindow
from enable.events import KeyEvent, MouseEvent
from traits.api import Any


class BaseWindow(AbstractWindow):

    def __init__(self, parent, wid=-1, pos=None, size=None, **traits):
        AbstractWindow.__init__(self, **traits)

    #------------------------------------------------------------------------
    # Implementations of abstract methods in AbstractWindow
    #------------------------------------------------------------------------

    def set_drag_result(self, result):
        # FIXME
        raise NotImplementedError

    def _capture_mouse ( self ):
        "Capture all future mouse events"
        pass

    def _release_mouse ( self ):
        "Release the mouse capture"
        pass
    
    def _create_key_event(self, event_type, event):
        "Convert a GUI toolkit key event into a KeyEvent"
        return None

    def _create_mouse_event(self, event):
        "Convert a GUI toolkit mouse event into a MouseEvent"
        return None

    def _redraw(self, coordinates=None):
        """ Request a redraw of the window, within just the (x,y,w,h) coordinates
        (if provided), or over the entire window if coordinates is None.
        """
        pass

    def _get_control_size(self):
        if self.control:
            return (self.control.width(), self.control.height())

        return None

    def _create_gc(self, size, pix_format="bgra32"):
        raise NotImplementedError

    def _window_paint(self, event):
        raise NotImplementedError

    def set_pointer(self, pointer):
        "Sets the current cursor shape"
        raise NotImplementedError

    def _set_timer_interval(self, component, interval):
        # FIXME
        raise NotImplementedError

    def set_tooltip(self, tooltip):
        "Set the window's tooltip (if necessary)"
        # FIXME
        raise NotImplementedError

    def _set_focus(self):
        "Sets this window to have keyboard focus"
        raise NotImplementedError
    
