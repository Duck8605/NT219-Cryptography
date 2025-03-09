def basin_map_key_hex(seed, length, mu=3):
    if not (0 < seed < 1):
        raise ValueError("Seed phải là số thực trong khoảng (0,1)")
    
    x = seed
    hex_key = ""
    for _ in range(length):
        x = mu * x * (1 - x * x)
        
        frac = abs(x - int(x))
        
        key_byte = int(frac * 256) % 256
        
        hex_key += "{:02x}".format(key_byte)
    return hex_key

def main():
    try:
        seed_input = input("Nhập seed (số thực trong khoảng (0,1)): ")
        seed = float(seed_input)
        length_input = input("Nhập độ dài chuỗi khóa (số byte): ")
        length = int(length_input)
    except ValueError:
        print("Sai định dạng đầu vào! Seed phải là số thực trong khoảng (0,1) và độ dài là số nguyên.")
        return

    try:
        key_hex = basin_map_key_hex(seed, length)
        print("Chuỗi khóa dạng hex (Basin chaotic map):", key_hex)
    except Exception as e:
        print("Lỗi:", e)

if __name__ == "__main__":
    main()
