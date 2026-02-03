<?php
require_once 'includes/auth_check.php';
require_once 'config/db.php';

if (isset($_GET['id'])) {
    $encuesta_id = $_GET['id'];

    // Validaciones extra: Verificar que tenga preguntas antes de publicar (Spec 5.2.1)
    $stmtQ = $pdo->prepare("SELECT COUNT(*) FROM preguntas WHERE encuesta_id = :id");
    $stmtQ->execute(['id' => $encuesta_id]);
    $count = $stmtQ->fetchColumn();

    if ($count > 0) {
        $stmt = $pdo->prepare("UPDATE encuestas SET estado_encuesta = 'activa' WHERE encuesta_id = :id");
        $stmt->execute(['id' => $encuesta_id]);
        
        // Redirigir a una página de éxito o lista con el link generado
        // Por simplicidad, vamos a lista_encuestas (que crearemos) o dashboard
        // Pero el usuario querrá ver el link. Vamos a una vista de "Detalle/Link"
        // O simplemente volvemos al dashboard con un mensaje.
        header("Location: lista_encuestas.php?msg=publicada");
    } else {
        // No tiene preguntas
        header("Location: editar_encuesta.php?id=$encuesta_id&error=nopreguntas");
    }
    exit;
}
?>
