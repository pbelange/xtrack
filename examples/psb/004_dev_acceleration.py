import pandas as pd
import numpy as np

from scipy.constants import c as clight

import xtrack as xt
import xdeps as xd

# REMEMBER:
# - Handle zero ramp rate

fname = 'RF_DoubleHarm.dat'

df = pd.read_csv(fname, sep='\t', skiprows=2,
    names=['t_s', 'E_kin_GeV', 'V1_MV', 'phi1_rad', 'V2_MV', 'phi2_rad'])
E_kin_GeV = df.E_kin_GeV.values
t_s = df.t_s.values

# # Stretch it to enhance change in revolution frequency
# E_min = np.min(E_kin_GeV)
# E_max = np.max(E_kin_GeV)
# E_kin_GeV = E_min/100 + (E_kin_GeV - E_min)
# # Shift the time scale for testing purposes
# t_s = t_s + 5e-3

line = xt.Line.from_json('psb_04_with_chicane_corrected_thin.json')
line.build_tracker()
line['br1.acwf7l1.1'].voltage = 5e3

# Attach energy program
ep = xt.EnergyProgram(t_s=t_s, kinetic_energy0=E_kin_GeV*1e9)
line.energy_program = ep

beta0_at_t_s = line.energy_program.get_beta0_at_t_s(t_s)
f_rev = beta0_at_t_s * clight / line.get_length()

line.functions['fun_f_rev'] = xd.FunctionPieceWiseLinear(x=t_s, y=f_rev)
line.vars['f_rev'] = line.functions['fun_f_rev'](line.vars['t_turn_s'])
line.element_refs['br1.acwf7l1.1'].frequency = line.vars['f_rev'] # cavity on h=1

tw6d = line.twiss(method='6d')

t_rev = []
qs = []
zeta_co = []
for ii in range(len(t_s)):
    print(f'Computing twiss at t_s = {t_s[ii]:.4} s    ', end='\r', flush=True)
    line.vars['t_turn_s'] = t_s[ii]
    tt = line.twiss(method='6d')
    t_rev.append(tt.T_rev0)
    qs.append(tt.qs)
    zeta_co.append(tt.zeta[0])



tw = line.twiss()

# Test tracking
p_test = line.build_particles(x_norm=0, zeta=np.linspace(0, 100., 20))
assert np.isclose(p_test.energy0[0] - p_test.mass0,  E_kin_GeV[0] * 1e9,
                  atol=0, rtol=1e-10)

line.enable_time_dependent_vars = True
n_turn_test = 10000
monitor = xt.ParticlesMonitor(num_particles=len(p_test.zeta), start_at_turn=0,
                              stop_at_turn=n_turn_test)
for ii in range(n_turn_test):
    if ii % 10 == 0:
        print(f'Tracking turn {ii}/{n_turn_test}     ', end='\r', flush=True)
    line.track(p_test, turn_by_turn_monitor=monitor)


t_test = 40e-3
p0c_test = ep.get_p0c_at_t_s(t_test)
p_test.update_p0c_and_energy_deviations(p0c_test)
ekin_test = p_test.energy0[0] - p_test.mass0

t_turn = line.energy_program.get_t_s_at_turn(np.arange(n_turn_test))

import matplotlib.pyplot as plt
plt.close('all')

plt.figure(1)
sp_ekin = plt.subplot(3,1,1)
plt.plot(t_s, E_kin_GeV)
plt.plot(t_test, ekin_test*1e-9, 'o')
plt.ylabel(r'$E_{kin}$ [GeV]')

sp_dekin = plt.subplot(3,1,2, sharex=sp_ekin)
# GeV/sec
dekin = (E_kin_GeV[1:] - E_kin_GeV[:-1])/(t_s[1:] - t_s[:-1])*1e3
plt.plot(t_s[:-1], dekin)
plt.ylabel(r'd$E_{kin}$/dt [GeV/s]')

sp_beta = plt.subplot(3,1,3, sharex=sp_ekin)
plt.plot(t_turn, monitor.beta0.T)
plt.ylabel(r'$\beta$')
plt.xlabel('t [s]')

plt.figure(2)
plt.plot(t_turn, np.arange(n_turn_test))

i_turn_test = 1000
t_test_set = ep.get_t_s_at_turn(i_turn_test)
plt.plot(t_test_set, i_turn_test, 'o')

plt.figure(3)
colors = plt.cm.jet(np.linspace(0,1, len(p_test.zeta)))
for ii in range(len(colors)):
    plt.plot(monitor.zeta[ii, :], monitor.delta[ii, :], color=colors[ii])
plt.xlim(-300, 300)
plt.ylim(-5e-3, 5e-3)

plt.show()
