import random
#from time import sleep

# I do this VERY differently, in a very OOP manner.
# I use classes to define neurons, layers, and entire brains instead of matrixes/matrices, vectors, etc.
# This is a little easier to understand from a programming standpoint rather than a mathematical standpoint.
# It uses the same math as matrices & vectors, they're just defined differently.

def cap(num, minimum, maximum):
    if num < minimum: return minimum
    elif num > maximum: return maximum
    else: return num

# Neuron Object
class neuron:
    LR = 1000000 # Learning Rate
    LS = 2 # Learning Strength (1/x)
    MR = 50 # Mutation Rate
    BS = 10 # Bias Strength (1/x)
    max_decimals = 9
    def __init__(self,inputs=[],weights=[],bias=None):
        self.inputs = list(inputs)
        self.weights = list(weights)
        if bias != None:
            self.bias = bias
        else:
            self.bias = round(cap(random.randint(-self.LR,self.LR)/self.LR/self.BS,-1/self.BS,1/self.BS)*10**self.max_decimals)/10**self.max_decimals
        while len(self.inputs) < len(self.weights):
            self.inputs.append(0)
        val = 0
        while len(self.inputs) > len(self.weights):
            weight = round(cap(random.randint(-self.LR,self.LR)/self.LR/self.LS,-1,1)*10**self.max_decimals)/10**self.max_decimals
            self.weights.append(weight)
            val += 1
    def output(self):
        out = 0+self.bias
        for x in range(len(self.inputs)):
            out += self.inputs[x] * self.weights[x]
        return round(out*10**self.max_decimals)/10**self.max_decimals
    def procreate(self,partner):
        newweights = []
        for x in range(len(self.weights)):
            if random.randint(1,self.MR) == self.MR:
                weight = (self.weights[x]+partner.weights[x])/2+random.randint(-self.LR,self.LR)/self.LR/self.LS
                weight = round(cap(weight,-1,1)*10**self.max_decimals)/10**self.max_decimals
                newweights.append(weight)
            else:
                weight = (self.weights[x]+partner.weights[x])/2
                weight = round(cap(weight,-1,1)*10**self.max_decimals)/10**self.max_decimals
                newweights.append(weight)
        if random.randint(1,self.MR) == self.MR:
            newbias = (self.bias+partner.bias)/2+random.randint(-self.LR,self.LR)/self.LR/self.LS
        else:
            newbias = (self.bias+partner.bias)/2
        newbias = round(cap(newbias,-1/self.BS,1/self.BS)*10**self.max_decimals)/10**self.max_decimals
        newinputs = []
        for x in range(len(self.weights)):
            newinputs.append(0)
        child = neuron(inputs=newinputs,weights=newweights,bias=newbias)
        child.MR = self.MR
        child.BS = self.BS
        child.LR = self.LR
        child.LS = self.LS
        return child
    def replicate(self):
        newweights = []
        for x in self.weights:
            if random.randint(1,self.MR) == self.MR:
                newweights.append(round(cap(x+random.randint(-self.LR,self.LR)/self.LR/self.LS,-1,1)*10**self.max_decimals)/10**self.max_decimals)
            else:
                newweights.append(0+x)
        newbias = 0+self.bias
        if random.randint(1,self.MR) == self.MR:
            newbias += random.randint(-self.LR,self.LR)/self.LR/self.BS
        newbias = round(cap(newbias,-1/self.BS,1/self.BS)*10**self.max_decimals)/10**self.max_decimals
        newinputs = []
        for x in range(len(self.weights)):
            newinputs.append(0)
        child = neuron(inputs=newinputs,weights=newweights,bias=newbias)
        child.MR = self.MR
        child.BS = self.BS
        child.LR = self.LR
        child.LS = self.LS
        return child

class layer:
    def __init__(self,inputs=[],neurons=[]):
        self.inputs = list(inputs)
        if type(neurons) == list:
            if len(neurons) > 0:
                self.neurons = list(neurons)
            else:
                self.neurons = [neuron(inputs=self.inputs)]
        elif type(neurons) == int:
            self.neurons = []
            for x in range(neurons):
                self.neurons.append(neuron(inputs=self.inputs))
        else:
            raise Exception("Type Error")
    def weights(self):
        weights = []
        for x in self.neurons:
            weights.append(x.weights)
        return weights
    def biases(self):
        biases = []
        for x in self.neurons:
            biases.append(x.bias)
        return biases
    def output(self):
        out = []
        for x in range(len(self.neurons)):
            out.append(self.neurons[x].output())
        return tuple(out)
    def procreate(self,partner):
        newneurons = []
        for x in range(len(self.neurons)):
            newneurons.append(self.neurons[x].procreate(partner.neurons[x]))
        newinputs = []
        for x in range(len(self.inputs)):
            newinputs.append(0)
        return layer(inputs=newinputs,neurons=newneurons)
    def replicate(self):
        newneurons = []
        for x in range(len(self.neurons)):
            newneurons.append(self.neurons[x].replicate())
        newinputs = []
        for x in range(len(self.inputs)):
            newinputs.append(0)
        return layer(inputs=newinputs,neurons=newneurons)

class brain:
    def __init__(self,inputs=[],layers=[]):
        self.inputs = inputs
        if len(layers) > 0:
            if type(layers[0]) == int:
                self.layers = []
                for x in layers:
                    self.layers.append(layer(inputs=self.inputs,neurons=x))
            else:
                self.layers = layers
        else:
            self.layers = layers
        self.rewards = 0
    def weights(self):
        weights = []
        for x in self.layers:
            weights.append(x.weights())
        return weights
    def biases(self):
        biases = []
        for x in self.layers:
            biases.append(x.biases())
        return biases
    def output(self):
        inputs = self.inputs
        for x in self.layers:
            x.inputs = list(inputs)
            inputs = x.output()
        outputs = inputs # the last layer is the output layer of neurons
        return outputs
    def output_action(self):
        outs = self.output()
        top = [-1,-2]
        for x in range(len(outs)):
            if outs [x] > top[1]:
                top = [x,outs[x]]
        return top
    def procreate(self,partner):
        newlayers = []
        for x in range(len(self.layers)):
            newlayers.append(self.layers[x].procreate(partner.layers[x]))
        newinputs = []
        for x in range(len(self.inputs)):
            newinputs.append(0)
        return brain(inputs=newinputs,layers=newlayers)
    def replicate(self):
        newlayers = []
        for x in range(len(self.layers)):
            newlayers.append(self.layers[x].replicate())
        newinputs = []
        for x in range(len(self.inputs)):
            newinputs.append(0)
        return brain(inputs=newinputs,layers=newlayers)

if __name__ == "__main__":
    # reproduction
    print("Reproduction")
    inp = [1,3,1,2,5]
    neuro = neuron(inputs=inp)
    for x in range(100):
        print(f"Generation #{x} - Bias: {neuro.bias} | Weights: {neuro.weights}")
        neuro = neuro.procreate()
    # test neuron
    print("\nNeurons")
    neurons = []
    for x in range(5):
        neu = neuron(inputs=inp)
        neurons.append(neu)
        print(f"Output: {neu.output()} | Bias: {neu.bias} | Weights: {neu.weights}")
    neurons[len(neurons)-1].weights[0] = 1
    # test layer
    print("\nLayer")
    lay = layer(inputs=inp,neurons=5)
    for x in lay.neurons:
        print(x.weights)
    print(lay.output())
    # test brain
    print("\nBrain")
    cranium = brain(inputs=inp,layers=[layer(inputs=inp,neurons=12),layer(inputs=inp,neurons=5)])
    print(cranium.output())
    for x in range(len(cranium.layers)):
        print(f"Layer #{x}")
        for z in range(len(cranium.layers[x].neurons)):
            print(cranium.layers[x].neurons[z].weights)
    cranium.output()
