module classical_neuron_32bit #(
    parameter N = 100
)(
    input  wire [$clog2(N+1)-1:0] num_inputs,
    input  wire [31:0] x [0:N-1],
    input  wire [31:0] W [0:N-1],
    input  wire [31:0] bias,
    output wire [SUM_WIDTH-1:0] z_raw,
    output wire [31:0] y
);

    localparam SUM_WIDTH = 65 + $clog2(N);

    wire [63:0] p [0:N-1];
    reg  [SUM_WIDTH-1:0] sum_products;
    wire [SUM_WIDTH-1:0] scaled_bias;
    wire [SUM_WIDTH-1:0] scaled_z_div;
    localparam SHIFT_WIDTH = $clog2($clog2(N+1)+1);
    reg [SHIFT_WIDTH-1:0] shift;
    integer i;
    integer s;

    genvar j;
    generate
        for (j = 0; j < N; j = j + 1) begin : multipliers
            assign p[j] = (j < num_inputs) ?
                          (x[j] * W[j]) : 64'd0;
        end
    endgenerate

    always @(*) begin
        sum_products = {SUM_WIDTH{1'b0}};

        for (i = 0; i < N; i = i + 1) begin
            sum_products = sum_products + {{(SUM_WIDTH-64){1'b0}}, p[i]};
        end
    end

    assign scaled_bias = {{(SUM_WIDTH-32){1'b0}}, bias} << 31;
    assign z_raw = sum_products + scaled_bias;

    always @(*) begin
        shift = 0;
        for (s = 0; s < $clog2(N+1); s = s + 1) begin
            if ((num_inputs + 1) > (1 << s))
                shift = s + 1;
        end
    end

    assign scaled_z_div = z_raw >> (31 + shift);

    assign y = (scaled_z_div > 80'd2147483648) ?
               32'h80000000 : scaled_z_div[31:0];

endmodule