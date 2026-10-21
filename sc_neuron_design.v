`timescale 1ns/1ps

module sc_neuron (input clk, rst_n, x1, x2, w1, w2, b, output reg y);
  wire out1, out2;
  wire[1:0] sel;
  and a1(out1, x1, w1);
  and a2(out2, x2, w2);

  rand_gen_2bit rng(clk, rst_n, sel);

  always @(*)
  begin
    case (sel)
      2'b00:
        y = out1;
      2'b01:
        y = out2;
      2'b10:
        y = b;
      2'b11:
        y = 1'b0;
      default:
        y = 1'b0;
    endcase
  end
endmodule

module rand_gen_2bit (input clk, rst_n, output wire [1:0] rand_out);

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
  assign rand_out = {state[15], state[11]};

endmodule
