<?php
require_once 'config/db.php';

if (!isset($_GET['id'])) {
    die("Encuesta no especificada.");
}

$id = $_GET['id'];

// Obtener encuesta
$stmt = $pdo->prepare("SELECT * FROM encuestas WHERE encuesta_id = :id AND estado_encuesta = 'activa'");
$stmt->execute(['id' => $id]);
$encuesta = $stmt->fetch();

if (!$encuesta) {
    die("Esta encuesta no existe o no está activa.");
}

// Obtener preguntas
$stmtQ = $pdo->prepare("SELECT * FROM preguntas WHERE encuesta_id = :id ORDER BY pregunta_id ASC");
$stmtQ->execute(['id' => $id]);
$preguntas = $stmtQ->fetchAll();
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo htmlspecialchars($encuesta['titulo']); ?></title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body style="background-color: #f3f4f6; padding: 2rem 1rem;">
    <div style="max-width: 800px; margin: 0 auto; background: white; padding: 2rem; border-radius: 1rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
        <header style="text-align: center; margin-bottom: 2rem; border-bottom: 1px solid #e5e7eb; padding-bottom: 1rem;">
            <h1 style="color: var(--primary-color); margin-bottom: 0.5rem;"><?php echo htmlspecialchars($encuesta['titulo']); ?></h1>
            <p style="color: var(--text-muted);"><?php echo nl2br(htmlspecialchars($encuesta['descripcion'])); ?></p>
        </header>

        <form action="procesar_voto.php" method="POST">
            <input type="hidden" name="encuesta_id" value="<?php echo $id; ?>">

            <!-- Datos Demográficos (Participante) -->
            <div style="background: #f9fafb; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem;">
                <h3 style="font-size: 1rem; margin-bottom: 1rem;">Datos Generales</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div class="form-group">
                        <label class="form-label">Edad</label>
                        <input type="number" name="edad" class="form-control" required min="5" max="100">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Género</label>
                        <select name="genero" class="form-control" required>
                            <option value="">Seleccione...</option>
                            <option value="masculino">Masculino</option>
                            <option value="femenino">Femenino</option>
                            <option value="otro">Otro</option>
                        </select>
                    </div>
                </div>
            </div>

            <div class="questions-container">
                <?php foreach ($preguntas as $index => $preg): ?>
                    <div class="question-card" style="margin-bottom: 2rem;">
                        <h3 style="font-size: 1.1rem; margin-bottom: 1rem;">
                            <?php echo ($index + 1) . '. ' . htmlspecialchars($preg['texto_pregunta']); ?>
                        </h3>

                        <?php 
                        if (in_array($preg['tipo_pregunta'], ['opcion_unica', 'opcion_multiple'])) {
                            $stmtO = $pdo->prepare("SELECT * FROM opciones_respuesta WHERE pregunta_id = :pid");
                            $stmtO->execute(['pid' => $preg['pregunta_id']]);
                            $opciones = $stmtO->fetchAll();
                        }
                        ?>

                        <!-- Renderizado según tipo -->
                        <?php if ($preg['tipo_pregunta'] === 'opcion_unica'): ?>
                            <?php foreach ($opciones as $op): ?>
                                <label style="display: flex; align-items: center; margin-bottom: 0.5rem; cursor: pointer;">
                                    <input type="radio" name="respuestas[<?php echo $preg['pregunta_id']; ?>]" value="<?php echo $op['opcion_id']; ?>" required style="margin-right: 0.5rem;">
                                    <?php echo htmlspecialchars($op['texto_opcion']); ?>
                                </label>
                            <?php endforeach; ?>

                        <?php elseif ($preg['tipo_pregunta'] === 'opcion_multiple'): ?>
                             <?php foreach ($opciones as $op): ?>
                                <label style="display: flex; align-items: center; margin-bottom: 0.5rem; cursor: pointer;">
                                    <input type="checkbox" name="respuestas[<?php echo $preg['pregunta_id']; ?>][]" value="<?php echo $op['opcion_id']; ?>" style="margin-right: 0.5rem;">
                                    <?php echo htmlspecialchars($op['texto_opcion']); ?>
                                </label>
                            <?php endforeach; ?>

                        <?php elseif ($preg['tipo_pregunta'] === 'texto_libre'): ?>
                            <textarea name="respuestas[<?php echo $preg['pregunta_id']; ?>]" class="form-control" rows="3"></textarea>

                        <?php elseif ($preg['tipo_pregunta'] === 'escala'): ?>
                            <div style="display: flex; justify-content: space-between; max-width: 300px;">
                                <?php for($i=1; $i<=5; $i++): ?>
                                    <label style="text-align: center; cursor: pointer;">
                                        <div style="font-weight: bold; margin-bottom: 0.25rem;"><?php echo $i; ?></div>
                                        <input type="radio" name="respuestas[<?php echo $preg['pregunta_id']; ?>]" value="<?php echo $i; ?>" required>
                                    </label>
                                <?php endfor; ?>
                            </div>
                        <?php endif; ?>
                    </div>
                <?php endforeach; ?>
            </div>

            <button type="submit" class="btn btn-primary" style="width: 100%; padding: 1rem; font-size: 1.1rem;">Enviar Respuestas</button>
        </form>
    </div>
</body>
</html>
