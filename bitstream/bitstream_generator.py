import random

def generate_bit(p_one):
    return 1 if random.random() < p_one else 0

def generate_bitstream(x_probs, w_probs, b_prob, num_lines, filename="inputs.txt"):
    with open(filename, "w") as f:
        for _ in range(num_lines):
            x_bits = [str(generate_bit(p)) for p in x_probs]
            w_bits = [str(generate_bit(p)) for p in w_probs]
            b_bit = str(generate_bit(b_prob))
            
            f.write(" ".join(x_bits + w_bits + [b_bit]) + "\n")

if __name__ == "__main__":
    n = int(input("Enter n: "))
    
    x_probs = [float(input(f"Enter probability for X{i+1}: ")) for i in range(n)]
    w_probs = [float(input(f"Enter probability for W{i+1}: ")) for i in range(n)]
    b_prob = float(input("Enter probability for B: "))
    
    TOTAL_LINES = 2_000_000
    OUTPUT_FILE = "input1.txt"
    
    generate_bitstream(x_probs, w_probs, b_prob, TOTAL_LINES, OUTPUT_FILE)
