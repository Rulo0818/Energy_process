document.addEventListener('DOMContentLoaded', function () {
    const typeSelect = document.getElementById('tipo_pregunta');
    const optionsContainer = document.getElementById('options-container');
    const addOptionBtn = document.getElementById('btn-add-option');
    const optionsList = document.getElementById('options-list');

    // Mapeo de tipos que requieren opciones
    const typesWithOptions = ['opcion_unica', 'opcion_multiple'];

    function toggleOptions() {
        const selectedType = typeSelect.value;
        const inputs = optionsContainer.querySelectorAll('input');

        if (typesWithOptions.includes(selectedType)) {
            optionsContainer.style.display = 'block';
            // Habilitar inputs para que se envíen y validen
            inputs.forEach(input => {
                input.disabled = false;
                input.required = true;
            });

            // Asegurar que haya al menos una opción
            if (optionsList.children.length === 0) {
                addOption();
            }
        } else {
            optionsContainer.style.display = 'none';
            // Deshabilitar inputs para ignorar validación HTML5
            inputs.forEach(input => {
                input.disabled = true;
                input.required = false;
            });
        }
    }

    function addOption() {
        const div = document.createElement('div');
        div.className = 'option-item';
        div.style.display = 'flex';
        div.style.marginBottom = '0.5rem';

        div.innerHTML = `
            <input type="text" name="opciones[]" class="form-control" placeholder="Opción de respuesta" required>
            <button type="button" class="btn btn-outline" style="margin-left: 0.5rem; color: #ef4444; border-color: #fecaca;" onclick="this.parentElement.remove()">
                ✖
            </button>
        `;
        optionsList.appendChild(div);
    }

    if (typeSelect) {
        typeSelect.addEventListener('change', toggleOptions);
        addOptionBtn.addEventListener('click', addOption);

        // Estado inicial
        toggleOptions();
    }
});
