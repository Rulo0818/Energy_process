-- phpMyAdmin SQL Dump
-- version 4.7.9
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 25-01-2026 a las 01:19:02
-- Versión del servidor: 10.1.31-MariaDB
-- Versión de PHP: 7.2.3

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";

SET AUTOCOMMIT = 0;

START TRANSACTION;

SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */
;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */
;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */
;
/*!40101 SET NAMES utf8mb4 */
;

--
-- Base de datos: `vota_y_opina`
--
CREATE DATABASE IF NOT EXISTS `vota_y_opina` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

USE `vota_y_opina`;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estados`
--

CREATE TABLE IF NOT EXISTS `estados` (
    `id_estado` int(11) NOT NULL AUTO_INCREMENT,
    `nombre` varchar(100) NOT NULL,
    PRIMARY KEY (`id_estado`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `municipios`
--

CREATE TABLE IF NOT EXISTS `municipios` (
    `id_municipio` int(11) NOT NULL AUTO_INCREMENT,
    `nombre` varchar(100) NOT NULL,
    `id_estado` int(11) NOT NULL,
    PRIMARY KEY (`id_municipio`),
    KEY `id_estado` (`id_estado`),
    CONSTRAINT `municipios_ibfk_1` FOREIGN KEY (`id_estado`) REFERENCES `estados` (`id_estado`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `secciones`
--

CREATE TABLE IF NOT EXISTS `secciones` (
    `id_seccion` int(11) NOT NULL AUTO_INCREMENT,
    `nombre_seccion` varchar(100) NOT NULL,
    `id_municipio` int(11) NOT NULL,
    PRIMARY KEY (`id_seccion`),
    KEY `id_municipio` (`id_municipio`),
    CONSTRAINT `secciones_ibfk_1` FOREIGN KEY (`id_municipio`) REFERENCES `municipios` (`id_municipio`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE IF NOT EXISTS `usuarios` (
    `usuario_id` int(11) NOT NULL AUTO_INCREMENT,
    `nombre_usuario` varchar(50) NOT NULL UNIQUE,
    `nombre` varchar(100) NOT NULL,
    `apellido` varchar(100) NOT NULL,
    `correo_electronico` varchar(150) NOT NULL,
    `telefono` varchar(20) DEFAULT NULL,
    `fecha_nacimiento` date DEFAULT NULL,
    `contrasena` varchar(255) NOT NULL,
    `rol` enum(
        'admin',
        'encuestador',
        'participante',
        'cliente'
    ) NOT NULL,
    `fecha_registro` datetime DEFAULT CURRENT_TIMESTAMP,
    `estado_usuario` enum('activo', 'inactivo') DEFAULT 'activo',
    `id_estado` int(11) DEFAULT NULL,
    `id_municipio` int(11) DEFAULT NULL,
    `id_seccion` int(11) DEFAULT NULL,
    PRIMARY KEY (`usuario_id`),
    UNIQUE KEY `correo_electronico` (`correo_electronico`),
    KEY `id_estado` (`id_estado`),
    KEY `id_municipio` (`id_municipio`),
    KEY `id_seccion` (`id_seccion`),
    CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`id_estado`) REFERENCES `estados` (`id_estado`),
    CONSTRAINT `usuarios_ibfk_2` FOREIGN KEY (`id_municipio`) REFERENCES `municipios` (`id_municipio`),
    CONSTRAINT `usuarios_ibfk_3` FOREIGN KEY (`id_seccion`) REFERENCES `secciones` (`id_seccion`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clientes`
--

CREATE TABLE IF NOT EXISTS `clientes` (
    `cliente_id` int(11) NOT NULL AUTO_INCREMENT,
    `nombre_organizacion` varchar(150) NOT NULL,
    `contacto_correo` varchar(150) DEFAULT NULL,
    `telefono` varchar(20) DEFAULT NULL,
    `direccion` varchar(255) DEFAULT NULL,
    PRIMARY KEY (`cliente_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `encuestas`
--

CREATE TABLE IF NOT EXISTS `encuestas` (
    `encuesta_id` int(11) NOT NULL AUTO_INCREMENT,
    `cliente_id` int(11) DEFAULT NULL,
    `creador_usuario_id` int(11) NOT NULL,
    `titulo` varchar(200) NOT NULL,
    `descripcion` text,
    `fecha_creacion` datetime DEFAULT CURRENT_TIMESTAMP,
    `fecha_inicio` date DEFAULT NULL,
    `fecha_fin` date DEFAULT NULL,
    `estado_encuesta` enum(
        'borrador',
        'activa',
        'cerrada'
    ) DEFAULT 'borrador',
    PRIMARY KEY (`encuesta_id`),
    KEY `cliente_id` (`cliente_id`),
    KEY `creador_usuario_id` (`creador_usuario_id`),
    CONSTRAINT `encuestas_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`cliente_id`),
    CONSTRAINT `encuestas_ibfk_2` FOREIGN KEY (`creador_usuario_id`) REFERENCES `usuarios` (`usuario_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `preguntas`
--

CREATE TABLE IF NOT EXISTS `preguntas` (
    `pregunta_id` int(11) NOT NULL AUTO_INCREMENT,
    `encuesta_id` int(11) NOT NULL,
    `texto_pregunta` text NOT NULL,
    `tipo_pregunta` enum(
        'opcion_unica',
        'opcion_multiple',
        'texto_libre',
        'escala'
    ) NOT NULL,
    PRIMARY KEY (`pregunta_id`),
    KEY `encuesta_id` (`encuesta_id`),
    CONSTRAINT `preguntas_ibfk_1` FOREIGN KEY (`encuesta_id`) REFERENCES `encuestas` (`encuesta_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `opciones_respuesta`
--

CREATE TABLE IF NOT EXISTS `opciones_respuesta` (
    `opcion_id` int(11) NOT NULL AUTO_INCREMENT,
    `pregunta_id` int(11) NOT NULL,
    `texto_opcion` varchar(255) NOT NULL,
    PRIMARY KEY (`opcion_id`),
    KEY `pregunta_id` (`pregunta_id`),
    CONSTRAINT `opciones_respuesta_ibfk_1` FOREIGN KEY (`pregunta_id`) REFERENCES `preguntas` (`pregunta_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `participantes`
--

CREATE TABLE IF NOT EXISTS `participantes` (
    `participante_id` int(11) NOT NULL AUTO_INCREMENT,
    `usuario_id` int(11) DEFAULT NULL,
    `edad` int(11) DEFAULT NULL,
    `genero` enum(
        'masculino',
        'femenino',
        'otro'
    ) DEFAULT NULL,
    `fecha_registro` datetime DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`participante_id`),
    KEY `usuario_id` (`usuario_id`),
    CONSTRAINT `participantes_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`usuario_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `respuestas`
--

CREATE TABLE IF NOT EXISTS `respuestas` (
    `respuesta_id` int(11) NOT NULL AUTO_INCREMENT,
    `participante_id` int(11) NOT NULL,
    `pregunta_id` int(11) NOT NULL,
    `opcion_id` int(11) DEFAULT NULL,
    `respuesta_texto` text,
    `fecha_respuesta` datetime DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`respuesta_id`),
    KEY `participante_id` (`participante_id`),
    KEY `pregunta_id` (`pregunta_id`),
    KEY `opcion_id` (`opcion_id`),
    CONSTRAINT `respuestas_ibfk_1` FOREIGN KEY (`participante_id`) REFERENCES `participantes` (`participante_id`),
    CONSTRAINT `respuestas_ibfk_2` FOREIGN KEY (`pregunta_id`) REFERENCES `preguntas` (`pregunta_id`),
    CONSTRAINT `respuestas_ibfk_3` FOREIGN KEY (`opcion_id`) REFERENCES `opciones_respuesta` (`opcion_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `informes`
--

CREATE TABLE IF NOT EXISTS `informes` (
    `informe_id` int(11) NOT NULL AUTO_INCREMENT,
    `encuesta_id` int(11) NOT NULL,
    `fecha_generacion` datetime DEFAULT CURRENT_TIMESTAMP,
    `tipo_reporte` varchar(100) DEFAULT NULL,
    `datos_json` text,
    PRIMARY KEY (`informe_id`),
    KEY `encuesta_id` (`encuesta_id`),
    CONSTRAINT `informes_ibfk_1` FOREIGN KEY (`encuesta_id`) REFERENCES `encuestas` (`encuesta_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- Insert Seed Admin User (password: admin123)
-- Hash generated via password_hash('admin123', PASSWORD_BCRYPT)
INSERT INTO
    `usuarios` (
        `nombre_usuario`,
        `nombre`,
        `apellido`,
        `correo_electronico`,
        `contrasena`,
        `rol`,
        `estado_usuario`
    )
VALUES (
        'admin',
        'Admin',
        'System',
        'admin@vota.com',
        '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
        'admin',
        'activo'
    );