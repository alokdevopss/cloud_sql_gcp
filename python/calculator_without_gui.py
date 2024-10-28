def add(num1, num2):
    return num1 + num2
def sub(num1, num2):
    return num1 - num2
def multi(num1, num2):
    return num1 * num2
def div(num1, num2):
    return num1 / num2

print("Please select operation \n" \
        "1. Add\n" \
        "2. Subtract\n" \
        "3. Multiply\n" \
        "4. Divide\n")

select=int(input("input number 1, 2, 3, 4: "))
number1= int(input("Enter first number: "))
number2= int(input("Enter second number: "))

if select == 1:
    print(number1, "+", number2, "=", add(number1, number2))
elif select == 2:
    print(number1, "-", number2, "=", sub(number1, number2))
elif select == 3:
    print(number1, "*", number2, "=", multi(number1, number2))
elif select == 4:
    print(number1, "/", number2, "=", div(number1, number2))
else:
    print("invalid input")
