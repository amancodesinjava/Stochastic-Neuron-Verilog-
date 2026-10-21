module tb_classical_neuron_32bit;
  	reg [4:0]  num_inputs;
  	reg [31:0] x [0:15];
  	reg [31:0] W [0:15];
    reg [31:0] bias;
  	wire [79:0] z_raw;
    wire [31:0] y;
    real z_decimal;
    real y_decimal;
    integer k;
    classical_neuron_32bit dut (
        .num_inputs(num_inputs),
        .x(x),
        .W(W),
        .bias(bias),
        .z_raw(z_raw),
        .y(y)
    );
    function [31:0] encode;
        input real value;
        begin
            encode=$rtoi(value*2147483648.0+0.5);
        end
    endfunction

    initial begin
        num_inputs=4;
        x[0]=encode(0.75);
        x[1]=encode(0.50);
        x[2]=encode(0.20);
        x[3]=encode(0.90);
      x[4]=32'd0; x[5]=32'd0; x[6]=32'd0; x[7]=32'd0; x[8]=32'd0; x[9]=32'd0; x[10]=32'd0;x[11]=32'd0; x[12]=32'd0; x[13]=32'd0; x[14]=32'd0; x[15]=32'd0;
        W[0]=encode(0.80);
        W[1]=encode(0.60);
        W[2]=encode(0.50);
        W[3]=encode(0.40);
        W[4]=32'd0; W[5]=32'd0; W[6]=32'd0; W[7]=32'd0;
      W[8]=32'd0; W[9]=32'd0; W[10]=32'd0; W[11]=32'd0; W[12]=32'd0; W[13]=32'd0; W[14]=32'd0; W[15]=32'd0;
        bias=encode(0.10);
        #10;
        z_decimal=z_raw/4611686018427387904.0; // 2^62
        y_decimal=y/2147483648.0; // 2^31
        $display("--- Classical Neuron 32-bit (Active Inputs = %0d) ---", num_inputs);
        for (k=0; k<num_inputs; k=k+1) begin
            $display("x[%0d] binary=%032b",k,x[k]);
            $display("W[%0d] binary=%032b", k, W[k]);
        end
        $display("Bias binary   = %032b", bias);
        $display("Raw output z  = %0d", z_raw);
        $display("Decimal z     = %f", z_decimal);
        $display("Neuron y (bin)= %032b", y);
        $display("Decimal y     = %f", y_decimal);
        $finish;
    end
endmodule
