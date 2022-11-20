from qiskit import QuantumCircuit, QuantumRegister, Aer, ClassicalRegister, transpile 
import numpy as np
import matplotlib.pyplot as plt
from util import *

def init_slot(add_circuit, angles=None):
    """
    初めてユーザーがアクセスした時の処理
    量子回路を初期化する

    Parameter
    --------------
    add_circuit: int, str 
        量子回路に追加する回路
        1: 何もしない
        2: Xゲート
        3: RYゲート, 回転角はランダム
        4: RYゲート, 6つの回転角を選択する
        5: Hゲート
        other: Hゲート
            実装上使えるが, 今回は5で統一する 
    angles: list(float), None
        add_circuit=4の時のみ使う
        長さ6のリスト
        回転角を定義している

    Return
    --------------
    qc1: QuantumCircuit 
    qc2: QuantumCircuit
    qc3: QuantumCircuit
    chip: int
        初めに持っているチップ
    d_chip: int
        初期化した際に使ったチップ
    """
    print('Welcome to Quantum Slot Game !!!')
    print()
    # print('Default ChipNumber:', chip)
    # print()

    n = 2 #一つの量子回路のレジスタの数

    #QC1
    qc1 = QuantumCircuit()
    qr1 = QuantumRegister(n)
    qc1.add_register(qr1)

    #QC2
    qc2 = QuantumCircuit()
    qr2 = QuantumRegister(n)
    qc2.add_register(qr2)

    #QC3
    qc3 = QuantumCircuit()
    qr3 = QuantumRegister(n)
    qc3.add_register(qr3)

    #スロットマシンの状態の初期化（各量子ビットのベクトルをバラバラにする）
    #RY回路（角度は0からpiのランダム値）を追加する
    theta = np.random.rand(6)
    #print(params)
    qc1.ry(np.pi*theta[0],qr1[0])
    qc1.ry(np.pi*theta[1],qr1[1])
    qc2.ry(np.pi*theta[2],qr2[0])
    qc2.ry(np.pi*theta[3],qr2[1])
    qc3.ry(np.pi*theta[4],qr3[0])
    qc3.ry(np.pi*theta[5],qr3[1])

    #状態を確認
    print('--------------------------------------------------------------------------------')
    print('QC1 : ', end="")
    sim_state(qc1, disp=True)
    print('QC2 : ', end="")
    sim_state(qc2, disp=True)
    print('QC3 : ', end="")
    sim_state(qc3, disp=True)

    print()
    print("Let's start Quantum slot Game !!!")
    print("If you want, you can add quantum gates.")
    print()

     #回路を選択する
    print('    1: None Circuit,              , 0 chip need')
    print('    2: X    Circuit,              , 1 chip need')
    print('    3: RY   Circuit (Random angle), 1 chip need')
    print('    4: RY   Circuit (Choose angle), 4 chip need')
    print('other: H    Circuit (Default)     , 3 chip need')
    print()

    # ans = input('Input 1, 2, 3, 4, or other, then enter. ==> ')
    print(f"Citcuit {add_circuit} is chosed by user")
    print()

    if str(add_circuit) == '1':
        #何もしない    
        d_chip = 0
    elif str(add_circuit) == '2':
        #X回路を追加する
        qc1.x(qr1)
        qc2.x(qr2)
        qc3.x(qr3)
        d_chip = -1
    elif str(add_circuit) == '3':
        #RY回路（角度は0からpiのランダム値）を追加する
        params = np.random.rand(6)
        #print(params)
        qc1.ry(np.pi*params[0],qr1[0])
        qc1.ry(np.pi*params[1],qr1[1])
        qc2.ry(np.pi*params[2],qr2[0])
        qc2.ry(np.pi*params[3],qr2[1])
        qc3.ry(np.pi*params[4],qr3[0])
        qc3.ry(np.pi*params[5],qr3[1])    
        d_chip = -1
    elif str(add_circuit) == '4':
        #RY回路（角度は0から2piまで指定可能）を追加する
        if angles is None:
            raise ValueError("You must setting angles. angles is list and length is 6")
        qc1.ry(np.pi*angles[0]/180, qr1[0])
        qc1.ry(np.pi*angles[1]/180, qr1[1])
        qc2.ry(np.pi*angles[2]/180, qr2[0])
        qc2.ry(np.pi*angles[3]/180, qr2[1])
        qc3.ry(np.pi*angles[4]/180, qr3[0])
        qc3.ry(np.pi*angles[5]/180, qr3[1])
        d_chip = -4
    else:
        #アダマール回路を追加する
        qc1.h(qr1)
        qc2.h(qr2)
        qc3.h(qr3)
        d_chip= -3

    #状態を確認
    print('--------------------------------------------------------------------------------')
    print('QC1 : ', end="")
    sim_state(qc1, disp=True)
    print('QC2 : ', end="")
    sim_state(qc2, disp=True)
    print('QC3 : ', end="")
    sim_state(qc3, disp=True)
    print()

    qc1.measure_all()
    qc2.measure_all()
    qc3.measure_all()
    
    return qc1, qc2, qc3, d_chip

def play_slot(qc1, qc2, qc3, chip, d_chip):
    """
    スロットを一度回す

    Parameter
    --------------
    qc1: QuantumCircuit
    qc2: QuantumCircuit
    qc3: QuantumCircuit
    chip: int
        ゲームを始める前のチップ
    d_chip: int
        回路を初期化したときに使ったチップ
    
    Return
    --------------
    slot1[0]: int
    slot2[0]: int
    slot3[0]: int
    inc: int
        1ゲームで増えたチップの数
    chip: int 
        1ゲーム終了後のチップ
    """
    if chip <= 0:
        raise ValueError(f'Input chip is {chip}. You must remove this case in server code.')

    #QC1, QC2, QC3を測定し、量子ビットの頻度と量子ビットの履歴を取り出す
    shots=20
    ans1, mem1 = sim_state_experiment(qc1,shots)
    ans2, mem2 = sim_state_experiment(qc2,shots)
    ans3, mem3 = sim_state_experiment(qc3,shots)

    print('--------------------------------------------------------------------------------')
    #量子ビットの頻度を表示する
    print('QC1:QubitNumber',ans1)
    print('QC2:QubitNumber',ans2)
    print('QC3:QubitNumber',ans3)
    print()

    #QC1, QC2, QC3の量子ビットの履歴をスロット番号（自然数）の履歴に変換する
    slot1 = slot_memory(mem1,shots)
    slot2 = slot_memory(mem2,shots)
    slot3 = slot_memory(mem3,shots)

    #スロット番号の履歴を表示する
    print('QC1:SlotNumber ', slot1)
    print('QC2:SlotNumber ', slot2)
    print('QC3:slotNumber ', slot3)
    print()

    #スロット番号を表示する
    print('SlotNumber      ', slot1[0], slot2[0], slot3[0])
    print()

    #初期回路に必要なチップ数、チップの増加数、チップ数を表示する
    print('ChipCirciut     ', d_chip)
    print()  
    inc = chip_increment(slot1[0], slot2[0], slot3[0])
    print('ChipIncrement  ', inc)
    print()
    chip = chip + inc + d_chip
    print('NewChipNumber  ', chip)
    print('--------------------------------------------------------------------------------')
    print()

    return slot1[0], slot2[0], slot3[0], inc, chip

if __name__ == "__main__":
    init_slot(1)