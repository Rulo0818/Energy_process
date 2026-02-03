<?php
require_once 'includes/auth_check.php';
require_once 'config/db.php';

// Selección basada en Rol
$sql = "SELECT e.*, u.nombre as creador FROM encuestas e JOIN usuarios u ON e.creador_usuario_id = u.usuario_id";

if ($_SESSION['rol'] !== 'admin') {
    // Si no es admin, solo ve las suyas
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
    <title>Mis Encuestas - Vota</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="assets/css/style.css">
    <link rel="stylesheet" href="assets/css/dashboard.css">
</head>
<body>
    <div class="dashboard-layout">
        <?php include 'includes/sidebar.php'; ?>

        <main class="main-content">
            <div class="top-bar">
                <h1 class="page-title">Mis Encuestas</h1>
                <a href="crear_encuesta.php" class="btn btn-primary">Nueva Encuesta</a>
            </div>

            <div class="content-wrapper">
                <div class="card" style="padding: 0;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background: #f9fafb; text-align: left; border-bottom: 1px solid var(--border-color);">
                                <th style="padding: 1rem;">ID</th>
                                <th style="padding: 1rem;">Título</th>
                                <th style="padding: 1rem;">Estado</th>
                                <th style="padding: 1rem;">Fechas</th>
                                <th style="padding: 1rem; text-align: right;">Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($encuestas as $enc): ?>
                            <tr style="border-bottom: 1px solid var(--border-color);">
                                <td style="padding: 1rem; color: var(--text-muted);">#<?php echo $enc['encuesta_id']; ?></td>
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
                                    <?php if ($enc['estado_encuesta'] === 'borrador'): ?>
                                        <a href="editar_encuesta.php?id=<?php echo $enc['encuesta_id']; ?>" class="btn btn-outline" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;">Editar</a>
                                    <?php elseif ($enc['estado_encuesta'] === 'activa'): ?>
                                        <a href="votar.php?id=<?php echo $enc['encuesta_id']; ?>" target="_blank" class="btn btn-outline" style="padding: 0.25rem 0.5rem; font-size: 0.75rem; border-color: var(--primary-color); color: var(--primary-color);">Ver Link</a>
                                        <a href="resultados.php?id=<?php echo $enc['encuesta_id']; ?>" class="btn btn-outline" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;">Resultados</a>
                                    <?php else: ?>
                                        <a href="resultados.php?id=<?php echo $enc['encuesta_id']; ?>" class="btn btn-outline" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;">Ver Resultados</a>
                                    <?php endif; ?>
                                </td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
