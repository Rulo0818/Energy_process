<?php
require_once 'includes/auth_check.php';
require_once 'config/db.php';

// Obtener estadísticas rápidas
$stats = [
    'total_encuestas' => 0,
    'encuestas_activas' => 0,
    'total_respuestas' => 0
];

try {
    $stmt = $pdo->query("SELECT COUNT(*) FROM encuestas");
    $stats['total_encuestas'] = $stmt->fetchColumn();

    $stmt = $pdo->query("SELECT COUNT(*) FROM encuestas WHERE estado_encuesta = 'activa'");
    $stats['encuestas_activas'] = $stmt->fetchColumn();

    $stmt = $pdo->query("SELECT COUNT(*) FROM respuestas");
    $stats['total_respuestas'] = $stmt->fetchColumn();

} catch (PDOException $e) {
    // Silencio en producción
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Panel de Administración - Vota</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="assets/css/style.css">
    <link rel="stylesheet" href="assets/css/dashboard.css">
</head>
<body>
    <div class="dashboard-layout">
        <?php include 'includes/sidebar.php'; ?>

        <main class="main-content">
            <div class="top-bar">
                <h1 class="page-title">Panel Principal</h1>
                <div class="date-display"><?php echo date('d/m/Y'); ?></div>
            </div>

            <div class="content-wrapper">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-title">Total Encuestas</div>
                        <div class="stat-value"><?php echo $stats['total_encuestas']; ?></div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-title">Encuestas Activas</div>
                        <div class="stat-value" style="color: var(--primary-color);"><?php echo $stats['encuestas_activas']; ?></div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-title">Total Respuestas</div>
                        <div class="stat-value"><?php echo $stats['total_respuestas']; ?></div>
                    </div>
                </div>

                <div class="card">
                    <h2 style="margin-bottom: 1rem; font-size: 1.1rem;">Bienvenido al Sistema de Gestión de Encuestas</h2>
                    <p style="color: var(--text-muted); margin-bottom: 1.5rem;">
                        Desde aquí puedes administrar todo el ciclo de vida de tus encuestas. 
                        Comienza creando una nueva encuesta o revisando los resultados de las existentes.
                    </p>
                    <a href="crear_encuesta.php" class="btn btn-primary">Crear Nueva Encuesta</a>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
