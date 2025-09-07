import sys

L_CODE = {
    "0": "0001101",
    "1": "0011001",
    "2": "0010011",
    "3": "0111101",
    "4": "0100011",
    "5": "0110001",
    "6": "0101111",
    "7": "0111011",
    "8": "0110111",
    "9": "0001011",
}
G_CODE = {
    "0": "0100111",
    "1": "0110011",
    "2": "0011011",
    "3": "0100001",
    "4": "0011101",
    "5": "0111001",
    "6": "0000101",
    "7": "0010001",
    "8": "0001001",
    "9": "0010111",
}
R_CODE = {
    "0": "1110010",
    "1": "1100110",
    "2": "1101100",
    "3": "1000010",
    "4": "1011100",
    "5": "1001110",
    "6": "1010000",
    "7": "1000100",
    "8": "1001000",
    "9": "1110100",
}
LEFT_PARITY_PATTERNS = [
    "LLLLLL",
    "LLGLGG",
    "LLGGLG",
    "LLGGGL",
    "LGLLGG",
    "LGGLLG",
    "LGGGLL",
    "LGLGLG",
    "LGLGGL",
    "LGGLGL",
]


def calculate_checksum(barcode_12_digits):
    """Calculates the EAN-13 check digit from a 12-digit barcode."""
    odd_sum = 0
    even_sum = 0
    for i, digit_char in enumerate(barcode_12_digits):
        digit = int(digit_char)
        if (i + 1) % 2 != 0:
            odd_sum += digit
        else:
            even_sum += digit * 3
    total_sum = odd_sum + even_sum
    checksum = (10 - (total_sum % 10)) % 10
    return str(checksum)


def generate_barcode_pattern(barcode_number):
    """Generates the complete binary pattern string for an EAN-13 barcode."""
    if len(barcode_number) != 13 or not barcode_number.isdigit():
        raise ValueError("Barcode must be a 13-digit number.")
    provided_checksum = barcode_number[12]
    calculated_checksum = calculate_checksum(barcode_number[:12])
    if provided_checksum != calculated_checksum:
        raise ValueError(f"Invalid barcode checksum. Provided: {provided_checksum}, Calculated: {calculated_checksum}")
    first_digit = int(barcode_number[0])
    left_hand_digits = barcode_number[1:7]
    right_hand_digits = barcode_number[7:]
    barcode_pattern = []
    barcode_pattern.append("101")
    parity_pattern_str = LEFT_PARITY_PATTERNS[first_digit]
    for i, digit_char in enumerate(left_hand_digits):
        if parity_pattern_str[i] == "L":
            barcode_pattern.append(L_CODE[digit_char])
        else:
            barcode_pattern.append(G_CODE[digit_char])
    barcode_pattern.append("01010")
    for digit_char in right_hand_digits:
        barcode_pattern.append(R_CODE[digit_char])
    barcode_pattern.append("101")
    return "".join(barcode_pattern)


def generate_pbm_image(barcode_pattern, bar_width, bar_height, padding_x, padding_y):
    """Generates PBM (P1) image content from a barcode pattern with added padding."""
    total_segments = len(barcode_pattern)
    content_width = total_segments * bar_width
    content_height = bar_height
    image_width = content_width + (2 * padding_x)
    image_height = content_height + (2 * padding_y)
    pbm_content = f"P1\n{image_width} {image_height}\n"
    barcode_content_row_pixels = []
    for segment_value in barcode_pattern:
        pixel_value = "1" if segment_value == "1" else "0"
        barcode_content_row_pixels.extend([pixel_value] * bar_width)
    padded_barcode_row_pixels = ["0"] * padding_x + barcode_content_row_pixels + ["0"] * padding_x
    padded_barcode_row_str = " ".join(padded_barcode_row_pixels) + "\n"
    blank_padded_row_pixels = ["0"] * image_width
    blank_padded_row_str = " ".join(blank_padded_row_pixels) + "\n"
    pbm_content += blank_padded_row_str * padding_y
    pbm_content += padded_barcode_row_str * content_height
    pbm_content += blank_padded_row_str * padding_y
    return pbm_content


def main():
    if len(sys.argv) != 2:
        print("Usage: python 1757170800.py <13-digit barcode>")
        sys.exit(1)
    barcode_input = sys.argv[1]
    try:
        barcode_pattern = generate_barcode_pattern(barcode_input)
        pbm_content = generate_pbm_image(barcode_pattern, 2, 30, 5, 5)
        output_filename = f"{barcode_input}.pbm"
        with open(output_filename, "w") as f:
            f.write(pbm_content)
        print(f"PBM file '{output_filename}' generated successfully.")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
