# print("hello world")
# print("he2eeello00 world")

# num1 = int(input("Enter first number:"))
# num2 = int(input("ENter second number:"))
# print("Sum:", num1 + num2)
# print("Difference:", num1 - num2)
# print("Product:", num1 * num2)
# print("Quotient:", num1 / num2)

# #power
# base = float(input("Enter base"))
# exponent = float(input("Enter exponent"))
# res = (base ** exponent)
# print(res)

#oddeven
# num = int(input("enter number"))

# if num % 2 == 0:
#     print("num is even")
# else:
#     print("num is even")

# year = int(input("Enter a year: "))
# if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
#     print("Year is Leap")
# else:
#     print("Year is not Leap")
    
# a = int(input("Enter the First number: "))
# b = int(input("Enter the second number: "))
# c = int(input("Enter the third number: "))
# if (a >= b and a >= c):
#     print("Number a is max ")
# elif (b >= a and b >= c):
#     print("Number b is max ")
# else:
#     print("Number c is max")

#Frizbuzz
# for i in range(1, 20):
#     if i % 3 == 0 and i % 5 == 0:
#         print("FizzBuzz")
#     elif i % 3 == 0:
#         print("Fizz")
#     elif i % 5 == 0:
#         print("Buzz")
#     else:
#         print(i)     

# numbers = list(map(int, input("Enter numbers separated by space: ").split()))
# print("Sum:", sum(numbers))

# numbers = list(map(int , input("Enter numbers separated by space: ").split()))
# print("Average: ", sum(numbers)/len(numbers))

# numbers = list(map(int , input("Enter numbers separated by space: ").split()))
# square = [x ** 2 for x in numbers]
# print("Squares: ", square)

# num =  [1,2,3,45,5]
# maximum = max(num) 
# print(maximum)

# text = input("Enter astring: ")
# char = input("Enter a character to count: ")
# print("Count: ", text.count(char))

# data = input("Enter values: ").split()
# a,b = data 
# print("Unpacked ", a,b)

# https://chat.deepseek.com/a/chat/s/f73d8193-2a01-42ea-a1e5-6aa65584c587

#16
# contacts = { "darshi" : "123-456" , "abc" : "909-888" }
# name = input("Enter name: ")
# print("Contact:" , contacts.get(name, "Not found"))

# text = input("enter a text")
# words = text.split()
# print("Word count: ", len(words))

# dict1 = {"a" : 1 , "b" : 2}
# dict2 = {"c" : 3 , "d" : 4}
# merge = {**dict1 , **dict2}
# print("Merged:" , merge)

# text = input("Enter string: ")
# print ("Palindrome" if text == text[:: -1] else "Not")

# str1 = input("Enter first String")
# str2 = input("Enter second string")
# if sorted(str1) == (str2):
#     print("Anagram")
# else:
#     print("NOT")

# text = input("Enter a string: ")
# print("Length of String", len(text))

# text = input("Enter astring: ")
# print("Rev of Str", text[::-1])

# text = input("enter str")
# vowels = "aeiouAEIOU"
# count = sum(1 for ch in text if ch in vowels )
#  print("vowels count: " , count)

# n = int(input("Enter a number: "))
# factorial = 1
# for i in range(1 , n + 1):
#     factorial *= i
# print("Factorial:", factorial)

# n = int(input("Enter a number: "))  # Get user input
# if n > 1:
#     for i in range(2, int (n ** 0.5) + 1):
#         if  n % i == 0:
#             print("not prime")
#             break
#     else:
#             print("prime")
# else:
#     print("not prime")

# n = int(input("enter number: "))
# a,b = 0,1
# for _ in range(n):
#     print(a, end = "")
#     a, b = b, a + b

# import math
# a = int(input("Enter first number: "))
# b = int(input("Enter second number: "))
# print("GCD:", math.gcd(a, b))

# def gcd(a, b):
#     while b:
#         a, b = b, a % b  # Swap a with b, and b with remainder
#     return a

# a = int(input("Enter first number: "))
# b = int(input("Enter second number: "))
# print("GCD:", gcd(a, b))


# # LCM
# def gcd(a,b):
#     while b:
#         a, b = b, a % b
#     return a

# def lcm(a,b):
#     return abs(a * b) // gcd(a,b)

# a = int(input("enter first number: "))
# b = int(input("enter second number: "))
# print("LCM", lcm(a, b))

# filename = input("Enter filename to read: ")
# try:
#     with open(filename, "r") as f:
#         print(f.read())
# except FileNotFoundError:
#     print("File not found")

# filename = input("Enter filename: ")
# content = input("Enter content: ")
# with open(filename, "w") as file:
#     file.write(content)

# soruce = input("enter source filename: ")
# destination = input("Enter destination filename: ")
# with open(soruce, "r") as src, open(destination, "w") as dest:
#     dest.write(src.read())

# a = int(input("Enter numerator: "))
# b = int(input("Enter denominator: "))
# try:
#     print("Result:", a / b)
# except ZeroDivisionError:
#     print("Cannot divide by zero!")

# filename = input(" enter a filename: ")
# try: 
#     with open(filename, "r") as file:
#         print(file.read())
# except FileNotFoundError:
#     print("file not found")

# import math
# n = float(input("Enter a number: "))
# print("Square root:", math.sqrt(n))
# print("Sine:" , math.sin(n))

# import random
# n = int(input("Enter a range: "))
# print("Random number:", random.randint(1, n))

# from datetime import datetime
# print("Current Date and Time:", datetime.now())

# class Person:
#     def __init__(self, name, age):
#         self.name = name
#         self.age = age

#     def display(self):
#         print(f"Name: {self.name}, Age: {self.age}")

# name = input("Enter name: ")
# age = int(input("Enter age: "))
# p = Person(name, age)
# p.display()

# class Animal:
#     def speak(self):
#         print("Animal speaks")

# class Dog(Animal):
#     def bark(self):
#         print("Dog barks")

# d = Dog()
# # d.speak()
# # d.bark()

# class Bird:
#     def speak(self):
#         print("Bird sings")

# class Dog:
#     def speak(self):
#         print("Dog barks")

# def make_sound(animal):
#     animal.speak()

# bird = Bird()
# dog = Dog()
# make_sound(bird)
# make_sound(dog)
