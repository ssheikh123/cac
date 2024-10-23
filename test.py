calorie_file = open("calorie_log.txt", 'r')
lines = calorie_file.readlines()
for i in range(20):
    calories = int(lines[i][-5:])
    print(calories)