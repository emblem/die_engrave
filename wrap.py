import math
import numpy as np

from pygcode import Line, GCode, Machine
import pygcode
from math import sin, cos

center_x = 1.125/2
#center_x = 0
radius = 4.409/2

def wrap_coords(gcode:GCode):
    if gcode.modal_group == pygcode.GCodeMotion.modal_group:
        x = gcode.params['X'].value
        y = gcode.params['Y'].value
        z = gcode.params['Z'].value

        angle = (x - center_x) / radius
        new_x = sin(angle) * radius + center_x
        new_z = (cos(angle) - 1) * radius + z

        gcode.params['X'] = pygcode.Word('X', new_x)
        gcode.params['Y'] = pygcode.Word('Y', y)
        gcode.params['Z'] = pygcode.Word('Z', new_z)

    return gcode

def as_vec(gpos):
    return np.array([gpos.values['X'], gpos.values['Y'], gpos.values['Z']])

max_seg_len = .005
def subdivide_moves(block, start_pos:pygcode.Position, end_pos):
    if len(block.gcodes) != 1 or block.gcodes[0].modal_group != pygcode.GCodeMotion.modal_group or start_pos is None:
        print("NoSub: ", block)
        return [block]
    blocks = []
    p0 = as_vec(start_pos)
    p1 = as_vec(end_pos)
    move_len = np.linalg.norm(p0-p1)
    steps = max(math.floor(move_len / max_seg_len), 2)
    for i in range(1, steps):
        u = float(i)/(steps-1)
        pos = p1 * u + p0 * (1 - u)
        new_block = pygcode.Block()
        new_block.gcodes.append(pygcode.GCodeLinearMove(X=pos[0], Y=pos[1], Z=pos[2]))
        blocks.append(new_block)

    return blocks


#input = 'Test-Pattern.ngc'
#output = 'Test-Pattern-Wrapped.ngc'
input = 'auk.ngc'
output = 'wrapped_auk.ngc'
def main():
    with open(input, 'r') as fh, open(output, 'w') as out_fh:
        m_orig = Machine()
        last_pos = None
        for line_text in fh.readlines():
            line = Line(line_text)
            m_orig.process_block(line.block)
            pos = m_orig.pos
            blocks = subdivide_moves(line.block, last_pos, pos)
            [wrap_coords(code) for block in blocks for code in block.gcodes]
            [out_fh.write(str(block) + '\n') for block in blocks]
            last_pos = pos


main()

