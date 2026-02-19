
from utils import clean_colombian_number, format_date_colombian

def test_numbers():
    cases = [
        ("40.000,00", 40000.0),
        ("33.613,45", 33613.45),
        ("40.000", 40000.0),
        ("1.500", 1500.0), # Dot as thousand
        ("1,50", 1.50),    # Comma as decimal
        ("100", 100.0),
        (200.5, 200.5),    # Already float
        ("$ 50.000", 50000.0),
        ("COP 20.000,00", 20000.0),
        (None, 0.0),
        ("", 0.0)
    ]
    
    print("--- Testing Numbers ---")
    failures = 0
    for input_val, expected in cases:
        result = clean_colombian_number(input_val)
        if abs(result - expected) > 0.001:
            print(f"FAIL: Input '{input_val}' -> Got {result}, Expected {expected}")
            failures += 1
        else:
            print(f"PASS: '{input_val}' -> {result}")
            
    if failures == 0:
        print("ALL NUMBER TESTS PASSED")
    else:
        print(f"{failures} NUMBER TESTS FAILED")

def test_dates():
    cases = [
        ("2026-02-08", "08/02/2026"),
        ("2026/02/08", "08/02/2026"),
        ("08/02/2026", "08/02/2026"), # Already correct
        (None, ""),
        ("", "")
    ]
    
    print("\n--- Testing Dates ---")
    failures = 0
    for input_val, expected in cases:
        result = format_date_colombian(input_val)
        if result != expected:
            print(f"FAIL: Input '{input_val}' -> Got '{result}', Expected '{expected}'")
            failures += 1
        else:
            print(f"PASS: '{input_val}' -> '{result}'")

    if failures == 0:
        print("ALL DATE TESTS PASSED")
    else:
        print(f"{failures} DATE TESTS FAILED")

def test_nits():
    cases = [
        ("900.123.456-1", "900123456-1"),
        ("1.032.443.194", "1032443194"),
        ("901464705", "901464705"),
        ("800 123 456", "800123456"),
        (" 123.456 ", "123456"),
        (None, ""),
        ("", "")
    ]
    
    print("\n--- Testing NITs ---")
    failures = 0
    from utils import clean_nit
    for input_val, expected in cases:
        result = clean_nit(input_val)
        if result != expected:
            print(f"FAIL: Input '{input_val}' -> Got '{result}', Expected '{expected}'")
            failures += 1
        else:
            print(f"PASS: '{input_val}' -> '{result}'")

    if failures == 0:
        print("ALL NIT TESTS PASSED")
    else:
        print(f"{failures} NIT TESTS FAILED")

def test_nit_dv():
    # Known NITs and their DVs
    # Examples:
    # 890903938 - 8 (Bancolombia)
    # 860000001 - 6
    # 900123456 - ? (Let's see what it calculates)
    # 413729231 - ?
    
    cases = [
        ("890903938", "8"), # Bancolombia
        ("860000001", "8"), # Standard test
        ("800220154", "1"), # Envigado
        ("800197268", "4"), # DIAN
        ("123", "8"),       # Short number
    ]
    
    print("\n--- Testing NIT DV Calculation ---")
    failures = 0
    from utils import calculate_nit_verification_digit
    
    for input_val, expected in cases:
        result = calculate_nit_verification_digit(input_val)
        # Note: We rely on standard known DVs. 
        # If I don't know the expected for 901..., I'll just print it.
        if expected != "?":
            if result != expected:
                print(f"FAIL: Input '{input_val}' -> Got '{result}', Expected '{expected}'")
                failures += 1
            else:
                print(f"PASS: '{input_val}' -> '{result}'")
        else:
             print(f"INFO: '{input_val}' -> '{result}'")

    if failures == 0:
        print("ALL NIT DV TESTS PASSED")
    else:
        print(f"{failures} NIT DV TESTS FAILED")

if __name__ == "__main__":
    test_numbers()
    test_dates()
    test_nits()
    test_nit_dv()
