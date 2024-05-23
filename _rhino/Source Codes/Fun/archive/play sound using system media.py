import sys
sys.path.append("..\lib")
import EnneadTab

folder = 'L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino\Source Codes\Fun\sound effects'
file = "sound effect_mario game over.wav"
path = folder + "\\" + file


from System.Media import SoundPlayer
sp = SoundPlayer()
sp.SoundLocation = path
sp.Play()
  
