<?php
require_once 'includes/auth_check.php';
require_once 'config/db.php';

// Check if a specific survey ID is requested
if (isset($_GET['id'])) {
    // --- SINGLE SURVEY RESULTS VIEW ---
    $encuesta_id = $_GET['id'];

    $stmt = $pdo->prepare("SELECT * FROM encuestas WHERE encuesta_id = :id");
    $stmt->execute(['id' => $encuesta_id]);
    $encuesta = $stmt->fetch();

    if (!$encuesta) {
        // If not found, redirect to the main results page (which now shows the list)
        header("Location: resultados.php"); 
        exit;
    }

    // Permission Check
    // Admin sees all.
    // Encuestador/Gestor sees if they created it OR if logic dictates. 
    // We stick to the existing check: if not admin and not creator, deny.
    // However, if Gestors need to see results for surveys they didn't create, this needs to be adjusted.
    // Based on "lista_encuestas.php", they only see what they created.
    if ($_SESSION['rol'] !== 'admin' && $encuesta['creador_usuario_id'] != $_SESSION['usuario_id']) {
        header("Location: resultados.php");
        exit;
    }

    $stmtCount = $pdo->prepare("SELECT COUNT(DISTINCT participante_id) FROM respuestas 
                            JOIN preguntas ON respuestas.pregunta_id = preguntas.pregunta_id 
                            WHERE preguntas.encuesta_id = :id");
    $stmtCount->execute(['id' => $encuesta_id]);
    $total_participantes = $stmtCount->fetchColumn();


    $stmtQ = $pdo->prepare("SELECT * FROM preguntas WHERE encuesta_id = :id");
    $stmtQ->execute(['id' => $encuesta_id]);
    $preguntas = $stmtQ->fetchAll();

    ?>
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Resultados - <?php echo htmlspecialchars($encuesta['titulo']); ?></title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="assets/css/style.css">
        <link rel="stylesheet" href="assets/css/dashboard.css">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <div class="dashboard-layout">
            <?php include 'includes/sidebar.php'; ?>

            <main class="main-content">
                <div class="top-bar">
                    <h1 class="page-title">Resultados: <?php echo htmlspecialchars($encuesta['titulo']); ?></h1>
                    <a href="resultados.php" class="btn btn-outline">Volver a Resultados</a>
                </div>

                <div class="content-wrapper">
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-title">Total Participantes</div>
                            <div class="stat-value"><?php echo $total_participantes; ?></div>
                        </div>
                    </div>

                    <div class="results-container">
                        <?php foreach ($preguntas as $preg): ?>
                            <div class="card" style="margin-bottom: 2rem;">
                                <h3 style="margin-bottom: 1rem; font-size: 1.1rem;"><?php echo htmlspecialchars($preg['texto_pregunta']); ?></h3>

                                <?php if (in_array($preg['tipo_pregunta'], ['opcion_unica', 'opcion_multiple'])): ?>
                                    <!-- Gráfico para opciones -->
                                    <div style="height: 300px; width: 100%;">
                                        <canvas id="chart-<?php echo $preg['pregunta_id']; ?>"></canvas>
                                    </div>
                                    <?php
                                    // Obtener datos para el gráfico
                                    $stmtData = $pdo->prepare("
                                        SELECT o.texto_opcion, COUNT(r.respuesta_id) as votos
                                        FROM opciones_respuesta o
                                        LEFT JOIN respuestas r ON o.opcion_id = r.opcion_id
                                        WHERE o.pregunta_id = :pid
                                        GROUP BY o.opcion_id
                                    ");
                                    $stmtData->execute(['pid' => $preg['pregunta_id']]);
                                    $results = $stmtData->fetchAll();
                                    
                                    $labels = [];
                                    $data = [];
                                    foreach ($results as $res) {
                                        $labels[] = $res['texto_opcion'];
                                        $data[] = $res['votos'];
                                    }
                                    ?>
                                    <script>
                                        new Chart(document.getElementById('chart-<?php echo $preg['pregunta_id']; ?>'), {
                                            type: 'bar',
                                            data: {
                                                labels: <?php echo json_encode($labels); ?>,
                                                datasets: [{
                                                    label: '# de Votos',
                                                    data: <?php echo json_encode($data); ?>,
                                                    backgroundColor: 'rgba(99, 102, 241, 0.5)',
                                                    borderColor: 'rgb(99, 102, 241)',
                                                    borderWidth: 1
                                                }]
                                            },
                                            options: {
                                                responsive: true,
                                                maintainAspectRatio: false,
                                                scales: {
                                                    y: { beginAtZero: true, ticks: { stepSize: 1 } }
                                                }
                                            }
                                        });
                                    </script>

                                <?php elseif ($preg['tipo_pregunta'] === 'escala'): ?>
                                    <!-- Distribución de Escala (Corregido para soportar ID de opción o Texto) -->
                                    <?php
                                    // 1. Obtener votos por texto (1-5)
                                    $stmtEscala = $pdo->prepare("SELECT respuesta_texto as valor, COUNT(*) as count FROM respuestas WHERE pregunta_id = :pid AND respuesta_texto IS NOT NULL GROUP BY respuesta_texto");
                                    $stmtEscala->execute(['pid' => $preg['pregunta_id']]);
                                    $escalaRes = $stmtEscala->fetchAll(PDO::FETCH_KEY_PAIR);
                                    
                                    // 2. Obtener votos por Opcion ID (si existen opciones manuales)
                                    $stmtEscalaOpt = $pdo->prepare("
                                        SELECT o.texto_opcion as valor, COUNT(r.respuesta_id) as count
                                        FROM opciones_respuesta o
                                        JOIN respuestas r ON o.opcion_id = r.opcion_id
                                        WHERE o.pregunta_id = :pid
                                        GROUP BY o.texto_opcion
                                    ");
                                    $stmtEscalaOpt->execute(['pid' => $preg['pregunta_id']]);
                                    $escalaOptRes = $stmtEscalaOpt->fetchAll(PDO::FETCH_KEY_PAIR);

                                    // 3. Fusionar resultados
                                    // Intentamos normalizar etiquetas. Si son numéricas las usamos, si son texto las agregamos.
                                    $finalData = [];
                                    
                                    // Preset 1-5
                                    foreach (['1','2','3','4','5'] as $k) $finalData[$k] = 0;
                                    
                                    // Merge Text Votes
                                    foreach ($escalaRes as $k => $v) {
                                        $finalData[$k] = ($finalData[$k] ?? 0) + $v;
                                    }

                                    // Merge Option Votes
                                    foreach ($escalaOptRes as $k => $v) {
                                       $finalData[$k] = ($finalData[$k] ?? 0) + $v;
                                    }
                                    
                                    $labelsE = array_keys($finalData);
                                    $dataE = array_values($finalData);
                                    ?>
                                    <div style="height: 250px; width: 100%;">
                                        <canvas id="chart-<?php echo $preg['pregunta_id']; ?>"></canvas>
                                    </div>
                                    <script>
                                        new Chart(document.getElementById('chart-<?php echo $preg['pregunta_id']; ?>'), {
                                            type: 'bar', // Cambiado a Bar para mejor visualización mixta
                                            data: {
                                                labels: <?php echo json_encode($labelsE); ?>,
                                                datasets: [{
                                                    label: 'Votos',
                                                    data: <?php echo json_encode($dataE); ?>,
                                                    backgroundColor: 'rgba(16, 185, 129, 0.5)',
                                                    borderColor: '#10b981',
                                                    borderWidth: 1
                                                }]
                                            },
                                            options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } } }
                                        });
                                    </script>

                                <?php else: ?>
                                    <!-- Texto Libre - Listado -->
                                    <div style="max-height: 200px; overflow-y: auto; background: #f9fafb; padding: 1rem; border-radius: 0.5rem;">
                                        <?php
                                        $stmtTxt = $pdo->prepare("SELECT respuesta_texto, fecha_respuesta FROM respuestas WHERE pregunta_id = :pid ORDER BY fecha_respuesta DESC LIMIT 50");
                                        $stmtTxt->execute(['pid' => $preg['pregunta_id']]);
                                        $textos = $stmtTxt->fetchAll();
                                        ?>
                                        <?php if (count($textos) > 0): ?>
                                            <ul style="list-style: none;">
                                                <?php foreach ($textos as $t): ?>
                                                    <li style="border-bottom: 1px solid #e5e7eb; padding: 0.5rem 0; font-size: 0.9rem;">
                                                        <?php echo htmlspecialchars($t['respuesta_texto']); ?>
                                                        <span style="display: block; font-size: 0.75rem; color: var(--text-muted);"><?php echo $t['fecha_respuesta']; ?></span>
                                                    </li>
                                                <?php endforeach; ?>
                                            </ul>
                                        <?php else: ?>
                                            <p style="color: var(--text-muted);">Sin respuestas aún.</p>
                                        <?php endif; ?>
                                    </div>
                                <?php endif; ?>
                            </div>
                        <?php endforeach; ?>
                    </div>
                </div>
            </main>
        </div>
    </body>
    </html>
    <?php

} else {
    // --- LIST SURVEYS VIEW (NO ID PROVIDED) ---
    // Show user a list of surveys to view results for.
    
    // Fetch Surveys Logic (Similar to lista_encuestas.php)
    $sql = "SELECT e.*, u.nombre as creador FROM encuestas e JOIN usuarios u ON e.creador_usuario_id = u.usuario_id";
    
    if ($_SESSION['rol'] !== 'admin') {
        $sql .= " WHERE e.creador_usuario_id = :uid";
    }
    
    $sql .= " ORDER BY e.fecha_creacion DESC";
    
    $stmt = $pdo->prepare($sql);
    
    if ($_SESSION['rol'] !== 'admin') {
        $stmt->execute(['uid' => $_SESSION['usuario_id']]);
    } else {
        $stmt->execute();
    }
    
    $encuestas = $stmt->fetchAll();
    ?>
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Resultados - Seleccionar Encuesta</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="assets/css/style.css">
        <link rel="stylesheet" href="assets/css/dashboard.css">
    </head>
    <body>
        <div class="dashboard-layout">
            <?php include 'includes/sidebar.php'; ?>

            <main class="main-content">
                <div class="top-bar">
                    <h1 class="page-title">Resultados de Encuestas</h1>
                </div>

                <div class="content-wrapper">
                    <p style="margin-bottom: 2rem; color: var(--text-muted);">Selecciona una encuesta para ver los resultados detallados y gráficos.</p>
                    
                    <div class="card" style="padding: 0;">
                        <table style="width: 100%; border-collapse: collapse;">
                            <thead>
                                <tr style="background: #f9fafb; text-align: left; border-bottom: 1px solid var(--border-color);">
                                    <th style="padding: 1rem;">Título</th>
                                    <th style="padding: 1rem;">Estado</th>
                                    <th style="padding: 1rem;">Fechas</th>
                                    <th style="padding: 1rem; text-align: right;">Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php if (count($encuestas) > 0): ?>
                                    <?php foreach ($encuestas as $enc): ?>
                                    <tr style="border-bottom: 1px solid var(--border-color);">
                                        <td style="padding: 1rem; font-weight: 500;">
                                            <?php echo htmlspecialchars($enc['titulo']); ?>
                                            <?php if ($_SESSION['rol'] === 'admin'): ?>
                                                <div style="font-size: 0.75rem; color: var(--text-muted); font-weight: normal;">Por: <?php echo htmlspecialchars($enc['creador']); ?></div>
                                            <?php endif; ?>
                                        </td>
                                        <td style="padding: 1rem;">
                                            <?php 
                                            $estadoClass = '';
                                            if ($enc['estado_encuesta'] === 'activa') $estadoClass = 'color: #059669; background: #d1fae5;';
                                            elseif ($enc['estado_encuesta'] === 'cerrada') $estadoClass = 'color: #991b1b; background: #fee2e2;';
                                            else $estadoClass = 'color: #b45309; background: #fef3c7;';
                                            ?>
                                            <span style="font-size: 0.75rem; padding: 2px 8px; border-radius: 999px; <?php echo $estadoClass; ?>">
                                                <?php echo ucfirst($enc['estado_encuesta']); ?>
                                            </span>
                                        </td>
                                        <td style="padding: 1rem; font-size: 0.875rem; color: var(--text-muted);">
                                            <?php echo date('d/m', strtotime($enc['fecha_inicio'])) . ' - ' . date('d/m', strtotime($enc['fecha_fin'])); ?>
                                        </td>
                                        <td style="padding: 1rem; text-align: right;">
                                            <a href="resultados.php?id=<?php echo $enc['encuesta_id']; ?>" class="btn btn-primary" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;">Ver Resultados</a>
                                        </td>
                                    </tr>
                                    <?php endforeach; ?>
                                <?php else: ?>
                                    <tr>
                                        <td colspan="4" style="padding: 2rem; text-align: center; color: var(--text-muted);">
                                            No hay encuestas disponibles.
                                        </td>
                                    </tr>
                                <?php endif; ?>
                            </tbody>
                        </table>
                    </div>
                </div>
            </main>
        </div>
    </body>
    </html>
<?php
}
?>
