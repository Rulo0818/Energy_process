<?php
require_once 'config/db.php';
session_start();

echo "<h1>Diagnóstico de DB</h1>";
echo "<h2>Sesión Actual</h2>";
var_dump($_SESSION);

echo "<h2>Usuarios</h2>";
$stmt = $pdo->query("SELECT * FROM usuarios");
echo "<table border=1><tr><th>ID</th><th>Nombre</th><th>Email</th><th>Rol</th></tr>";
while ($row = $stmt->fetch()) {
    echo "<tr><td>{$row['usuario_id']}</td><td>{$row['nombre']}</td><td>{$row['correo_electronico']}</td><td>{$row['rol']}</td></tr>";
}
echo "</table>";

echo "<h2>Encuestas</h2>";
$stmt = $pdo->query("SELECT * FROM encuestas");
echo "<table border=1><tr><th>ID</th><th>Titulo</th><th>Creador ID</th><th>Estado</th></tr>";
while ($row = $stmt->fetch()) {
    echo "<tr><td>{$row['encuesta_id']}</td><td>{$row['titulo']}</td><td>{$row['creador_usuario_id']}</td><td>{$row['estado_encuesta']}</td></tr>";
}
echo "</table>";
?>
