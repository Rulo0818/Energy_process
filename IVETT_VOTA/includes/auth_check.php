<?php
session_start();

if (!isset($_SESSION['usuario_id']) || !in_array($_SESSION['rol'], ['admin', 'encuestador'])) {
    // Si no está logueado o no es rol permitido
    header("Location: index.php");
    exit;
}
?>
