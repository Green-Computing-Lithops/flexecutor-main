import time

def sleep_function(x):
    print(f"Processing input: {x}")
    print(f"MAP FUNCTION SLEEP")
    time.sleep(x * 2)
    return x + 7

def prime_function(x):
    print(f"Processing input: {x}")
    print(f"MAP FUNCTION PRIME")
    
    aux = x
    for i in range(1, 50 ** x):
        if i > 1:
            for j in range(2, int(i**0.5) + 1):
                if i % j == 0:
                    break
            else:
                aux = i

    print(f"MAX PRIME {aux} ")
    return aux
