import matplotlib
import matplotlib.pyplot as plt
import bdsim
from bdsim.blocks.displays import Scope

def run_bdsim_simulation(blocks, wires, T=5):
    """
    Run the BDSim simulation and only display the Matplotlib plot.

    blocks: List of blocks for the block diagram.
     wires: List of wires connecting the blocks.
     T: Simulation time (default is 5 seconds).
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
        elif block_type == "RAMP":
            block_instances[name] = bd.RAMP(
                T=properties.get("Start Time", 0),
                slope=properties.get("Slope", 1),
                name=name,
            )
        elif block_type == "WAVEFORM":
            block_instances[name] = bd.WAVEFORM(
                wave=properties.get("Wave Type", "square"),
                freq=properties.get("Frequency", 1),
                amplitude=properties.get("Amplitude", 1),
                offset=properties.get("Offset", 0),
                phase=properties.get("Phase", 0),
                name=name,
            )
        elif block_type == "CONSTANT":
            block_instances[name] = bd.CONSTANT(
                value=properties.get("Value", 0),
                name=name,
            )
        elif block_type == "LTI":
            block_instances[name] = bd.LTI_SISO(
                N=properties.get("Numerator", [1]),
                D=properties.get("Denominator", [1, 1]),
                name=name,
            )
        else:
            raise ValueError(f"Unsupported block type: {block_type}")
    # Connect wires
    for wire in wires:
        start = wire["start"]
        end = wire["end"]

        # Check if the end block is a SUM block or if input-output ports mismatch
        if block_instances[start].nout != block_instances[end].nin or block_instances[end].type == "sum":
            # Connect specific output of start to an available input port of end
            start_port = wire.get("start_port", 0)  # Specify which output port to use, default is 0
            end_block = block_instances[end]

            # Find the first available input port for the SUM block
            available_input_port = None
            try:
                for port in range(end_block.nin):
                    # Check if a wire is already connected to this port
                    if not any(w.end.port == port for w in bd.wirelist if w.end.block == end_block):
                        available_input_port = port
                        break

                if available_input_port is None:
                    raise RuntimeError(f"All input ports on block {end} are already occupied!")

                # Connect start's specific output to the first available input of end
                bd.connect(block_instances[start][start_port], block_instances[end][available_input_port])
            except AttributeError as e:
                raise RuntimeError(f"Error connecting to block {end}: {str(e)}")

        else:
            # Connect entire blocks if inputs and outputs match
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
        #
        # plt.show(block=True)

    except Exception as e:
        print(f"Simulation failed: {e}")



