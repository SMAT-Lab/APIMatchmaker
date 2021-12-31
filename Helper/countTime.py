path = "runtime.txt"

if __name__ == "__main__":
    times = 0
    count = 0
    with open(path, "r") as fr:
        content = fr.read()
    lst = content.split("\n")
    for item in lst:
        item = item.strip()
        if not item:
            break
        if "." in item:
            item = item.split(".")[0]
        item = int(item)
        times += item
        count += 1
    print("avg time is : ", str(times / count))
