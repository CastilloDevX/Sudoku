 // Función para actualizar el tablero con datos del backend
function updateBoard(board) {
    const containers = document.querySelectorAll(".cell-container");
    containers.forEach((container, index) => {
        const row = Math.floor(index / 9);
        const col = index % 9;
        const value = board[row][col] || '';
        
        container.innerHTML = '';
        
        if (value !== '') {
            // Números fijos
            const fixedNumber = document.createElement('p');
            fixedNumber.className = 'fixed-number';
            fixedNumber.textContent = value;
            container.appendChild(fixedNumber);
        } else {
            // Celdas editables
            const newInput = document.createElement('input');
            newInput.type = 'text';
            newInput.className = 'cell-input';
            newInput.maxLength = 1;
            
            // Asegurar que los nuevos inputs mantengan valores existentes
            if (container.querySelector('input')?.value) {
                newInput.value = container.querySelector('input').value;
            }
            
            container.appendChild(newInput);
        }
    });
}

// Manejador del botón "Generar"
async function createSudoku() {
    const loading = document.getElementById("loading");
    const generateBtn = document.getElementById("generate");
    
    // Mostrar carga y deshabilitar botón
    loading.style.display = 'block';
    generateBtn.disabled = true;
    
    try {
        const difficulty = document.getElementById("difficulty").value;
        const response = await fetch("/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ difficulty })
        });
        const data = await response.json();
        updateBoard(data.puzzle);
        document.getElementById("message").textContent = "Sudoku generado!";
        document.getElementById("message").style.color = "green"
    } catch (error) {
        document.getElementById("message").textContent = "Error al generar Sudoku";
        document.getElementById("message").style.color = "red"
    } finally {
        // Ocultar carga y habilitar botón
        loading.style.display = 'none';
        generateBtn.disabled = false;
    }
}

// Función auxiliar para verificar una celda individual
function isCellValid(board, row, col) {
    const value = board[row][col];
    
    // Verificar fila
    for (let j = 0; j < 9; j++) {
        if (j !== col && board[row][j] === value) return false;
    }
    
    // Verificar columna
    for (let i = 0; i < 9; i++) {
        if (i !== row && board[i][col] === value) return false;
    }
    
    // Verificar región 3x3
    const boxRow = Math.floor(row / 3) * 3;
    const boxCol = Math.floor(col / 3) * 3;
    for (let i = boxRow; i < boxRow + 3; i++) {
        for (let j = boxCol; j < boxCol + 3; j++) {
            if (i !== row && j !== col && board[i][j] === value) return false;
        }
    }
    
    return true;
}

// Boton de validación
document.getElementById("validate").addEventListener("click", async () => {
    const messageDiv = document.getElementById("message");
    const inputs = document.querySelectorAll('.cell-input, .cell-container input');
    const board = Array(9).fill().map(() => Array(9).fill(''));
    let hasEmpty = false;
    
    // Paso 1: Recolectar valores
    inputs.forEach(input => {
        const row = parseInt(input.parentElement.dataset.row);
        const col = parseInt(input.parentElement.dataset.col);
        const value = input.value?.trim() || input.textContent?.trim() || '';
        
        board[row][col] = value;
        
        if (value === '' && input.tagName === 'INPUT') {
            input.style.border = "2px solid red";
            hasEmpty = true;
        } else {
            input.style.border = "";
        }
    });

    if (hasEmpty) {
        messageDiv.textContent = "Hay campos vacíos! Completa todos los espacios.";
        messageDiv.style.color = "red";
        return;
    }

    // Paso 2: Validar con servidor
    const response = await fetch("/validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ board })
    });

    const result = await response.json();
    
    if (result.status === "valid") {
        messageDiv.textContent = "¡Sudoku correcto! ¡Felicidades!";
        messageDiv.style.color = "green";
    } else {
        messageDiv.textContent = "¡Conflicto encontrado! Hay números repetidos.";
        messageDiv.style.color = "red";
        
        // Marcar celdas incorrectas
        inputs.forEach(input => {
            const row = parseInt(input.parentElement.dataset.row);
            const col = parseInt(input.parentElement.dataset.col);
            if (!isCellValid(board, row, col)) {
                input.style.backgroundColor = "#ffe6e6";
            } else {
                input.style.backgroundColor = "";
            }
        });
    }
});
// Boton de Resolver
document.getElementById("solve").addEventListener("click", async () => {
    const response = await fetch("/solve");
    const data = await response.json();
    if (data.error) {
        document.getElementById("message").textContent = data.error;
        document.getElementById("message").style.color = "red"
    } else {
        updateBoard(data.solution);
        document.getElementById("message").textContent = "¡Sudoku resuelto!";
        document.getElementById("message").style.color = "green"
    }
});

document.getElementById("generate").addEventListener("click", createSudoku);
createSudoku();