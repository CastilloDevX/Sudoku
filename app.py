# Codigo desarrollador por todos los integrantes del equipo
import random
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def is_valid(board, row, col, num):
    # Verificar fila
    if num in board[row]:
        return False
    
    # Verificar columna
    if num in [board[i][col] for i in range(9)]:
        return False
    
    # Verificar región 3x3
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            if board[i][j] == num:
                return False
    return True

def solve_sudoku(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == '':
                for num in random.sample(range(1, 10), 9):  # Probamos números en orden aleatorio
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku(board):
                            return True
                        board[row][col] = ''  # Backtrack
                return False
    return True

def generate_complete_sudoku():
    # Crear tablero vacío
    board = [['' for _ in range(9)] for _ in range(9)]
    
    # Llenar diagonal de las 3 regiones principales primero (ayuda a la generación)
    for box in range(0, 9, 3):
        nums = random.sample(range(1, 10), 9)
        for i in range(3):
            for j in range(3):
                board[box + i][box + j] = nums.pop()
    
    # Resolver el resto del tablero
    solve_sudoku(board)
    return board

def generate_sudoku(difficulty):
    # Generar tablero completo
    solved_board = generate_complete_sudoku()
    
    # Definir celdas a ocultar según dificultad
    cells_to_remove = {
        "easy": random.randint(35, 45),   # 35-45 celdas vacías
        "medium": random.randint(46, 55), # 46-55 celdas vacías
        "hard": random.randint(56, 64)    # 56-64 celdas vacías
    }.get(difficulty, 40)

    # Crear una copia del tablero y ocultar celdas
    puzzle_board = [row.copy() for row in solved_board]
    empty_cells = 0
    attempts = 0
    
    while empty_cells < cells_to_remove and attempts < 200:
        row, col = random.randint(0, 8), random.randint(0, 8)
        if puzzle_board[row][col] != '':
            # Guardar el valor por si necesitamos revertir
            backup = puzzle_board[row][col]
            puzzle_board[row][col] = ''
            
            # Verificar que el puzzle tenga solución única
            temp_board = [row.copy() for row in puzzle_board]
            if count_solutions(temp_board) == 1:
                empty_cells += 1
            else:
                puzzle_board[row][col] = backup  # Revertir si no es única
            attempts += 1
    
    return {
        "puzzle": puzzle_board,
        "solution": solved_board
    }

def count_solutions(board, count=0):
    # Función para contar soluciones (asegurar solución única)
    for row in range(9):
        for col in range(9):
            if board[row][col] == '':
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        count = count_solutions(board, count)
                        if count > 1:  # Cortar si encontramos múltiples soluciones
                            return count
                        board[row][col] = ''  # Backtrack
                return count
    return count + 1

def is_valid_sudoku(board):
    # Verificar filas y columnas
    for i in range(9):
        row = [board[i][j] for j in range(9) if board[i][j] != '']
        col = [board[j][i] for j in range(9) if board[j][i] != '']
        if len(row) != len(set(row)) or len(col) != len(set(col)):
            return False

    # Verificar regiones 3x3
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            region = []
            for i in range(3):
                for j in range(3):
                    cell = board[box_row + i][box_col + j]
                    if cell != '':
                        region.append(cell)
            if len(region) != len(set(region)):
                return False
    return True

# Variable global para almacenar la solución del último Sudoku generado
current_solution = None
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    global current_solution
    difficulty = request.get_json().get("difficulty", "easy")
    sudoku = generate_sudoku(difficulty)
    current_solution = sudoku["solution"]  # Almacenar la solución
    return jsonify({"puzzle": sudoku["puzzle"]})

@app.route("/solve", methods=["GET"])
def solve():
    if current_solution is None:
        return jsonify({"error": "No hay un Sudoku generado para resolver"})
    return jsonify({"solution": current_solution})

@app.route("/validate", methods=["POST"])
def validate():
    data = request.get_json()
    board = data.get('board', [])
    
    # Primero verificar si hay celdas vacías (aunque el frontend ya lo hace)
    for row in board:
        if any(cell == '' for cell in row):
            return jsonify({
                "status": "invalid",
                "message": "Hay celdas vacías. Completa todo el tablero."
            })
    
    if is_valid_sudoku(board):
        return jsonify({
            "status": "valid",
            "message": "¡Solución correcta!"
        })
    else:
        return jsonify({
            "status": "invalid",
            "message": "Conflicto encontrado. Revisa filas, columnas o regiones."
        })

if __name__ == "__main__":
    app.run(debug=True)