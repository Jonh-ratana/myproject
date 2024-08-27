# number = int(input("Number : "))
# a = bin(number)[2:]
# print(a)


# number = int(input("Number: "))

# if number == 0:
#     binary_representation = "0"
# else:
#     binary_representation = ""
#     while number > 0:
#         remainder = number % 2
#         binary_representation = str(remainder) + binary_representation
#         number = number // 2

# print(f"The binary representation is {binary_representation}")

while True:
    print("\noption 1 input\noptin 2 delete\noption 3 print\noption 4 search")
    a = int(input("choose option : "))
    if a == 1:
        print("===== input data ======")
        num1 = int(input("Input number : "))
        num2 = int(input("Input number : "))
        num3 = int(input("Input number : "))
        num4 = int(input("Input number : "))
        total = list((num1,num2,num3,num4))
        
    if a == 2:
        
        for delete in total:
            delete = int(input("input number that you wan't delete : "))
            # print(delete)
            if delete in total:
                print(f"Found {delete}")
                total.remove(delete)
            else:
                print("error")
            break
        
    if a == 3:
        for x in total:
            print(x)
        

    if a == 4:
        for search in total:
            search = int(input("Number that you want search : "))
            if search in total:
                print(f"Found {search}")
            else:
                print(f"Not found {search}")
            break