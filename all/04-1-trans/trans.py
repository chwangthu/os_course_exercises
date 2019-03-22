
def read_data():
    file = open("memory")
    memory = []
    lines = file.readlines()
    for line in lines:
        line = line.split()[2:]
        memory.append(line)
    return memory

class Translater:
    def __init__(self, memory, pdbr):
        self.memory = memory
        self.pd = memory[pdbr >> 5]
        print(self.pd)
    def translate(self):
        pass

if __name__ == "__main__":
    memory = read_data()
    translater = Translater(memory, pdbr=0xd80)
