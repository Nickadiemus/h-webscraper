import json

jsondata = {}

def lazyLoadJson(filename, method):
    with open(filename, method) as infile:
        data = json.loads(infile)
    
def main():
    file1 = lazyLoadJson('assets/states_cities.json', 'r')
    file2 = lazyLoadJson('assets/states_shorthand.json', 'r')

    for item in file1:
        print(file1)


if __name__ == "__main__":
    main()