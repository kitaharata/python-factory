from PIL import Image

WIDTH, HEIGHT = 1024, 1024

RE_START, RE_END = -2, 1
IM_START, IM_END = -1.5, 1.5
MAX_ITER = 256

img = Image.new("RGB", (WIDTH, HEIGHT))
pixels = img.load()

for x in range(WIDTH):
    for y in range(HEIGHT):
        c_real = RE_START + (x / WIDTH) * (RE_END - RE_START)
        c_imag = IM_START + (y / HEIGHT) * (IM_END - IM_START)

        c = complex(c_real, c_imag)
        z = complex(0, 0)

        for i in range(MAX_ITER):
            z = z * z + c
            if abs(z) > 2:
                break

        if i == MAX_ITER - 1:
            pixels[x, y] = (0, 0, 0)
        else:
            color_component = int(10 + 245 * ((i + 1) / MAX_ITER))
            pixels[x, y] = (color_component, color_component // 2, color_component // 4)

img.save("mandelbrot.png")
print("Mandelbrot set image saved as mandelbrot.png")
