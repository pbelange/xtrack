import xtrack as xt
import xpart as xp

line_ng = xt.Line(elements=[xt.Fringe(fint=0.5, hgap=0.035, k=0.12)])
line_ng.particle_ref = xp.Particles(mass0=xp.PROTON_MASS_EV, p0c=2e9)
line_ng.config.XTRACK_FRINGE_MADNG = True
line_ng.build_tracker()

line_gianni = line_ng.copy()
line_gianni.config.XTRACK_FRINGE_MADNG = False
line_gianni.config.XTRACK_FRINGE_GIANNI = True
line_gianni.build_tracker()

line_ptc = line_ng.copy()
line_ptc.config.XTRACK_FRINGE_MADNG = False
line_ptc.config.XTRACK_FRINGE_Gianni = False
line_ptc.build_tracker()

p_ng = xp.Particles(p0c=2e9, x=0.001, y=0.002, px=0.12/2, py=0.04, delta=0.001)
p_gianni = p_ng.copy()
p_ptc = p_ng.copy()

line_ng.track(p_ng)
line_gianni.track(p_gianni)
line_ptc.track(p_ptc)

print(f'y_ng =     {p_ng.y[0]}')
print(f'y_ptc =    {p_ptc.y[0]}')
print(f'y_gianni = {p_gianni.y[0]}')

print(f'py_ng =     {p_ng.py[0]}')
print(f'py_ptc =    {p_ptc.py[0]}')
print(f'py_gianni = {p_gianni.py[0]}')

# R_ng = line_ng.compute_one_turn_matrix_finite_differences(
#     particle_on_co=line_ng.build_particles(px=0.04, py= 0.05, x=0.01, y=0.02))
# R_gianni = line_gianni.compute_one_turn_matrix_finite_differences(
#     particle_on_co=line_gianni.build_particles(px=0.04, py= 0.05, x=0.01, y=0.02))
# R_ptc = line_ptc.compute_one_turn_matrix_finite_differences(
#     particle_on_co=line_ptc.build_particles(px=0.04, py= 0.05, x=0.01, y=0.02))