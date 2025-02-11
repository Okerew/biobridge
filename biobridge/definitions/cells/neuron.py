from biobridge.definitions.cells.eukaryotic_cell import EukaryoticCell, json
from biobridge.neural_network import Neuron


class NeuronCell(EukaryoticCell, Neuron):
    def __init__(self, name, cell_type, activation_function="sigmoid", *args, **kwargs):
        EukaryoticCell.__init__(self, name, cell_type, *args, **kwargs)
        Neuron.__init__(self, name, cell_type, activation_function)

    def activate_neuron(self, current_time):
        """Activate the neuron and handle the logic."""
        if self.activate(current_time):
            print(f"Neuron {self.name} fired!")
        else:
            print(f"Neuron {self.name} did not fire.")

    def describe(self):
        """Extend the Cell's describe method to include Neuron specifics."""
        base_description = super().describe()
        neuron_description = f"Activation Function: {self.activation_function}\n" \
                             f"Threshold: {self.threshold}\n" \
                             f"Activation: {self.activation}\n" \
                             f"Output: {self.output}\n" \
                             f"Fired: {self.fired}\n" \
                             f"Learning Rate: {self.learning_rate}\n" \
                             f"Refractory Period: {self.refractory_period}\n" \
                             f"Last Spike Time: {self.last_spike_time}"
        return base_description + "\n" + neuron_description

    def update(self, current_time, external_input=0.0):
        """Update method to simulate neuron behavior along with cell metabolism."""
        self.activation += external_input
        if self.activate_neuron(current_time):
            self.adjustThreshold(0.5)   # Adjust the threshold when the neuron fires
        self.metabolize()

    def to_json(self) -> str:
        """Return a JSON representation of the neuron."""
        neuron_dict = super().__dict__.copy()
        neuron_dict.update({
            "activation_function": self.activation_function,
            "threshold": self.threshold,
            "activation": self.activation,
            "output": self.output,
            "fired": self.fired,
            "learning_rate": self.learning_rate,
            "refractory_period": self.refractory_period,
            "last_spike_time": self.last_spike_time
        })
        return json.dumps(neuron_dict)

    @classmethod
    def from_json(cls, json_str: str) -> 'NeuronCell':
        """Load a neuron from a JSON string."""
        neuron_dict = json.loads(json_str)
        neuron = cls(
            name=neuron_dict['name'],
            cell_type=neuron_dict['cell_type'],
            activation_function=neuron_dict['activation_function'],
            threshold=neuron_dict['threshold'],
            activation=neuron_dict['activation'],
            output=neuron_dict['output'],
            fired=neuron_dict['fired'],
            learning_rate=neuron_dict['learning_rate'],
            refractory_period=neuron_dict['refractory_period'],
            last_spike_time=neuron_dict['last_spike_time']
        )
        return neuron
