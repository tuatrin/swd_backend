
"""
Convert Number to Thai Text.
เขียนโปรแกรมรับค่าจาก user เพื่อแปลง input ของ user ที่เป็นตัวเลข เป็นตัวหนังสือภาษาไทย
โดยที่ค่าที่รับต้องมีค่ามากกว่าหรือเท่ากับ 0 และน้อยกว่า 10 ล้าน

*** อนุญาตให้ใช้แค่ตัวแปรพื้นฐาน, built-in methods ของตัวแปรและ function พื้นฐานของ Python เท่านั้น
ห้ามใช้ Library อื่น ๆ ที่ต้อง import ในการทำงาน(ยกเว้น ใช้เพื่อการ test การทำงานของฟังก์ชัน).

"""

THAI_NUM = [
    "๐",
    "๑",
    "๒",
    "๓",
    "๔",
    "๕",
    "๖",
    "๗",
    "๘",
    "๙"
]

def thai_converter():
    input_number = int(input('Input 0 - 10000000: '))
    result = ""
    if input_number >= 0 and input_number <= 10000000:

      for val in map(int, str(input_number)):
        result += THAI_NUM[val]

      print(result)

    else:
      print('Input number is out of range')

if __name__ == "__main__":
    thai_converter()