<?php
session_start();
require_once 'config/db.php';

if (!isset($_SESSION['usuario_id']) || $_SESSION['rol'] !== 'participante') {
    header("Location: index.php");
    exit;
}

$stmt = $pdo->query("SELECT * FROM encuestas WHERE estado_encuesta = 'activa' ORDER BY fecha_creacion DESC");
$encuestas = $stmt->fetchAll();
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Participante - Vota&opina</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="assets/css/style.css">
    <style>
        .portal-header {
            background: white;
            padding: 1rem 2rem;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .survey-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
    </style>
</head>
<body>
    <header class="portal-header">
        <div style="font-weight: 700; font-size: 1.25rem; color: var(--primary-color);">Vota & Opina</div>
        <div style="display: flex; align-items: center; gap: 1rem;">
            <span>Hola, <?php echo htmlspecialchars($_SESSION['usuario_nombre']); ?></span>
            <a href="logout.php" class="btn btn-outline" style="font-size: 0.8rem; color: #ef4444;">Cerrar Sesión</a>
        </div>
    </header>

    <main>
        <div class="survey-grid">
            <?php if (count($encuestas) === 0): ?>
                <div class="card" style="grid-column: 1 / -1; text-align: center;">
                    <h3>No hay encuestas activas en este momento.</h3>
                </div>
            <?php else: ?>
                <?php foreach ($encuestas as $enc): ?>
                    <div class="card">
                        <h3 style="font-size: 1.1rem; margin-bottom: 0.5rem;"><?php echo htmlspecialchars($enc['titulo']); ?></h3>
                        <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1rem; flex-grow: 1;">
                            <?php echo htmlspecialchars(substr($enc['descripcion'], 0, 100)) . (strlen($enc['descripcion']) > 100 ? '...' : ''); ?>
                        </p>
                        <div style="margin-top: auto;">
                            <a href="votar.php?id=<?php echo $enc['encuesta_id']; ?>" class="btn btn-primary" style="width: 100%;">Participar</a>
                        </div>
                    </div>
                <?php endforeach; ?>
            <?php endif; ?>
        </div>
    </main>
</body>
</html>
