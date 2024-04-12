
"""
เขียนโปรแกรมหาจำนวนเลข 0 ที่อยู่ติดกันหลังสุดของค่า factorial ด้วย Python โดยห้ามใช้ math.factorial เช่น 7! = 5040 มีเลข 0 ต่อท้าย 1 ตัว, 10! = 3628800 มีเลข 0 ต่อท้าย 2 ตัว

"""

def find_zero(number):
    factorial = 1
    result = 0

    for i in range(1, number + 1):
      factorial = factorial*i

    for val in reversed(list(str(factorial))):
      if val == "0":
        result += 1
      else:
        break

    print(result)



if __name__ == "__main__":
    factorial = 10
    find_zero(factorial)