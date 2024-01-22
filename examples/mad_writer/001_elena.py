from cpymad.madx import Madx
import xtrack as xt
import xdeps as xd

mad = Madx()
folder = ('../../test_data/elena')
mad.call(folder + '/elena.seq')
mad.call(folder + '/highenergy.str')
mad.call(folder + '/highenergy.beam')
mad.use('elena')

# Build xsuite line
seq = mad.sequence.elena
line = xt.Line.from_madx_sequence(seq)
line.particle_ref = xt.Particles(gamma0=seq.beam.gamma,
                                    mass0=seq.beam.mass * 1e9,
                                    q0=seq.beam.charge)

def expr_to_mad_str(expr):

    expr_str = str(expr)

    fff = line._var_management['data']['functions']
    for nn in fff._mathfunctions:
        expr_str = expr_str.replace(f'f.{nn}(', f'{nn}(')

    expr_str = expr_str.replace("'", "")
    expr_str = expr_str.replace('"', "")

    # transform vars[...] in (...)
    while "vars[" in expr_str:
        before, after = tuple(*[expr_str.split("vars[", 1)])
        # find the corresponding closing bracket
        count = 1
        for ii, cc in enumerate(after):
            if cc == "]":
                count -= 1
            elif cc == "[":
                count += 1
            if count == 0:
                break

        expr_str = before + "(" + after[:ii] + ")" + after[ii+1:]

    return expr_str

def mad_str_or_value(var):
    vv = _get_expr(var)
    if _is_ref(vv):
        out = expr_to_mad_str(vv)
        out = out.strip('._expr')
        return out
    else:
        return vv

def mad_assignment(lhs, rhs):
    if _is_ref(rhs):
        rhs = mad_str_or_value(rhs)
    if isinstance(rhs, str):
        return f"{lhs} := {rhs}"
    else:
        return f"{lhs} = {rhs}"


_get_expr = xt.elements._get_expr
_is_ref = xd.refs.is_ref

# build variables part
vars_str = ""
for vv in line.vars.keys():
    if vv == '__vary_default':
        continue
    vars_str += mad_assignment(vv, line.vars[vv]) + ";\n"


def cavity_to_madx_str(cav):
    tokens = []
    tokens.append('rfcavity')
    tokens.append(mad_assignment('freq', cav.frequency._expr * 1e-6))
    tokens.append(mad_assignment('volt', cav.voltage._expr * 1e-6))
    tokens.append(mad_assignment('lag', cav.lag._expr / 360.))

    return ', '.join(tokens)

def marker_to_madx_str(marker):
    return 'marker'

def drift_to_madx_str(drift):
    tokens = []
    tokens.append('drift')
    tokens.append(mad_assignment('l', drift.length._expr))
    return ', '.join(tokens)

def multipole_to_madx_str(mult):
    tokens = []
    tokens.append('multipole')
    tokens.append(mad_assignment('knl', mult.knl._expr))
    tokens.append(mad_assignment('ksl', mult.ksl._expr))
    tokens.append(mad_assignment('l', mult.length._expr))
    return ', '.join(tokens)


xsuite_to_mad_conveters={
    xt.Cavity: cavity_to_madx_str,
    xt.Marker: marker_to_madx_str,
    xt.Drift: drift_to_madx_str,
}

elements_str = ""
for nn in line.element_names:
    eref = line.element_refs[nn]
    el = line[nn]
    el_str = xsuite_to_mad_conveters[type(el)](eref)
    elements_str += f"{nn}: {el_str};\n"

print(elements_str)

line_str = 'myseq: line=(' + ', '.join(line.element_names) + ');'

mad_input = vars_str + '\n' + elements_str + '\n' + line_str

mad2 = Madx()
mad2.input(mad_input)
mad2.beam()
mad2.use('myseq')