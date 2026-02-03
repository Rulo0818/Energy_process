<?php
$current_page = basename($_SERVER['PHP_SELF']);
?>
<aside class="sidebar">
    <div class="sidebar-header">
        <span class="sidebar-brand">VotaAdmin</span>
    </div>
    <ul class="sidebar-nav">
        <li class="nav-item">
            <a href="dashboard.php" class="nav-link <?php echo $current_page === 'dashboard.php' ? 'active' : ''; ?>">
                <span class="nav-icon"></span> Panel Principal
            </a>
        </li>
        <li class="nav-item">
            <a href="crear_encuesta.php" class="nav-link <?php echo $current_page === 'crear_encuesta.php' || $current_page === 'editar_encuesta.php' ? 'active' : ''; ?>">
                <span class="nav-icon"></span> Crear Encuesta
            </a>
        </li>
        <li class="nav-item">
            <a href="lista_encuestas.php" class="nav-link <?php echo $current_page === 'lista_encuestas.php' ? 'active' : ''; ?>">
                <span class="nav-icon"></span> Mis Encuestas
            </a>
        </li>
        <li class="nav-item">
            <a href="resultados.php" class="nav-link <?php echo $current_page === 'resultados.php' ? 'active' : ''; ?>">
                <span class="nav-icon"></span> Resultados
            </a>
        </li>
        <?php if ($_SESSION['rol'] === 'admin'): ?>
        <li class="nav-item">
            <a href="usuarios.php" class="nav-link <?php echo $current_page === 'usuarios.php' ? 'active' : ''; ?>">
                <span class="nav-icon"></span> Usuarios
            </a>
        </li>
        <?php endif; ?>
    </ul>
    <div class="user-profile">
        <div class="user-avatar">
            <?php echo strtoupper(substr($_SESSION['usuario_nombre'] ?? 'U', 0, 1)); ?>
        </div>
        <div class="user-info">
            <div class="user-name"><?php echo htmlspecialchars($_SESSION['usuario_nombre'] ?? 'Usuario'); ?></div>
            <div class="user-role"><?php echo ucfirst($_SESSION['rol'] === 'encuestador' ? 'Gestor' : $_SESSION['rol']); ?></div>
            <a href="logout.php" style="font-size: 0.75rem; color: #ef4444;">Cerrar Sesión</a>
        </div>
    </div>
</aside>
