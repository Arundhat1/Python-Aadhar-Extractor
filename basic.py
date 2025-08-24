# ===== Variables =====
name = "Arundhati"   # string
age = 21             # integer
height = 5.4         # float
is_student = True    # boolean

print(f"Name: {name}, Age: {age}, Height: {height}, Student: {is_student}")

# ===== List =====
fruits = ["apple", "banana", "cherry"]
fruits.append("orange")     # add element
fruits.remove("banana")     # remove element
print("Fruits List:", fruits)

# ===== Tuple =====
coordinates = (10, 20)  # immutable
print("Coordinates:", coordinates)

# ===== Dictionary =====
person = {
    "name": name,
    "age": age,
    "hobbies": ["reading", "coding"]
}
person["city"] = "Mumbai"  # add new key-value pair
print("Person Dictionary:", person)

# ===== Set =====
unique_numbers = {1, 2, 3, 3, 2, 1}  # duplicates auto-removed
unique_numbers.add(4)
print("Unique Numbers:", unique_numbers)

# ===== Looping =====
print("Looping through fruits:")
for fruit in fruits:
    print("-", fruit)

# ===== If-Else =====
if age >= 18:
    print(f"{name} is an adult.")
else:
    print(f"{name} is a minor.")

# ===== Functions =====
def greet(user_name):
    return f"Hello, {user_name}!"

print(greet(name))
