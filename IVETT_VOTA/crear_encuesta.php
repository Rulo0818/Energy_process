<?php
require_once 'includes/auth_check.php';
require_once 'config/db.php';

$error = '';
$success = '';

// Obtener clientes para el selector
$stmtC = $pdo->query("SELECT * FROM clientes ORDER BY nombre_organizacion ASC");
$clientes = $stmtC->fetchAll();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $titulo = trim($_POST['titulo']);
    $descripcion = trim($_POST['descripcion']);
    $fecha_inicio = $_POST['fecha_inicio'];
    $fecha_fin = $_POST['fecha_fin'];
    $cliente_id = $_POST['cliente_id'];

    if (empty($titulo) || empty($fecha_inicio) || empty($fecha_fin) || empty($cliente_id)) {
        $error = "Por favor complete los campos obligatorios.";
    } elseif ($fecha_inicio > $fecha_fin) {
        $error = "La fecha de inicio no puede ser posterior a la fecha de fin.";
    } else {
        try {
            $sql = "INSERT INTO encuestas (creador_usuario_id, cliente_id, titulo, descripcion, fecha_inicio, fecha_fin, estado_encuesta) 
                    VALUES (:uid, :cid, :titulo, :desc, :inicio, :fin, 'borrador')";
            $stmt = $pdo->prepare($sql);
            $stmt->execute([
                'uid' => $_SESSION['usuario_id'],
                'cid' => $cliente_id,
                'titulo' => $titulo,
                'desc' => $descripcion,
                'inicio' => $fecha_inicio,
                'fin' => $fecha_fin
            ]);

            $id_encuesta = $pdo->lastInsertId();
            header("Location: editar_encuesta.php?id=" . $id_encuesta);
            exit;

        } catch (PDOException $e) {
            $error = "Error al guardar: " . $e->getMessage();
        }
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crear Encuesta - Vota</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="assets/css/style.css">
    <link rel="stylesheet" href="assets/css/dashboard.css">
</head>
<body>
    <div class="dashboard-layout">
        <?php include 'includes/sidebar.php'; ?>

        <main class="main-content">
            <div class="top-bar">
                <h1 class="page-title">Crear Nueva Encuesta</h1>
            </div>

            <div class="content-wrapper">
                <div class="card" style="max-width: 800px; margin: 0 auto;">
                    <?php if ($error): ?>
                        <div class="alert alert-danger"><?php echo htmlspecialchars($error); ?></div>
                    <?php endif; ?>

                    <form method="POST" action="">
                        <div class="form-group">
                            <label for="titulo" class="form-label">Título de la Encuesta *</label>
                            <input type="text" id="titulo" name="titulo" class="form-control" placeholder="Ej: Satisfacción de Clientes 2026" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="cliente_id" class="form-label">Cliente / Organización *</label>
                            <select id="cliente_id" name="cliente_id" class="form-control" required>
                                <option value="">Seleccione un cliente...</option>
                                <?php foreach ($clientes as $cli): ?>
                                    <option value="<?php echo $cli['cliente_id']; ?>"><?php echo htmlspecialchars($cli['nombre_organizacion']); ?></option>
                                <?php endforeach; ?>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="descripcion" class="form-label">Descripción</label>
                            <textarea id="descripcion" name="descripcion" class="form-control" rows="4" placeholder="Breve descripción del objetivo de la encuesta..."></textarea>
                        </div>

                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                            <div class="form-group">
                                <label for="fecha_inicio" class="form-label">Fecha Inicio *</label>
                                <input type="date" id="fecha_inicio" name="fecha_inicio" class="form-control" required>
                            </div>
                            <div class="form-group">
                                <label for="fecha_fin" class="form-label">Fecha Fin *</label>
                                <input type="date" id="fecha_fin" name="fecha_fin" class="form-control" required>
                            </div>
                        </div>

                        <div style="margin-top: 1.5rem; text-align: right;">
                            <a href="dashboard.php" class="btn btn-outline" style="margin-right: 0.5rem;">Cancelar</a>
                            <button type="submit" class="btn btn-primary">Guardar y Agregar Preguntas</button>
                        </div>
                    </form>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
