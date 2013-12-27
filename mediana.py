def checkio(number):
    n = 0
    m = 0
    while number:
        m += 1
        tmp = n + m
        if number - tmp < 0:
            if number > n:
                n += number - n
            number = 0
        else:
            n += m
            number -= m

    return n

#These "asserts" using only for self-checking and not necessary for auto-testing
if __name__ == '__main__':
    assert checkio(1) == 1
    assert checkio(2) == 1
    assert checkio(3) == 2
    assert checkio(5) == 3
    assert checkio(10) == 6
