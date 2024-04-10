import xtrack as xt

bend = xt.Bend(k0=0.4, h=0.3, length=1)

line = xt.Line(elements=[bend, xt.Replica(_parent_name='e0')])

line.build_tracker()

tt = line.get_table(attr=True)
tt.show()

import pdb; pdb.set_trace()
line.slice_thick_elements(
    slicing_strategies=[
        xt.Strategy(slicing=xt.Teapot(3), element_type=xt.Bend),
    ])

l2 = xt.Line.from_dict(line.to_dict())