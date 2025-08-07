WIDTH = 1024
HEIGHT = 1024
OUTPUT_FILENAME = "rule110.pbm"
RULES = {
    (1, 1, 1): 0,
    (1, 1, 0): 1,
    (1, 0, 1): 1,
    (1, 0, 0): 0,
    (0, 1, 1): 1,
    (0, 1, 0): 1,
    (0, 0, 1): 1,
    (0, 0, 0): 0,
}


def generate_image():
    """Simulates Rule 110 and writes the output to a PBM file."""
    current_gen = [0] * WIDTH
    current_gen[-1] = 1
    image_data = []

    print(f"Simulating {HEIGHT} generations of Rule 110...")
    for _ in range(HEIGHT):
        image_data.append(list(current_gen))
        next_gen = [0] * WIDTH
        for i in range(WIDTH):
            left = current_gen[i - 1] if i > 0 else 0
            center = current_gen[i]
            right = current_gen[i + 1] if i < WIDTH - 1 else 0
            neighborhood = (left, center, right)
            next_gen[i] = RULES.get(neighborhood, 0)
        current_gen = next_gen

    print(f"Writing image data to {OUTPUT_FILENAME}...")
    try:
        with open(OUTPUT_FILENAME, "w") as f:
            f.write("P1\n")
            f.write(f"{WIDTH} {HEIGHT}\n")
            for row in image_data:
                f.write(" ".join(map(str, row)) + "\n")
        print(f"Successfully generated {OUTPUT_FILENAME}")
        print("You can view this file with a standard image viewer.")
    except IOError as e:
        print(f"Error writing to file: {e}")


if __name__ == "__main__":
    generate_image()
