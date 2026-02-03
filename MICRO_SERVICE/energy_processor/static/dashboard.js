document.addEventListener('DOMContentLoaded', () => {
    // Tab Navigation
    const navItems = document.querySelectorAll('.nav-item');
    const tabPanes = document.querySelectorAll('.tab-pane');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const tabId = item.getAttribute('data-tab');

            // Update active states
            navItems.forEach(nav => nav.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));

            item.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });

    // File Upload Handling
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadBtn = document.getElementById('upload-btn');
    const fileListElement = document.getElementById('file-list');

    let selectedFiles = [];

    dropZone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--primary)';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.borderColor = 'var(--border)';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--border)';
        handleFiles(e.dataTransfer.files);
    });

    function handleFiles(files) {
        selectedFiles = Array.from(files);
        renderFileList();
    }

    function renderFileList() {
        if (selectedFiles.length === 0) {
            fileListElement.innerHTML = '';
            return;
        }

        fileListElement.innerHTML = `
            <div style="margin-top: 20px; width: 100%;">
                <h4 style="margin-bottom: 10px;">Archivos seleccionados:</h4>
                ${selectedFiles.map(f => `
                    <div style="background: rgba(255,255,255,0.05); padding: 8px 16px; border-radius: 8px; margin-bottom: 4px; display: flex; justify-content: space-between;">
                        <span>${f.name}</span>
                        <span>${(f.size / 1024).toFixed(1)} KB</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    uploadBtn.addEventListener('click', async () => {
        if (selectedFiles.length === 0) {
            alert('Por favor selecciona archivos primero.');
            return;
        }

        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('file', file);
        });

        try {
            uploadBtn.innerText = 'Procesando...';
            uploadBtn.disabled = true;

            const response = await fetch('/api/process-file/', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                alert('Procesamiento completado con éxito.');
                selectedFiles = [];
                renderFileList();
                fetchStats();
            } else {
                alert('Error: ' + (result.detail || 'Error desconocido'));
            }
        } catch (error) {
            console.error('Error uploading files:', error);
            alert('Error de conexión con la API.');
        } finally {
            uploadBtn.innerText = 'Procesar Archivos';
            uploadBtn.disabled = false;
        }
    });

    // Fetch Stats and Activity
    async function fetchStats() {
        try {
            const response = await fetch('/api/energy-records/');
            if (response.ok) {
                const data = await response.json();
                document.getElementById('total-records').innerText = data.length;
                renderActivity(data.slice(0, 5));
                renderProcessedTable(data);
            }
        } catch (error) {
            console.error('Error fetching stats:', error);
            document.getElementById('total-records').innerText = '0';
        }
    }

    function renderProcessedTable(records) {
        const tableBody = document.querySelector('#processed-table tbody');
        if (!tableBody) return;

        if (records.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 20px;">No hay registros disponibles.</td></tr>';
            return;
        }

        tableBody.innerHTML = records.map(r => {
            const sumNeta = (r.valor_energia_neta_gen || []).reduce((a, b) => a + b, 0).toFixed(2);
            const sumAuto = (r.valor_energia_autoconsumida || []).reduce((a, b) => a + b, 0).toFixed(2);
            const sumTda = (r.pago_tda || []).reduce((a, b) => a + b, 0).toFixed(2);
            const fDesde = new Date(r.fecha_desde).toLocaleDateString();
            const fHasta = new Date(r.fecha_hasta).toLocaleDateString();

            return `
                <tr>
                    <td>${r.id}</td>
                    <td><span class="cups-badge">${r.cups}</span></td>
                    <td><span class="type-tag">${r.tipo_autoconsumo}</span></td>
                    <td>${fDesde}</td>
                    <td>${fHasta}</td>
                    <td class="val-num">${sumNeta}</td>
                    <td class="val-num">${sumAuto}</td>
                    <td class="val-num highlight">${sumTda} €</td>
                </tr>
            `;
        }).join('');
    }

    function renderActivity(records) {
        const recentList = document.getElementById('recent-list');
        if (records.length === 0) {
            recentList.innerHTML = '<div class="activity-item">No hay actividad reciente.</div>';
            return;
        }

        recentList.innerHTML = records.map(r => {
            const totalTda = (r.pago_tda || []).reduce((a, b) => a + b, 0).toFixed(2);
            return `
                <div class="activity-item">
                    <div style="display: flex; flex-direction: column;">
                        <span style="font-weight: 600;">Registro #${r.id}</span>
                        <span style="font-size: 12px; color: var(--text-muted);">CUPS: ${r.cups} (${r.tipo_autoconsumo})</span>
                    </div>
                    <div style="text-align: right;">
                        <span style="color: var(--success); font-weight: 600;">${totalTda} €</span>
                        <div style="font-size: 11px; color: var(--text-muted);">Procesado</div>
                    </div>
                </div>
            `;
        }).join('');
    }

    // Initial Load
    fetchStats();
});
