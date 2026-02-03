<?php
require_once 'includes/auth_check.php';
require_once 'config/db.php';

if (!isset($_GET['id'])) {
    header("Location: lista_encuestas.php");
    exit;
}

$encuesta_id = $_GET['id'];
$msg = '';

// Obtener datos de la encuesta
$stmt = $pdo->prepare("SELECT * FROM encuestas WHERE encuesta_id = :id");
$stmt->execute(['id' => $encuesta_id]);
$encuesta = $stmt->fetch();

if (!$encuesta) {
    die("Encuesta no encontrada.");
}

// Seguridad: Solo admin o creador
if ($_SESSION['rol'] !== 'admin' && $encuesta['creador_usuario_id'] != $_SESSION['usuario_id']) {
    header("Location: lista_encuestas.php");
    exit;
}

// Procecsar formulario de agregar pregunta
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'add_question') {
    $texto = trim($_POST['texto_pregunta']);
    $tipo = $_POST['tipo_pregunta'];
    
    if (!empty($texto)) {
        try {
            $pdo->beginTransaction();
            
            // Insertar Pregunta
            $sql = "INSERT INTO preguntas (encuesta_id, texto_pregunta, tipo_pregunta) VALUES (:eid, :txt, :tipo)";
            $stmt = $pdo->prepare($sql);
            $stmt->execute(['eid' => $encuesta_id, 'txt' => $texto, 'tipo' => $tipo]);
            $pregunta_id = $pdo->lastInsertId();

            // Insertar Opciones si aplica
            if (in_array($tipo, ['opcion_unica', 'opcion_multiple']) && isset($_POST['opciones'])) {
                $sqlOpt = "INSERT INTO opciones_respuesta (pregunta_id, texto_opcion) VALUES (:pid, :txt)";
                $stmtOpt = $pdo->prepare($sqlOpt);
                foreach ($_POST['opciones'] as $opcion) {
                    $opcion = trim($opcion);
                    if (!empty($opcion)) {
                        $stmtOpt->execute(['pid' => $pregunta_id, 'txt' => $opcion]);
                    }
                }
            }
            
            $pdo->commit();
            $msg = "Pregunta agregada correctamente.";
        } catch (botException $e) {
            $pdo->rollBack();
            $msg = "Error: " . $e->getMessage();
        }
    }
}

// Obtener preguntas existentes
$stmtQ = $pdo->prepare("SELECT * FROM preguntas WHERE encuesta_id = :id ORDER BY pregunta_id ASC");
$stmtQ->execute(['id' => $encuesta_id]);
$preguntas = $stmtQ->fetchAll();

?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Editar Encuesta - <?php echo htmlspecialchars($encuesta['titulo']); ?></title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="assets/css/style.css">
    <link rel="stylesheet" href="assets/css/dashboard.css">
</head>
<body>
    <div class="dashboard-layout">
        <?php include 'includes/sidebar.php'; ?>

        <main class="main-content">
            <div class="top-bar">
                <h1 class="page-title">Editando: <?php echo htmlspecialchars($encuesta['titulo']); ?></h1>
                <div>
                     <!-- Botón de publicar o volver -->
                     <?php if ($encuesta['estado_encuesta'] === 'borrador'): ?>
                        <a href="publicar_encuesta.php?id=<?php echo $encuesta_id; ?>" class="btn btn-primary" style="background-color: #059669;">Publicar Encuesta</a>
                     <?php else: ?>
                        <span class="badge" style="padding: 0.5rem; background: #dbf4ff; color: #004a77; border-radius: 4px;">Publicada</span>
                     <?php endif; ?>
                </div>
            </div>

            <div class="content-wrapper">
                <?php if ($msg): ?>
                    <div class="alert alert-success"><?php echo htmlspecialchars($msg); ?></div>
                <?php endif; ?>

                <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 2rem; align-items: start;">
                    
                    <!-- Columna Izquierda: Lista de Preguntas -->
                    <div class="questions-list">
                        <h2 style="font-size: 1.1rem; margin-bottom: 1rem;">Preguntas de la encuesta</h2>
                        
                        <?php if (count($preguntas) === 0): ?>
                            <div class="card" style="text-align: center; color: var(--text-muted);">
                                <p>No hay preguntas aún. Agrega la primera desde el panel derecho.</p>
                            </div>
                        <?php endif; ?>

                        <?php foreach ($preguntas as $idx => $preg): ?>
                            <div class="card" style="margin-bottom: 1rem;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                    <strong><?php echo ($idx + 1) . '. ' . htmlspecialchars($preg['texto_pregunta']); ?></strong>
                                    <span style="font-size: 0.75rem; background: #eee; padding: 2px 6px; border-radius: 4px;">
                                        <?php echo str_replace('_', ' ', $preg['tipo_pregunta']); ?>
                                    </span>
                                </div>

                                <?php
                                // Si es de opciones, mostrarlas
                                if (in_array($preg['tipo_pregunta'], ['opcion_unica', 'opcion_multiple'])) {
                                    $stmtO = $pdo->prepare("SELECT * FROM opciones_respuesta WHERE pregunta_id = :pid");
                                    $stmtO->execute(['pid' => $preg['pregunta_id']]);
                                    $opciones = $stmtO->fetchAll();
                                    
                                    echo '<ul style="list-style: disc; margin-left: 1.5rem; color: var(--text-muted); font-size: 0.9rem;">';
                                    foreach ($opciones as $op) {
                                        echo '<li>' . htmlspecialchars($op['texto_opcion']) . '</li>';
                                    }
                                    echo '</ul>';
                                }
                                ?>
                                <div style="margin-top: 1rem; text-align: right;">
                                    <!-- Aquí iría botón eliminar -->
                                    <a href="eliminar_pregunta.php?id=<?php echo $preg['pregunta_id']; ?>&eid=<?php echo $encuesta_id; ?>" class="btn btn-outline" style="font-size: 0.75rem; padding: 0.25rem 0.5rem; color: #ef4444; border-color: #fecaca;">Eliminar</a>
                                </div>
                            </div>
                        <?php endforeach; ?>
                    </div>

                    <!-- Columna Derecha: Formulario Agregar -->
                    <div class="add-question-panel">
                        <div class="card" style="position: sticky; top: 1rem;">
                            <h2 style="font-size: 1.1rem; margin-bottom: 1rem;">Agregar Pregunta</h2>
                            <form method="POST" action="">
                                <input type="hidden" name="action" value="add_question">
                                
                                <div class="form-group">
                                    <label class="form-label">Texto de la Pregunta</label>
                                    <input type="text" name="texto_pregunta" class="form-control" required>
                                </div>

                                <div class="form-group">
                                    <label class="form-label">Tipo de Respuesta</label>
                                    <select name="tipo_pregunta" id="tipo_pregunta" class="form-control">
                                        <option value="opcion_unica">Opción Única (Radio)</option>
                                        <option value="opcion_multiple">Opción Múltiple (Checkbox)</option>
                                        <option value="texto_libre">Texto Libre</option>
                                        <option value="escala">Escala (1-5)</option>
                                    </select>
                                </div>

                                <div id="options-container" style="display: none; background: #f9fafb; padding: 1rem; border-radius: var(--radius); margin-bottom: 1rem;">
                                    <label class="form-label" style="font-size: 0.875rem;">Opciones de Respuesta</label>
                                    <div id="options-list"></div>
                                    <button type="button" id="btn-add-option" class="btn btn-outline" style="width: 100%; margin-top: 0.5rem; border-style: dashed;">+ Agregar Opción</button>
                                </div>

                                <button type="submit" class="btn btn-primary" style="width: 100%;">Agregar Pregunta</button>
                            </form>
                        </div>
                    </div>

                </div>
            </div>
        </main>
    </div>
    <script src="assets/js/survey-editor.js"></script>
</body>
</html>
