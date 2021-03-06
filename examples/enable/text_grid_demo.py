
from numpy import array

from enable.example_support import DemoFrame, demo_main

from enable.api import Container, Window
from enable.text_grid import TextGrid

class MyFrame(DemoFrame):
    def _create_window(self):

        strings = array([["apple", "banana", "cherry", "durian"],
                         ["eggfruit", "fig", "grape", "honeydew"]])
        grid = TextGrid(string_array=strings)
        container = Container(bounds=[500,100])
        container.add(grid)
        return Window(self, -1, component=container)

if __name__ == "__main__":
    demo_main(MyFrame, size=[500,100])

