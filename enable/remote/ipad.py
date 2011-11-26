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

from kiva.ipad import CompiledPath, GraphicsContext, font_metrics_provider

class NativeScrollBar(object):
    pass

class Window(BaseWindow):
    def _create_gc(self, size, pix_format="bgra32"):
        return GraphicsContext(size)

    def _window_paint(self, event):
        # Normally the GC would be disposed here, but that doesn't really make
        # sense with the remote backend.
        # XXX: Perhaps tell the gc instance that drawing is complete?
        self._gc
