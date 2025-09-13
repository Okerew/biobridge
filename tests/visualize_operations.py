import biobridge.tools.operations_simulator as ops


def main():
    simulator = ops.SurgicalSimulator()
    # Create a target with initial health
    target = ops.OperationTarget("Liver", 100.0)

    print("Launching visualization...")

    # Call visualizeOperation (interactive GUI)
    simulator.visualize_operation(target)

    # After closing the first window, you can test training mode
    print("Launching training mode visualization...")
    simulator.visualize_operation(target)


if __name__ == "__main__":
    main()
