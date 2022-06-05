import pygame.midi
import time, random
from qiskit import *
import numpy as np
from mido import Message, MidiFile, MidiTrack, MetaMessage
import mido

notes = [["C"], ["C#", "Db"], ["D"], ["Eb", "D#"], ["E"], ["F"], ["F#", "Gb"], ["G"], ["G#", "Ab"], ["A"], ["Bb", "A#"], ["B"]]

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

test = stringNote(40, "Bb", 4, majorScale("Bb"))
noteLength(test)

INSTRUMENT = 46

pygame.midi.init()
player = pygame.midi.Output(0)
player.set_instrument(INSTRUMENT) # 46, 49, 51, 78, 32, 33, 85

mid = MidiFile()
track = MidiTrack()
mid.tracks.append(track)
track.append(Message('program_change', program=INSTRUMENT, time=0))
track.append(MetaMessage('set_tempo', tempo=200000))

for i in test:
    midiNote = noteToMidi(i[0], i[1])
    track.append(Message('note_on', note=midiNote, velocity=127, time=int(mido.second2tick(second=i[2], ticks_per_beat=480, tempo=200000))))
    player.note_on(midiNote, 127)
    time.sleep(i[2])
    player.note_off(midiNote, 127)

mid.save('new_song.mid')

time.sleep(.5)
del player
pygame.midi.quit()
