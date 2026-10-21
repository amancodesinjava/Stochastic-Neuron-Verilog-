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

  reg [4:0] lfsr_reg;
  wire feedback;

  assign feedback = lfsr_reg[4] ^ lfsr_reg[2];

  always @(posedge clk or negedge rst_n)
  begin
    if (!rst_n)
    begin
      lfsr_reg <= 5'h1F;
    end
    else
    begin
      lfsr_reg <= {lfsr_reg[3:0], feedback};
    end
  end

  assign rand_out = lfsr_reg[1:0];

endmodule
