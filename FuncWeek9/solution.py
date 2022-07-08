from collections import defaultdict

def average_city_temps():
    d = defaultdict(list)
    while True:
        enter = input('Enter name and temperature of the city:').strip()
        if not enter:
            break
        else:
            cityweather = enter.split(' ')
            if len(cityweather) == 1:
                print(f'No whitespace')
                break
            elif not cityweather[-1].isdigit():
                print(f'not a valid temperature')
                break
            elif cityweather[-1].isdigit():
                key = ' '.join(cityweather[0:-1])
                value = cityweather[-1]
                d[key].append(int(cityweather[-1]))
    r = {k: (sum(v)/len(v)) for k,v in d.items()}
    return r


