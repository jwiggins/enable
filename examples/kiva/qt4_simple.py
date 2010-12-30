# This is PyQt specific so force the toolkit selection.
from enthought.etsconfig.api import ETSConfig
ETSConfig.toolkit = 'qt4'

from numpy import array
import sys

try:
    from enthought.qt.api import QtGui
except ImportError:
    raise Exception('PyQt4 needs to be installed to run this example')

from enthought.kiva import Canvas


class MyCanvas(Canvas):
    
    def do_draw(self, gc):
        w = gc.width()
        h = gc.height()
        # Draw a red gradient filled box with green border
        gc.rect(w/4, h/4, w/2, h/2)
        gc.set_line_width(5.0)
        gc.set_stroke_color((0.0, 1.0, 0.0, 1.0))
        
        start = array([0.0, 1.0, 0.0, 0.0, 1.0])
        end = array([1.0, 1.0, 1.0, 1.0, 1.0])
        gc.radial_gradient(w/4, h/4, 200, w/4+100, h/4+100,
                           array([start, end]), 'reflect')
        gc.draw_path()
        return


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    w = MyCanvas()
    w.resize(500, 500)
    w.setWindowTitle("Simple Kiva.qt4 example")
    w.show()

    app.exec_()
