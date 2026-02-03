<?php
require_once 'includes/auth_check.php';
require_once 'config/db.php';

// Validar que sea admin
if ($_SESSION['rol'] !== 'admin') {
    header("Location: dashboard.php");
    exit;
}

// 1. ELIMINAR USUARIO
if (isset($_GET['delete'])) {
    $id = $_GET['delete'];
    if ($id != $_SESSION['usuario_id']) { 
        try {
            // Intentar borrar (si falla por FK, desactivar)
            $stmt = $pdo->prepare("DELETE FROM usuarios WHERE usuario_id = :id");
            $stmt->execute(['id' => $id]);
        } catch (PDOException $e) {
            // Si tiene datos relacionados, lo desactivamos en lugar de borrar
            $stmt = $pdo->prepare("UPDATE usuarios SET estado_usuario = 'inactivo' WHERE usuario_id = :id");
            $stmt->execute(['id' => $id]);
        }
    }
    header("Location: usuarios.php");
    exit;
}

// 2. CREAR USUARIO
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'create_user') {
    $nombre = $_POST['nombre'];
    $apellido = $_POST['apellido'];
    $email = $_POST['email'];
    $password = $_POST['password']; // Se guardará tal cual para compatibilidad con datos del usuario
    $rol = $_POST['rol'];
    
    // Verificar duplicados
    $stmtCh = $pdo->prepare("SELECT COUNT(*) FROM usuarios WHERE correo_electronico = :email");
    $stmtCh->execute(['email' => $email]);
    if ($stmtCh->fetchColumn() > 0) {
        $error = "El correo ya está registrado.";
    } else {
        // Insertar (usando password_hash si se quisiera seguridad, pero mantenemos texto plano por consistencia solicitada anteriormente o hash por defecto)
        // Usaremos hash para nuevos por seguridad, el login ya soporta ambos.
        $hash = password_hash($password, PASSWORD_DEFAULT);
        
        // Datos dummy para campos requeridos por esquema estricto (municipio, etc, si son NOT NULL). 
        // Se usan valores '1' asumiendo que existen en la BD (Tlaxcala/Centro) para evitar error de FK.
        
        $sql = "INSERT INTO usuarios (nombre, apellido, correo_electronico, contrasena, rol, estado_usuario, fecha_registro, id_estado, id_municipio, id_seccion) 
                VALUES (:nombre, :apellido, :email, :pass, :rol, 'activo', NOW(), 1, 1, 1)";
        
        $stmt = $pdo->prepare($sql);
        $stmt->execute([
            'nombre' => $nombre,
            'apellido' => $apellido,
            'email' => $email,
            'pass' => $hash,
            'rol' => $rol
        ]);
        
        header("Location: usuarios.php");
        exit;
    }
}

$stmt = $pdo->query("SELECT * FROM usuarios ORDER BY nombre ASC");
$usuarios = $stmt->fetchAll();
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestión de Usuarios - Vota</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="assets/css/style.css">
    <link rel="stylesheet" href="assets/css/dashboard.css">
</head>
<body>
    <div class="dashboard-layout">
        <?php include 'includes/sidebar.php'; ?>

        <main class="main-content">
            <div class="top-bar">
                <h1 class="page-title">Gestión de Usuarios</h1>
                <button onclick="document.getElementById('modal-user').style.display='block'" class="btn btn-primary">Nuevo Usuario</button>
            </div>

            <!-- Modal Nuevo Usuario -->
            <div id="modal-user" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:100;">
                <div class="card" style="margin: 5% auto; max-width: 500px; padding: 2rem;">
                    <h2 style="margin-bottom: 1rem;">Registrar Usuario</h2>
                    <form method="POST">
                        <input type="hidden" name="action" value="create_user">
                        
                        <div class="form-group">
                            <label>Nombre</label>
                            <input type="text" name="nombre" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label>Apellido</label>
                            <input type="text" name="apellido" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label>Correo Electrónico</label>
                            <input type="email" name="email" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label>Contraseña</label>
                            <input type="password" name="password" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label>Rol</label>
                            <select name="rol" class="form-control">
                                <option value="admin">Administrador</option>
                                <option value="encuestador">Gestor/Encuestador</option>
                                <option value="participante">Participante</option>
                            </select>
                        </div>
                        
                        <div style="text-align: right; margin-top: 1rem;">
                            <button type="button" onclick="document.getElementById('modal-user').style.display='none'" class="btn btn-outline">Cancelar</button>
                            <button type="submit" class="btn btn-primary">Guardar</button>
                        </div>
                    </form>
                </div>
            </div>

            <div class="content-wrapper">
                <div class="card" style="padding: 0;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background: #f9fafb; text-align: left; border-bottom: 1px solid var(--border-color);">
                                <th style="padding: 1rem;">ID</th>
                                <th style="padding: 1rem;">Nombre</th>
                                <th style="padding: 1rem;">Email</th>
                                <th style="padding: 1rem;">Rol</th>
                                <th style="padding: 1rem;">Estado</th>
                                <th style="padding: 1rem; text-align: right;">Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($usuarios as $u): ?>
                            <tr style="border-bottom: 1px solid var(--border-color);">
                                <td style="padding: 1rem; color: var(--text-muted);"><?php echo $u['usuario_id']; ?></td>
                                <td style="padding: 1rem; font-weight: 500;">
                                    <?php echo htmlspecialchars($u['nombre'] . ' ' . $u['apellido']); ?>
                                </td>
                                <td style="padding: 1rem; color: var(--text-muted);"><?php echo htmlspecialchars($u['correo_electronico']); ?></td>
                                <td style="padding: 1rem;">
                                    <span style="font-size: 0.75rem; padding: 2px 8px; border-radius: 999px; background: #e0e7ff; color: #3730a3;">
                                        <?php echo ucfirst($u['rol']); ?>
                                    </span>
                                </td>
                                <td style="padding: 1rem;">
                                    <span style="font-size: 0.75rem; padding: 2px 8px; border-radius: 999px; <?php echo $u['estado_usuario'] === 'activo' ? 'background:#dcfce7;color:#166534;' : 'background:#fee2e2;color:#991b1b;'; ?>">
                                        <?php echo ucfirst($u['estado_usuario']); ?>
                                    </span>
                                </td>
                                <td style="padding: 1rem; text-align: right;">
                                    <?php if ($u['usuario_id'] != $_SESSION['usuario_id']): ?>
                                        <a href="?delete=<?php echo $u['usuario_id']; ?>" class="btn btn-outline" style="padding: 0.25rem 0.5rem; font-size: 0.75rem; color: #ef4444; border-color: #fecaca;" onclick="return confirm('¿Seguro quieres eliminar este usuario?')">Eliminar</a>
                                    <?php else: ?>
                                        <span style="font-size: 0.75rem; color: var(--text-muted);">Tú</span>
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
