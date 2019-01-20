
def do_work():
    for x in range(3):
        print(x)


def setup(handler):
    return handler.add(do_work)
