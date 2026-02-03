<?php
require_once 'config/db.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $encuesta_id = $_POST['encuesta_id'];
    $edad = $_POST['edad'];
    $genero = $_POST['genero'];
    $respuestas = $_POST['respuestas'] ?? [];

    try {
        $pdo->beginTransaction();

        // 1. Crear Participante (Anónimo, usuario_id NULL)
        $stmtP = $pdo->prepare("INSERT INTO participantes (usuario_id, edad, genero) VALUES (NULL, :edad, :genero)");
        $stmtP->execute(['edad' => $edad, 'genero' => $genero]);
        $participante_id = $pdo->lastInsertId();

        // 2. Guardar Respuestas
        $sqlR = "INSERT INTO respuestas (participante_id, pregunta_id, opcion_id, respuesta_texto) VALUES (:pid, :qid, :oid, :txt)";
        $stmtR = $pdo->prepare($sqlR);

        foreach ($respuestas as $pregunta_id => $valor) {
            // Caso 1: Checkbox (Array)
            if (is_array($valor)) {
                foreach ($valor as $opcion_id) {
                    $stmtR->execute([
                        'pid' => $participante_id,
                        'qid' => $pregunta_id,
                        'oid' => $opcion_id,
                        'txt' => NULL
                    ]);
                }
            } 
            // Caso 2: Texto o Única
            else {
                // Verificar si es numérico (Opción ID o Escala?)
                // Si es escala (1-5), guarda en respuesta_texto o opcion_id?
                // Tabla respuestas: opcion_id (FK), respuesta_texto
                // Si la pregunta es tipo 'escala', guardamos el valor en respuesta_texto, porque no hay ID de opción asociado a '1', '2'... a menos que creemos opciones.
                // Pero mi editor de escala NO crea opciones en DB.
                
                // Consultar tipo de pregunta
                $stmtType = $pdo->prepare("SELECT tipo_pregunta FROM preguntas WHERE pregunta_id = :qid");
                $stmtType->execute(['qid' => $pregunta_id]);
                $tipo = $stmtType->fetchColumn();

                if ($tipo === 'texto_libre' || $tipo === 'escala') {
                     $stmtR->execute([
                        'pid' => $participante_id,
                        'qid' => $pregunta_id,
                        'oid' => NULL,
                        'txt' => $valor // Texto o número de escala
                    ]);
                } else {
                    // Es opcion_unica
                    $stmtR->execute([
                        'pid' => $participante_id,
                        'qid' => $pregunta_id,
                        'oid' => $valor,
                        'txt' => NULL
                    ]);
                }
            }
        }

        $pdo->commit();
        
        // Redirigir a página de gracias
        echo "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Gracias</title><link rel='stylesheet' href='assets/css/style.css'></head><body style='display:flex;justify-content:center;align-items:center;height:100vh;background:#f3f4f6;'><div class='card' style='text-align:center;'><h1>¡Gracias por tu participación!</h1><p>Tus respuestas han sido registradas.</p></div></body></html>";
        exit;

    } catch (Exception $e) {
        $pdo->rollBack();
        die("Error al procesar: " . $e->getMessage());
    }
} else {
    header("Location: index.php");
}
?>
