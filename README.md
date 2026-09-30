<img width="400" alt="arm_pic" src="https://github.com/user-attachments/assets/7e8b1a35-48b7-4102-b9b3-a2102b5a1f15"/>

[](https://github.com/user-attachments/assets/8f888bc7-2a79-4761-b7e8-ac3f96ce00dd)

# Outline
- [Materials](#bom)
- [Code](#code)
- [Wiring](#wiring)
- [Design](#design)
- [Contributions](#contributions)
  
Robotic arm with arduino uno


# BOM
[Google sheets](https://docs.google.com/spreadsheets/d/1iTVFNJzW-89m5eGzNgUOlDTH-qVcBC-gSiHKc8zezOk/edit?usp=sharing)

# Code

## Basic + Claw
VScode + PlatformIO
1. Install PlatformIO plugin in VScode
2. Choose New Project
3. Choose Arduino UNO as board
### C++
1. create and paste src > [main.cpp](script/main.cpp)
2. create and paste [platformio.ini](script/platformio.ini)
3. Upload code to Arduino UNO board

### Python
1. create and paste from [requirements.txt](script/requirements.txt) 
2. paste the below in terminal
```pip install -r requirements.txt```
3. create and paste [control_screen.py](script/control_screen.py)
4. run python file while connected to arduino UNO board

## Air Digits
[Github repository](https://github.com/clchrf/ntu-robotics-2026-robotarm-air-digits)

# Wiring

# Design

## Board box
[OnShape](https://cad.onshape.com/documents/f77709e5ce5be262c520dafa/w/4b2eb07887c0c508498d0155/e/a5fcd016c12caa61ba753ae8?renderMode=0&uiState=6abcc5dc0b570a9f2b8378fc)

### Outer wall
<img width="535" height="530" alt="square" src="https://github.com/user-attachments/assets/878be83b-43e8-4781-ad3f-8646950397f2" />

### Inner Wall
<img width="601" height="546" alt="image" src="https://github.com/user-attachments/assets/2cf1beed-5077-4144-bfc9-4fedb46fa51d" />

### Upper Holes
<img width="563" height="507" alt="image" src="https://github.com/user-attachments/assets/8dfe1741-86aa-4f4d-9d68-ecc78ad46b2b" />

### Side Holes
<img width="563" height="507" alt="image" src="https://github.com/user-attachments/assets/f2068181-1d4d-4f1f-b4e9-99a0016e3cad" />


## Motor box
## Arm
## Forearm
## Claw
<img width="400" alt="claw" src="https://github.com/user-attachments/assets/e9996fb6-2195-4e39-9d38-de831cacae0c" />

[OnShape](https://cad.onshape.com/documents/761557366b316c90763acd4c/w/99afad2b5040069016dce09f/e/a711ace2a2d7c05e5d14087f?renderMode=0&uiState=6abcc23a1a6abfafb3fded53)

# Contributions
- Arm Design & code 王齊均
- Claw Design 林珈亘
- Air digits [Hsin-Yen](https://github.com/clchrf)
