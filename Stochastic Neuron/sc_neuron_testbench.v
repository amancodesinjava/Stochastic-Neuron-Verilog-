`include "sc_neuron_design.v"
`timescale 1ns / 1ps

module tb_sc_neuron;

  // Inputs
  reg clk;
  reg rst_n;
  reg x1, x2, w1, w2, b;
  wire y;

  integer file_in, file_out, scan_file;
  sc_neuron uut (
              clk,
              rst_n,
              x1,
              x2,
              w1,
              w2,
              b,
              y
            );

  always #5 clk = ~clk;

  initial
  begin
    clk = 0;
    rst_n = 0;
    x1 = 0;
    x2 = 0;
    w1 = 0;
    w2 = 0;
    b = 0;

    file_in = $fopen("inputs.txt", "r");
    file_out = $fopen("output.txt", "w");

    #15;
    rst_n = 1;
  end

  always @(posedge clk)
  begin
    if (rst_n)
    begin
      if (!$feof(file_in))
      begin
        scan_file = $fscanf(file_in, "%b %b %b %b %b\n", x1, x2, w1, w2, b);
        #1;
        $fdisplay(file_out, "%b", y);
      end
      else
      begin
        $fclose(file_in);
        $fclose(file_out);
        $finish;
      end
    end
  end

endmodule
