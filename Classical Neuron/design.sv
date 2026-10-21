module classical_neuron_32bit (
  	input  wire [4:0]  num_inputs,
  	input  wire [31:0] x [0:15],
  	input  wire [31:0] W [0:15],
    input  wire [31:0] bias,
  	output wire [79:0] z_raw,
    output wire [31:0] y
);

  	wire [63:0] p [0:15];
  	reg  [79:0] sum_products;
    wire [63:0] scaled_bias;
  	wire [79:0] scaled_z_div;
    integer i;
  
    assign p[0]=(0<num_inputs) ? (x[0]*W[0]) : 64'd0;
    assign p[1]=(1<num_inputs) ? (x[1]*W[1]) : 64'd0;
    assign p[2]=(2<num_inputs) ? (x[2]*W[2]) : 64'd0;
    assign p[3]=(3<num_inputs) ? (x[3]*W[3]) : 64'd0;
    assign p[4]=(4<num_inputs) ? (x[4]*W[4]) : 64'd0;
    assign p[5]=(5<num_inputs) ? (x[5]*W[5]) : 64'd0;
    assign p[6]=(6<num_inputs) ? (x[6]*W[6]) : 64'd0;
    assign p[7]=(7<num_inputs) ? (x[7]*W[7]) : 64'd0;
  	assign p[8]=(8<num_inputs) ? (x[8]*W[8]) : 64'd0;
  	assign p[9]=(9<num_inputs) ? (x[9]*W[9]) : 64'd0;
  	assign p[10]=(10<num_inputs) ? (x[10]*W[10]) : 64'd0;
  	assign p[11]=(11<num_inputs) ? (x[11]*W[11]) : 64'd0;
  	assign p[12]=(12<num_inputs) ? (x[12]*W[12]) : 64'd0;
  	assign p[13]=(13<num_inputs) ? (x[13]*W[13]) : 64'd0;
  	assign p[14]=(14<num_inputs) ? (x[14]*W[14]) : 64'd0;
  	assign p[15]=(15<num_inputs) ? (x[15]*W[15]) : 64'd0;
    always @(*) begin
        sum_products=80'd0;
      	for (i=0; i<16; i=i+1) begin
            sum_products=sum_products+{8'd0, p[i]};
        end
    end
    assign scaled_bias=({32'd0, bias}<<31);
    assign z_raw=sum_products+{8'd0, scaled_bias};
  	assign scaled_z_div=z_raw >> (31+num_inputs);
    assign y=(scaled_z_div>72'd2147483648) ? 32'h80000000 : scaled_z_div[31:0];

endmodule
