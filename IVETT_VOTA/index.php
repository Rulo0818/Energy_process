<?php
session_start();
require_once 'config/db.php';

if (isset($_SESSION['usuario_id']) && in_array($_SESSION['rol'], ['admin', 'encuestador'])) {
    header("Location: dashboard.php");
    exit;
}

$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $usuario = trim($_POST['usuario']);
    $password = $_POST['password'];

    if (empty($usuario) || empty($password)) {
        $error = "Por favor ingrese todos los campos.";
    } else {
        try {
            $stmt = $pdo->prepare("SELECT * FROM usuarios WHERE correo_electronico = :usuario LIMIT 1");
            $stmt->execute(['usuario' => $usuario]);
            $user = $stmt->fetch();

            $auth = false;
            if ($user) {
                if (password_verify($password, $user['contrasena'])) {
                    $auth = true;
                } elseif ($password === $user['contrasena']) {
                    $auth = true;
                }
            }

            if ($auth) {
                if ($user['estado_usuario'] === 'activo') {
                    $_SESSION['usuario_id'] = $user['usuario_id'];
                    $_SESSION['usuario_nombre'] = $user['nombre'];
                    $_SESSION['rol'] = $user['rol'];

                    if ($user['rol'] === 'participante') {
                        header("Location: portal_participante.php");
                    } else {
                        header("Location: dashboard.php");
                    }
                    exit;
                } else {
                    $error = "Su cuenta está inactiva.";
                }
            } else {
                $error = "Usuario o contraseña incorrectos.";
            }
        } catch (PDOException $e) {
            $error = "Error de conexión: " . $e->getMessage();
        }
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Iniciar Sesión - Vota Sistema</title>
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <link rel="stylesheet" href="assets/css/style.css">
    <link rel="stylesheet" href="assets/css/auth.css">
</head>
<body>
    <div class="auth-wrapper">
        <div class="auth-card">
            <div class="auth-header">
                <h1>Vota & Opina</h1>
                <p>Ingrese sus datos para continuar</p>
            </div>

            <?php if ($error): ?>
                <div class="alert alert-danger"><?php echo htmlspecialchars($error); ?></div>
            <?php endif; ?>

            <form method="POST" action="">
                <div class="form-group">
                    <label for="usuario" class="form-label">Usuario</label>
                    <input type="text" id="usuario" name="usuario" class="form-control" placeholder="Ej: admin" value="<?php echo isset($_POST['usuario']) ? htmlspecialchars($_POST['usuario']) : ''; ?>" required>
                </div>
                <div class="form-group">
                    <label for="password" class="form-label">Contraseña</label>
                    <input type="password" id="password" name="password" class="form-control" placeholder="••••••••" required>
                </div>
                
                <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 1rem;">Iniciar Sesión</button>
            </form>

            <div class="auth-footer">
                <p>&copy; <?php echo date('Y'); ?> Sistema de Votación</p>
            </div>
        </div>
    </div>
</body>
</html>
