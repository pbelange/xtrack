import numpy as np
import xtrack as xt

num_particles_test = 300

# fname = 'fccee_z'; gemitt_y_target = 1.4e-12; n_turns_track_test = 3000
# fname = 'fccee_w'; gemitt_y_target = 2.2e-12; n_turns_track_test = 1000
fname = 'fccee_h'; gemitt_y_target = 1.4e-12; n_turns_track_test = 400
fname = 'fccee_t'; gemitt_y_target = 2e-12; n_turns_track_test = 400


line = xt.Line.from_json(fname + '_thin.json')
# Add monitor in a dispersion-free place out of crab waist
monitor = xt.ParticlesMonitor(num_particles=num_particles_test,
                              start_at_turn=0, stop_at_turn=n_turns_track_test)
line.insert_element(element=monitor, name='monitor', index='qrdr2.3_entry')

line.build_tracker()

tw_no_rad = line.twiss(method='4d')

line.configure_radiation(model='mean')
line.compensate_radiation_energy_loss()

tw_rad_wig_off = line.twiss(eneloss_and_damping=True)

line.vars['on_wiggler_v'] = 0.1
line.compensate_radiation_energy_loss()
opt = line.match(
    solve=False,
    eneloss_and_damping=True,
    compensate_radiation_energy_loss=True,
    targets=[
        xt.Target(eq_gemitt_y=gemitt_y_target, tol=1e-15, optimize_log=True)],
    vary=xt.Vary('on_wiggler_v', step=0.01, limits=(0.1, 2))
)

opt.solve()

tw_rad = line.twiss(eneloss_and_damping=True)

ex = tw_rad.eq_gemitt_x
ey = tw_rad.eq_gemitt_y
ez = tw_rad.eq_gemitt_zeta

line.configure_radiation(model='quantum')
p = line.build_particles(num_particles=num_particles_test)
line.track(p, num_turns=n_turns_track_test, turn_by_turn_monitor=True, time=True)
print(f'Tracking time: {line.time_last_track}')

import matplotlib.pyplot as plt
plt.close('all')
for ii, (mon, element_mon, label) in enumerate(
                            [(line.record_last_track, 0, 'inside crab waist'),
                              (monitor, 'monitor', 'outside crab waist')
                             ]):

    betx = tw_rad['betx', element_mon]
    bety = tw_rad['bety', element_mon]
    betx2 = tw_rad['betx2', element_mon]
    bety1 = tw_rad['bety1', element_mon]
    dx = tw_rad['dx', element_mon]
    dy = tw_rad['dy', element_mon]

    sigma_tab = tw_rad.get_beam_covariance(gemitt_x=tw_rad.eq_gemitt_x,
                                       gemitt_y=tw_rad.eq_gemitt_y,
                                       gemitt_zeta=tw_rad.eq_gemitt_zeta)

    fig = plt.figure(ii + 1, figsize=(6.4, 4.8*1.3))
    spx = fig. add_subplot(3, 1, 1)
    spx.plot(np.std(mon.x, axis=0), label='track')
    spx.axhline(
        sigma_tab['sigma_x', element_mon],
        color='red', label='twiss')
    spx.legend(loc='lower right')
    spx.set_ylabel(r'$\sigma_{x}$ [m]')
    spx.set_ylim(bottom=0)

    spy = fig. add_subplot(3, 1, 2, sharex=spx)
    spy.plot(np.std(mon.y, axis=0), label='track')
    spy.axhline(
        sigma_tab['sigma_y', element_mon],
        color='red', label='twiss')
    spy.set_ylabel(r'$\sigma_{y}$ [m]')
    spy.set_ylim(bottom=0)

    spz = fig. add_subplot(3, 1, 3, sharex=spx)
    spz.plot(np.std(mon.zeta, axis=0))
    spz.axhline(sigma_tab['sigma_zeta', element_mon], color='red')
    spz.set_ylabel(r'$\sigma_{z}$ [m]')
    spz.set_ylim(bottom=0)

    plt.suptitle(f'{fname} - ' r'$\varepsilon_y$ = ' f'{ey*1e12:.6f} pm - {label}')

plt.show()
