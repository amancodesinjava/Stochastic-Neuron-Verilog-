`timescale 1ns/1ps

module sc_neuron #(
  parameter N = 2,      
  parameter SEL_WIDTH = $clog2(N + 1)
)(
  input clk, 
  input rst_n, 
  input [N-1:0] x,
  input [N-1:0] w,
  input b,
  output reg y
);

  wire [N-1:0] out_xw;
  wire [SEL_WIDTH-1:0] sel;
  
  and a1 [N-1:0] (out_xw, x, w);

  rand_gen #(
    .SEL_WIDTH(SEL_WIDTH)
  ) rng (
    .clk(clk), 
    .rst_n(rst_n), 
    .rand_out(sel)
  );

  always @(*)
  begin
    if (sel < N)
      y = out_xw[sel];
    else if (sel == N)
      y = b;
    else
      y = 1'b0;
  end
endmodule


module rand_gen #(
  parameter SEL_WIDTH = 2
)(
  input clk, 
  input rst_n, 
  output wire [SEL_WIDTH-1:0] rand_out
);

  reg [15:0] state;
  wire [15:0] next_state;
  wire [15:0] t1, t2, t3;
  
  assign t1 = state ^ (state << 7);
  assign t2 = t1 ^ (t1 >> 9);
  assign t3 = t2 ^ (t2 << 8);
  
  assign next_state = t3;

  always @(posedge clk or negedge rst_n)
  begin
    if (!rst_n)
    begin
      state <= 16'hACE1; 
    end
    else
    begin
      state <= next_state;
    end
  end

  genvar i;
  generate
    for (i = 0; i < SEL_WIDTH; i = i + 1) begin : rng_taps
      assign rand_out[i] = state[(i * 16) / SEL_WIDTH];
    end
  endgenerate

endmodule