def calculate_probability(filename):
    with open(filename, 'r') as file:
        content = file.read()
    ones = content.count('1')
    zeros = content.count('0')
    total_bits = ones + zeros
    
    probability = ones / total_bits
    print(f"Number of '1' bits : {ones}")
    print(f"Total valid bits   : {total_bits}")
    print(f"Probability of '1' : {probability:.4f} ({probability * 100:.2f}%)")
        

calculate_probability('output.txt')