<?php
require_once 'includes/auth_check.php';
require_once 'config/db.php';

if (isset($_GET['id']) && isset($_GET['eid'])) {
    $pregunta_id = $_GET['id'];
    $encuesta_id = $_GET['eid'];

    try {
        // En un caso real, verificar que la encuesta pertenezca al usuario aquí.
        // DELETE CASCADA manual si no está en BD (aunque MySQL lo soporta si está configurado, aquí lo hacemos manual por seguridad)
        
        $pdo->beginTransaction();

        $stmt = $pdo->prepare("DELETE FROM opciones_respuesta WHERE pregunta_id = :pid");
        $stmt->execute(['pid' => $pregunta_id]);

        $stmt = $pdo->prepare("DELETE FROM preguntas WHERE pregunta_id = :pid");
        $stmt->execute(['pid' => $pregunta_id]);

        $pdo->commit();
    } catch (Exception $e) {
        $pdo->rollBack();
    }
    
    header("Location: editar_encuesta.php?id=" . $encuesta_id);
    exit;
} else {
    header("Location: dashboard.php");
}
?>
