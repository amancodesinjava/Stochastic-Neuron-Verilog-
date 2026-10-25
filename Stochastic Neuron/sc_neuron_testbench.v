`include "sc_neuron_design.v"
`timescale 1ns / 1ps

module tb_sc_neuron;
  parameter N = 4;
  reg clk;
  reg rst_n;
  reg [N-1:0] x;
  reg [N-1:0] w;
  reg b;
  
  
  wire y;
integer file_in, file_out, scan_file;
  sc_neuron #(
    .N(N)
  ) uut (
    .clk(clk),
    .rst_n(rst_n),
    .x(x),
    .w(w),
    .b(b),
    .y(y)
  );

  always #5 clk = ~clk;

  initial
  begin
    clk = 0;
    rst_n = 0;
    x = 0;
    w = 0;
    b = 0;

    file_in = $fopen("../bitstream/inputs.txt", "r");
    if (file_in == 0) begin
      file_in = $fopen("inputs.txt", "r");
    end
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
       
        scan_file = $fscanf(file_in, "%b %b %b\n", x, w, b);
        
        #1;
        $fdisplay(file_out, "%b", y);
      end
      else
      begin
        $fclose(file_in);
        $fclose(file_out);$finish;
      end
    end
  end

endmodule
