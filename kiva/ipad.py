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
from arc_conversion import arc_to_tangent_points
from fonttools import Font
import constants


class CompiledPath(object):
    pass

class GraphicsContext(object):
    pass

def font_metrics_provider():
    return GraphicsContext()

