To run the Stochastic Neuron Verilog, use the following terminal commands:

iverilog -o neuron_sim sc_neuron_testbench.v
vvp neuron_sim
python3 count.py
