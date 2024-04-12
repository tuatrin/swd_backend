
"""
เขียนโปรแกรมหา index ของตัวเลขที่มีค่ามากที่สุดใน Array ด้วยภาษา python เช่น [1,2,1,3,5,6,4] ลำดับที่มีค่ามากที่สุด คือ index = 5 โดยไม่ให้ใช้ฟังก์ชั่นที่มีอยู่แล้ว ให้ใช้แค่ลูปกับการเช็คเงื่อนไข

"""

def most_num_index(number):
    result = ""

    for index, val in enumerate(number):
      if index == 0:
        result = index
      else:
        if val > number[result]:
          result = index

    print(result)

if __name__ == "__main__":
    number = [1,2,1,3,5,6,4]
    most_num_index(number)