import bdsim

def run_bdsim_simulation():
    sim = bdsim.BDSim()
    bd = sim.blockdiagram()

    step = bd.STEP(T=1, name="Step Input")
    gain = bd.GAIN(2, name="Gain")
    scope = bd.SCOPE(name="Scope")

    bd.connect(step, gain)
    bd.connect(gain, scope)

    bd.compile()
    out = sim.run(bd, T=5)

    return {"time": out.t, "data": out.y0}
