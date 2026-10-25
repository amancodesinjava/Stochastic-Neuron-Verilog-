## Automated Comparison & Benchmarking

To compare both the Classical Fixed-Point Neuron and the Stochastic Neuron on arbitrary inputs, run:

```bash
python3 compare_neurons.py
```

Or pass inputs directly via CLI arguments:

```bash
python3 compare_neurons.py -n 4 -x 0.1 0.1 0.1 0.1 -w 0.2 0.2 0.2 0.2 -b 0.4 --cycles 100000 > answer.txt
```

## Running Manually

### Stochastic Neuron
To run the Stochastic Neuron Verilog manually, use the following terminal commands inside `Stochastic Neuron/`:

```bash
iverilog -o neuron_sim sc_neuron_testbench.v
vvp neuron_sim
python3 count.py
```

### Classical Neuron
To run the Classical Neuron SystemVerilog manually inside `Classical Neuron/`:

```bash
iverilog -g2012 -o classical_sim design.sv testbench.sv
vvp classical_sim
```
