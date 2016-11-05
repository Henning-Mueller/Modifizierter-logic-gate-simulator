"""
Alignments.

This module contains all the possible alignments for an renderable object. They
can be used by all objects that inherit from interfaces.IRenderable. You can
either align an object to a point or to a rect like object. For more infomation
look at the align method of interfaces.IRenderable.
"""
import collections

Alignment = collections.namedtuple("Alignment", ["x", "y"])

left = 0
top = 0
middle = 1
center = 1
right = 2
bottom = 2

top_left = Alignment(0, 0)
top_middle = Alignment(1, 0)
top_center = Alignment(1, 0)
top_right = Alignment(2, 0)

middle_left = Alignment(0, 1)
middle_middle = Alignment(1, 1)
middle_center = Alignment(1, 1)
middle_right = Alignment(2, 1)

center_left = Alignment(0, 1)
center_middle = Alignment(1, 1)
center_center = Alignment(1, 1)
center_right = Alignment(2, 1)

bottom_left = Alignment(0, 2)
bottom_middle = Alignment(1, 2)
bottom_center = Alignment(1, 2)
bottom_right = Alignment(2, 2)

left_top = Alignment(0, 0)
left_middle = Alignment(0, 1)
left_center = Alignment(0, 1)
left_bottom = Alignment(0, 2)

middle_top = Alignment(1, 0)
middle_bottom = Alignment(1, 2)

center_top = Alignment(1, 0)
center_bottom = Alignment(1, 2)

right_top = Alignment(2, 0)
right_middle = Alignment(2, 1)
right_center = Alignment(2, 1)
right_bottom = Alignment(2, 2)

# A tuple of all possible alignments
_alignments = tuple(Alignment(i, j) for i in range(3) for j in range(3))
