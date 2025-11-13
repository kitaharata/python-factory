import sys


def hex_to_rgb(hex_color):
    """Converts HEX string (#RRGGBB or RRGGBB) to RGB tuple (R, G, B)."""
    hex_color = hex_color.lstrip("#").strip()
    if len(hex_color) != 6:
        raise ValueError("Invalid HEX color format: Must be 6 characters (e.g., #FFFFFF)")
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return r, g, b
    except ValueError:
        raise ValueError("Invalid hexadecimal digits in HEX color")


def rgb_to_hex(r, g, b):
    """Converts RGB tuple (0-255) to HEX string (#RRGGBB)."""
    if not all(0 <= c <= 255 for c in [r, g, b]):
        raise ValueError("RGB values must be between 0 and 255")
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}".upper()


def rgb_to_hsl(r, g, b):
    """Converts RGB tuple (0-255) to HSL tuple (H 0-360, S 0-100, L 0-100)."""
    if not all(0 <= c <= 255 for c in [r, g, b]):
        raise ValueError("RGB values must be between 0 and 255")

    r /= 255.0
    g /= 255.0
    b /= 255.0

    cmax = max(r, g, b)
    cmin = min(r, g, b)
    delta = cmax - cmin

    l = (cmax + cmin) / 2.0

    if delta == 0:
        h = 0.0
        s = 0.0
    else:
        s = delta / (1.0 - abs(2.0 * l - 1.0))
        s = delta / (1.0 - abs(2.0 * l - 1.0))

        if cmax == r:
            h = 60.0 * (((g - b) / delta) % 6.0)
        elif cmax == g:
            h = 60.0 * ((b - r) / delta + 2.0)
        else:
            h = 60.0 * ((r - g) / delta + 4.0)

    if h < 0:
        h += 360

    h = round(h)
    s_percent = round(s * 100, 2)
    l_percent = round(l * 100, 2)

    return h, s_percent, l_percent


def hsl_to_rgb(h, s, l):
    """Converts HSL tuple (H 0-360, S 0-100, L 0-100) to RGB tuple (R, G, B 0-255)."""
    if not (0 <= h <= 360 and 0 <= s <= 100 and 0 <= l <= 100):
        raise ValueError("HSL values must be H(0-360), S(0-100), L(0-100)")

    s /= 100.0
    l /= 100.0

    if s == 0:
        r = g = b = l
    else:

        def hue_to_rgb_component(p, q, t):
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1 / 6:
                return p + (q - p) * 6 * t
            if t < 1 / 2:
                return q
            if t < 2 / 3:
                return p + (q - p) * (2 / 3 - t) * 6
            return p

        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q

        r = hue_to_rgb_component(p, q, h / 360.0 + 1 / 3)
        g = hue_to_rgb_component(p, q, h / 360.0)
        b = hue_to_rgb_component(p, q, h / 360.0 - 1 / 3)

    r_int = int(round(r * 255))
    g_int = int(round(g * 255))
    b_int = int(round(b * 255))

    r_int = min(255, max(0, r_int))
    g_int = min(255, max(0, g_int))
    b_int = min(255, max(0, b_int))

    return r_int, g_int, b_int


def print_result(color_type, color_value, r, g, b, h, s, l, hex_code):
    """Prints conversion results."""
    print("-" * 30)
    print(f"Input ({color_type}): {color_value}")
    print("-" * 30)
    print(f"RGB: ({r}, {g}, {b})")
    print(f"HEX: {hex_code}")
    print(f"HSL: ({h}, {s}%, {l}%)")
    print("-" * 30)


def try_conversion(input_str):
    """Attempts to identify color format and perform conversions."""
    input_str = input_str.strip().upper()

    try:
        if (
            input_str.startswith("#") and len(input_str) == 7 and all(c in "0123456789ABCDEF" for c in input_str[1:])
        ) or (len(input_str) == 6 and all(c in "0123456789ABCDEF" for c in input_str)):
            r, g, b = hex_to_rgb(input_str)
            h, s, l = rgb_to_hsl(r, g, b)
            print_result("HEX", input_str, r, g, b, h, s, l, rgb_to_hex(r, g, b))
            return

    except ValueError:
        pass

    try:
        processed_input = input_str.strip("()").replace(",", " ")
        parts = processed_input.split()
        if len(parts) == 3:
            r = int(parts[0])
            g = int(parts[1])
            b = int(parts[2])

            if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
                h, s, l = rgb_to_hsl(r, g, b)
                hex_code = rgb_to_hex(r, g, b)
                print_result("RGB", f"({r}, {g}, {b})", r, g, b, h, s, l, hex_code)
                return
    except ValueError:
        pass

    try:
        processed_input = input_str.strip("()").replace(",", " ")
        parts = [p.rstrip("%") for p in processed_input.split()]
        if len(parts) == 3:
            h = int(parts[0])
            s = float(parts[1])
            l = float(parts[2])

            if 0 <= h <= 360 and 0 <= s <= 100 and 0 <= l <= 100:
                r, g, b = hsl_to_rgb(h, s, l)
                hex_code = rgb_to_hex(r, g, b)
                print_result("HSL", f"({h}, {s}%, {l}%)", r, g, b, h, s, l, hex_code)
                return
    except ValueError:
        pass

    print(
        f"Error: Could not parse input '{input_str}' as HEX, RGB (0-255, 0-255, 0-255), or HSL (0-360, 0-100, 0-100)."
    )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_code = " ".join(sys.argv[1:])
        try:
            try_conversion(input_code)
        except Exception as e:
            print(f"An error occurred during conversion: {e}")
    else:
        print("Color Conversion Tool (HEX/RGB/HSL)")
        print("-----------------------------------")
        print("Usage: python 1762959600.py [COLOR_CODE]")
        print("Examples:")
        print("  python 1762959600.py #FF4500")
        print("  python 1762959600.py 255, 69, 0")
        print("  python 1762959600.py 16, 100%, 50%")
