import bdsim
import bdsim.blockdiagram

def test_simulation():
    """
    A slightly larger test for BDSim.
    This sets up a simulation with multiple blocks and ensures proper connections and scope data extraction.
    """
    sim = bdsim.BDSim()
    bd = sim.blockdiagram()

    # Define blocks
    step1 = bd.STEP(T=1, Amplitude=2, name="Step 1")
    step2 = bd.STEP(T=2, Amplitude=3, name="Step 2")
    gain = bd.GAIN(K=2, name="Gain")
    sum_block = bd.SUM("++", name="Sum")
    scope = bd.SCOPE(name="Scope 1")

    # Connect blocks
    bd.connect(step1, sum_block[0])
    bd.connect(step2, sum_block[1])
    bd.connect(sum_block, gain)
    bd.connect(gain, scope)

    # Compile and simulate
    bd.compile()
    print("Simulation compiled successfully.")

    try:
        # Run the simulation and watch the scope
        results = sim.run(bd, T=5, watch=[scope])
        print("Simulation completed successfully.")
    except Exception as e:
        print(f"Simulation failed: {e}")
        return

    # Extract scope data
    try:
        scope_data = results.watch[scope]
        print("Scope Data:")
        print(f"Time: {results.t}")
        print(f"Output: {scope_data}")
    except KeyError:
        print(f"No data found for scope block: {scope.name}")
    except AttributeError as e:
        print(f"Error accessing scope data: {e}")

# Run the test
if __name__ == "__main__":
    test_simulation()
