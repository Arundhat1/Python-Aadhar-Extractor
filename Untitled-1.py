baksets = [4,2,5,6,4,3,2,1,5,6]
indexed_baskets = list(enumerate(baksets))
print(indexed_baskets)
sorted_baskets = sorted(indexed_baskets, key=lambda x: x[1])
print(sorted_baskets)