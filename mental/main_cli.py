from chat.loop import run_screening
import os
if __name__ == "__main__":
    txt = input("How have you been feeling lately?\n> ")
    run_screening(txt)
