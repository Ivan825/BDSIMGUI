import matplotlib
import matplotlib.pyplot as plt
import bdsim
from bdsim.blocks.displays import Scope

def run_bdsim_simulation(blocks, wires, T=5):
    """
    Run the BDSim simulation and only display the Matplotlib plot.

    :param blocks: List of blocks for the block diagram.
    :param wires: List of wires connecting the blocks.
    :param T: Simulation time (default is 5 seconds).
    """
    sim = bdsim.BDSim()  # Create BDSim instance
    bd = sim.blockdiagram()  # Create block diagram

    # Create block instances
    block_instances = {}
    for block in blocks:
        block_type = block["type"]
        name = block["name"]
        properties = block["properties"]

        # Define blocks with their properties
        if block_type == "STEP":
            block_instances[name] = bd.STEP(
                T=properties.get("Start Time", 0),
                A=properties.get("Amplitude", 1),
                name=name,
            )
        elif block_type == "GAIN":
            block_instances[name] = bd.GAIN(properties.get("Gain", 1), name=name)
        elif block_type == "SUM":
            block_instances[name] = bd.SUM(properties.get("Inputs", "+-"), name=name)
        elif block_type == "SCOPE":
            block_instances[name] = bd.SCOPE(name=name)
        else:
            raise ValueError(f"Unsupported block type: {block_type}")

    # Connect wires
    for wire in wires:
        start = wire["start"]
        end = wire["end"]
        bd.connect(block_instances[start], block_instances[end])

    # Compile and run the simulation
    bd.compile()

    try:
        results = sim.run(bd, T=T, block=False)  # Pass user-defined simulation time
        '''If ever need to display in screen take every alternate value in results and plot only if ever needed'''
        # # Collect and plot scope data
        # for block_name, block in block_instances.items():
        #     if isinstance(block, bdsim.blocks.displays.Scope):
        #         plt.figure()
        #         plt.plot(results.t, block.tdata, label=block_name)
        #         plt.title(f"Simulation Results: {block_name}")
        #         plt.xlabel("Time (s)")
        #         plt.ylabel("Value")
        #         plt.legend()
        #         plt.grid()
        #
        # # Ensure the Matplotlib plot remains open
        # plt.show(block=True)

    except Exception as e:
        print(f"Simulation failed: {e}")


# Example usage
if __name__ == "__main__":
    # Define example blocks and wires
    blocks = [
        {"type": "STEP", "name": "Step1", "properties": {"Start Time": 1, "Amplitude": 2}},
        {"type": "GAIN", "name": "Gain1", "properties": {"Gain": 2}},
        {"type": "SCOPE", "name": "Scope1", "properties": {}},
    ]

    wires = [
        {"start": "Step1", "end": "Gain1"},
        {"start": "Gain1", "end": "Scope1"},
    ]

    # Allow the user to specify the simulation time
    simulation_time = float(input("Enter simulation time (seconds): ") or 5)

    run_bdsim_simulation(blocks, wires, T=simulation_time)
