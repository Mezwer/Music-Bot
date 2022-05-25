import pygame.midi
import time, random
from qiskit import *
import numpy as np


num_qubits = 5
circ = QuantumCircuit(num_qubits, num_qubits)
circ.h(range(num_qubits))
circ.measure(range(num_qubits), range(num_qubits))


def quantum_dice(randomizer):
    
    def random_num():

        backend_sim = Aer.get_backend('qasm_simulator')
        job_sim = execute(circ, backend_sim, shots=1)
        result_sim = job_sim.result()
        counts = result_sim.get_counts(circ)

        return int(list(counts.keys()) [0], 2)
    
    num = random_num()
    while num > randomizer:
        num = random_num()
    return num

notes = [["C"], ["C#", "Db"], ["D"], ["Eb", "D#"], ["E"], ["F"], ["F#", "Gb"], ["G"], ["G#", "Ab"], ["A"], ["Bb", "A#"], ["B"]]

def noteToMidi(note, octave):
    jump = 12
    for i in notes:
        if note in i: jump += notes.index(i)
    
    return jump + ((octave) * 12)

def majorScale(note):
    sc = [note]
    for i in range(6):
        if i != 2: 
            if sc[-1] == "B": sc.append("C#")
            elif sc[-1] == "Bb" or sc[-1] == "A#": sc.append("C")
            else: sc.append(notes[[i for i, v in enumerate(notes) if sc[-1] in v][0] + 2][0])
        else:
            if sc[-1] == "B": sc.append("C")
            else: sc.append(notes[[i for i, v in enumerate(notes) if sc[-1] in v][0] + 1][0])

    return sc

def minorScale(note):
    sc = [note]
    for i in range(6):
        if i != 1 and i != 4:
            if sc[-1] == "B": sc.append("C#")
            elif sc[-1] == "Bb" or sc[-1] == "A#": sc.append("C")
            else: sc.append(notes[[i for i, v in enumerate(notes) if sc[-1] in v][0] + 2][0])
        else:
            if sc[-1] == "B": sc.append("C")
            else: sc.append(notes[[i for i, v in enumerate(notes) if sc[-1] in v][0] + 1][0])
    
    return sc

# pre-condition start must be in scale
def stringNote(length, start, octave, scale):
    n = [[start, octave]]
    nextN = scale.index(start)
    for i in range(length - 1):
        x = quantum_dice(20)
        if 0 <= x <= 2: nextN -= 2
        elif 2 < x <= 7: nextN -= 1
        elif 7 < x <= 14: nextN += 1
        elif 14 < x <= 17: nextN += 2

        if nextN > len(scale) - 1:
            octave += 1
            nextN = nextN - (len(scale) - 1)
        elif nextN < 0:
            octave -= 1
            nextN = (len(scale) - 1) - abs(nextN)
        
        n.append([scale[nextN], octave])
    
    return n

# quarter = .4
def noteLength(noteL):
    for i in noteL:
        length = 0
        x = quantum_dice(10)
        if 0 <= x <= 2: length = .2
        elif 2 < x <= 6: length = .4
        elif 6 < x <= 8: length = .6
        else: length = .2

        i.append(length)

print(minorScale("C#"))
test = stringNote(40, "C#", 4, minorScale("C#"))
noteLength(test)

pygame.midi.init()
player = pygame.midi.Output(0)
player.set_instrument(85) # 46, 49, 51, 78, 32, 33

for i in test:
    player.note_on(noteToMidi(i[0], i[1]), 127)
    time.sleep(i[2])
    player.note_off(noteToMidi(i[0], i[1]), 127)

time.sleep(.5)
del player
pygame.midi.quit()
