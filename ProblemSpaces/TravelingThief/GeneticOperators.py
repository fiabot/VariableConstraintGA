import random 

def random_individual(cities, num_items):
    cities = cities[:]
    random.shuffle(cities)

    items = []

    for i in range(num_items):
        items.append(random.choice([0,0, 0, 1]))
    
    return [cities, items]

def swap(li, i1, i2):
    save = li[i1]

    li[i1] = li[i2]
    li[i2] = save  


def mutate(ind, mut_rate):
    cities = ind[0][:]
    items = ind[1][:]

    num_swaps = round(mut_rate * len(ind[0]))

    for i in range(num_swaps):
        i1 = random.randint(0, len(cities) - 1)
        i2 = random.randint(0, len(cities) -1)
        swap(cities, i1, i2)
    
    for i in range(len(items)):
        if random.random() < mut_rate:
            """if items[i] == 0:
                items[i] = 1 
            else:
                items[i] = 0 """
            items[i] = random.choice([0,0, 0, 1])

    return [cities, items]

def cross_over(par1, par2):
    # x over cities 
    city1 = par1[0]
    city2 = par2[0]

    point1 = random.randint(0, len(city1) - 2)
    point2 = random.randint(point1 + 1, len(city1) - 1)

    middle1 = city1[point1:point2]

    new_city1 = [] 

    for i, val in enumerate(city2):
        if i == point1:
            new_city1 += middle1
        
        if not val in middle1:
            new_city1.append(val)

    middle2 = city2[point1:point2]

    new_city2 = [] 

    for i, val in enumerate(city1):
        if i == point1:
            new_city2 += middle2
        
        if not val in middle2:
            new_city2.append(val)
    

    item_point = random.randint(0, len(par1[1]) - 1)

    new_items1 = par1[1][0:item_point] + par2[1][item_point:]

    new_items2= par2[1][:item_point] + par1[1][item_point:]

    return [new_city1, new_items1] , [new_city2, new_items2]



