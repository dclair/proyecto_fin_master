/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.11.14-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: aficionados_network_db
-- ------------------------------------------------------
-- Server version	10.11.14-MariaDB-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `aficionados_network_contactmessage`
--

DROP TABLE IF EXISTS `aficionados_network_contactmessage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `aficionados_network_contactmessage` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(254) NOT NULL,
  `subject` varchar(200) NOT NULL,
  `message` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `read` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aficionados_network_contactmessage`
--

LOCK TABLES `aficionados_network_contactmessage` WRITE;
/*!40000 ALTER TABLE `aficionados_network_contactmessage` DISABLE KEYS */;
INSERT INTO `aficionados_network_contactmessage` VALUES
(5,'José Manuel Declara Lanzas','jmdclair@gmail.com','nuevo prueba de email','DEFAULT_FROM_EMAIL = os.getenv(\"EMAIL_USER\")','2026-01-18 18:04:06.019000',0),
(6,'José Manuel Declara Lanzas','jmdclair@gmail.com','nuevo prueba 333  de email','# Añade esto temporalmente debajo de load_dotenv()\r\nprint(f\"--- DEBUG: EMAIL_USER es {os.getenv(\'EMAIL_USER\')} ---\")','2026-01-18 18:25:34.385000',1),
(7,'YO-JOSE MANUEL','0y1informatica@gmail.com','nuevo prueba formulario de contacto','Formulario de Contacto\r\nRellena los campos y te responderemos lo antes posible.','2026-01-22 21:27:43.988000',1),
(8,'YO-JOSE MANUEL','0y1informatica@gmail.com','asunto de prueba desde formulario  de contacto','¡Esa plantilla es perfecta! Tiene un diseño limpio, moderno y los colores corporativos bien integrados. Usarla para todo (Quedadas y Contacto) es la decisión correcta para que Hubs&Clicks tenga esa \"visión de empresa\" que buscamos.\r\n\r\nAquí tienes cómo queda la integración definitiva en tu vista de contacto, asegurándonos de que los nombres de las variables coincidan exactamente con tu plantilla (recipient_name, message_body, action_url).\r\n\r\n🛠️ Integración en ContactFormView\r\nCopia este bloque en tu archivo views.py. He ajustado el message_body para que, cuando recibas el correo, veas todos los datos del remitente de forma clara.\r\n\r\nPython\r\n# general/views.py\r\nfrom django.core.mail import EmailMultiAlternatives\r\nfrom django.template.loader import render_to_string\r\nfrom django.utils.html import strip_tags\r\nfrom email.mime.image import MIMEImage\r\nimport os\r\n\r\n# ... dentro de tu clase ContactFormView ...\r\n\r\n    def form_valid(self, form):\r\n        contact_message = form.save()\r\n\r\n        # 1. Definimos los datos para la plantilla\r\n        subject = f\"📬 Nuevo mensaje: {contact_message.subject}\"\r\n        recipient_email = settings.CONTACT_EMAIL\r\n        \r\n        # El cuerpo del mensaje que irá dentro de {{ message_body }}\r\n        full_message = (\r\n            f\"Has recibido un nuevo mensaje de contacto a través de la web.\\n\\n\"\r\n            f\"👤 Nombre: {contact_message.name}\\n\"\r\n            f\"📧 Email: {contact_message.email}\\n\"\r\n            f\"📝 Mensaje:\\n{contact_message.message}\"\r\n        )\r\n\r\n        context = {\r\n            \"recipient_name\": \"Equipo de Hubs&Clicks\", # Quién recibe el mail (tú)\r\n            \"message_body\": full_message,\r\n            \"action_url\": self.request.build_absolute_uri(\'/admin/\'), # Link al panel\r\n        }\r\n\r\n        # 2. Renderizamos el HTML\r\n        html_content = render_to_string(\"emails/notification_email.html\", context)\r\n        text_content = strip_tags(html_content)\r\n\r\n        # 3. Creamos el objeto Email\r\n        email = EmailMultiAlternatives(\r\n            subject,\r\n            text_content,\r\n            settings.DEFAULT_FROM_EMAIL,\r\n            [recipient_email],\r\n        )\r\n        email.attach_alternative(html_content, \"text/html\")\r\n\r\n        # 4. Incrustamos el logo usando el ID exacto de tu plantilla: logo_hubs\r\n        logo_path = os.path.join(settings.BASE_DIR, \"static\", \"img\", \"logo_hubs.png\")\r\n        if os.path.exists(logo_path):\r\n            with open(logo_path, \"rb\") as f:\r\n                logo_image = MIMEImage(f.read())\r\n                logo_image.add_header(\"Content-ID\", \"<logo_hubs>\")\r\n                email.attach(logo_image)\r\n\r\n        # 5. Enviar\r\n        email.send(fail_silently=False)\r\n\r\n        messages.success(self.request, \"Gracias por tu mensaje. Nos pondremos en contacto pronto.\")\r\n        return super().form_valid(form)\r\n🧐 Detalles a tener en cuenta para el éxito total\r\nVariables de la Plantilla: He respetado escrupulosamente tus nombres: recipient_name, message_body y action_url.\r\n\r\nEl Botón: En este caso, el botón \"Ver en la web\" te llevará directamente al administrador de Django (/admin/) para que puedas gestionar los mensajes cómodamente.\r\n\r\nIdentidad: Al usar cid:logo_hubs en la plantilla y <logo_hubs> en el código Python, el logo aparecerá automáticamente en la cabecera azul, justo como lo diseñaste.\r\n\r\n🚀 Prueba de fuego\r\nUna vez guardes esto:\r\n\r\nEnvía un mensaje desde tu formulario de contacto.\r\n\r\nSi estás en modo consola (EMAIL_BACKEND en settings), verás todo el código HTML generado en tu terminal.\r\n\r\nSi estás con SMTP real, abre tu bandeja de entrada. Deberías ver el correo con el borde redondeado, el fondo azul en la cabecera y el logo de Hubs&Clicks presidiendo el mensaje.','2026-01-25 16:53:34.413000',1),
(9,'Jose Manuel','boss@gmail.com','asunto','mensaje es este','2026-06-10 10:41:34.998051',1),
(10,'Jose Manuel','jmdclair@gmail.com','asunto de prueba','mensaje de prueba con adjuntos','2026-06-10 10:58:44.101850',1),
(11,'Jose Manuel','jmdclair@gmail.com','asunto de prueba','mensaje de prueba con adjuntos','2026-06-10 11:00:35.660011',1),
(12,'Jose Manuel','jmdclair@gmail.com','asunto de pruebas','mansaje de pruebas con adjuntos','2026-06-10 11:02:29.857799',1),
(13,'Jose Manuel','jmdclair@gmail.com','asunto de pruebas','pruebas con adjuntos','2026-06-10 11:06:55.798261',1),
(14,'Jose Manuel','jmdclair@gmail.com','asunto de prueba','mensaje de prueba','2026-06-10 12:32:01.253403',1),
(15,'Jose Manuel','jmdclair@gmail.com','asunto de prueba','Es un mensaje de prueba','2026-06-10 12:38:37.696320',0),
(16,'Jose Manuel','jmdclair@gmail.com','asunto de prueba','mensaje de prueba','2026-06-10 12:44:36.556565',0),
(17,'Jose Manuel','jmdclair@gmail.com','pruebas','pruebas','2026-06-10 12:48:20.813725',0);
/*!40000 ALTER TABLE `aficionados_network_contactmessage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
INSERT INTO `auth_group` VALUES
(1,'ADMINISTRADORES');
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=89 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
INSERT INTO `auth_group_permissions` VALUES
(1,1,1),
(2,1,2),
(3,1,3),
(4,1,4),
(5,1,5),
(6,1,6),
(7,1,7),
(8,1,8),
(9,1,9),
(10,1,10),
(11,1,11),
(12,1,12),
(13,1,13),
(14,1,14),
(15,1,15),
(16,1,16),
(17,1,17),
(18,1,18),
(19,1,19),
(20,1,20),
(21,1,21),
(22,1,22),
(23,1,23),
(24,1,24),
(25,1,25),
(26,1,26),
(27,1,27),
(28,1,28),
(29,1,29),
(30,1,30),
(31,1,31),
(32,1,32),
(33,1,33),
(34,1,34),
(35,1,35),
(36,1,36),
(37,1,37),
(38,1,38),
(39,1,39),
(40,1,40),
(41,1,41),
(42,1,42),
(43,1,43),
(44,1,44),
(45,1,45),
(46,1,46),
(47,1,47),
(48,1,48),
(49,1,49),
(50,1,50),
(51,1,51),
(52,1,52),
(53,1,53),
(54,1,54),
(55,1,55),
(56,1,56),
(57,1,57),
(58,1,58),
(59,1,59),
(60,1,60),
(61,1,61),
(62,1,62),
(63,1,63),
(64,1,64),
(65,1,65),
(66,1,66),
(67,1,67),
(68,1,68),
(69,1,69),
(70,1,70),
(71,1,71),
(72,1,72),
(73,1,73),
(74,1,74),
(75,1,75),
(76,1,76),
(77,1,77),
(78,1,78),
(79,1,79),
(80,1,80),
(81,1,81),
(82,1,82),
(83,1,83),
(84,1,84),
(85,1,85),
(86,1,86),
(87,1,87),
(88,1,88);
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=125 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES
(1,'Can add log entry',1,'add_logentry'),
(2,'Can change log entry',1,'change_logentry'),
(3,'Can delete log entry',1,'delete_logentry'),
(4,'Can view log entry',1,'view_logentry'),
(5,'Can add permission',3,'add_permission'),
(6,'Can change permission',3,'change_permission'),
(7,'Can delete permission',3,'delete_permission'),
(8,'Can view permission',3,'view_permission'),
(9,'Can add group',2,'add_group'),
(10,'Can change group',2,'change_group'),
(11,'Can delete group',2,'delete_group'),
(12,'Can view group',2,'view_group'),
(13,'Can add user',4,'add_user'),
(14,'Can change user',4,'change_user'),
(15,'Can delete user',4,'delete_user'),
(16,'Can view user',4,'view_user'),
(17,'Can add content type',5,'add_contenttype'),
(18,'Can change content type',5,'change_contenttype'),
(19,'Can delete content type',5,'delete_contenttype'),
(20,'Can view content type',5,'view_contenttype'),
(21,'Can add session',6,'add_session'),
(22,'Can change session',6,'change_session'),
(23,'Can delete session',6,'delete_session'),
(24,'Can view session',6,'view_session'),
(25,'Can add site',7,'add_site'),
(26,'Can change site',7,'change_site'),
(27,'Can delete site',7,'delete_site'),
(28,'Can view site',7,'view_site'),
(29,'Can add flat page',8,'add_flatpage'),
(30,'Can change flat page',8,'change_flatpage'),
(31,'Can delete flat page',8,'delete_flatpage'),
(32,'Can view flat page',8,'view_flatpage'),
(33,'Can add Post',12,'add_posts'),
(34,'Can change Post',12,'change_posts'),
(35,'Can delete Post',12,'delete_posts'),
(36,'Can view Post',12,'view_posts'),
(37,'Can add Comentario',9,'add_comment'),
(38,'Can change Comentario',9,'change_comment'),
(39,'Can delete Comentario',9,'delete_comment'),
(40,'Can view Comentario',9,'view_comment'),
(41,'Can add Quedada',10,'add_event'),
(42,'Can change Quedada',10,'change_event'),
(43,'Can delete Quedada',10,'delete_event'),
(44,'Can view Quedada',10,'view_event'),
(45,'Can add event comment',11,'add_eventcomment'),
(46,'Can change event comment',11,'change_eventcomment'),
(47,'Can delete event comment',11,'delete_eventcomment'),
(48,'Can view event comment',11,'view_eventcomment'),
(49,'Can add hobby',14,'add_hobby'),
(50,'Can change hobby',14,'change_hobby'),
(51,'Can delete hobby',14,'delete_hobby'),
(52,'Can view hobby',14,'view_hobby'),
(53,'Can add Perfil de Usuario',17,'add_userprofile'),
(54,'Can change Perfil de Usuario',17,'change_userprofile'),
(55,'Can delete Perfil de Usuario',17,'delete_userprofile'),
(56,'Can view Perfil de Usuario',17,'view_userprofile'),
(57,'Can add user hobby',16,'add_userhobby'),
(58,'Can change user hobby',16,'change_userhobby'),
(59,'Can delete user hobby',16,'delete_userhobby'),
(60,'Can view user hobby',16,'view_userhobby'),
(61,'Can add follow',13,'add_follow'),
(62,'Can change follow',13,'change_follow'),
(63,'Can delete follow',13,'delete_follow'),
(64,'Can view follow',13,'view_follow'),
(65,'Can add review',15,'add_review'),
(66,'Can change review',15,'change_review'),
(67,'Can delete review',15,'delete_review'),
(68,'Can view review',15,'view_review'),
(69,'Can add Mensaje de Contacto',18,'add_contactmessage'),
(70,'Can change Mensaje de Contacto',18,'change_contactmessage'),
(71,'Can delete Mensaje de Contacto',18,'delete_contactmessage'),
(72,'Can view Mensaje de Contacto',18,'view_contactmessage'),
(73,'Can add notification',19,'add_notification'),
(74,'Can change notification',19,'change_notification'),
(75,'Can delete notification',19,'delete_notification'),
(76,'Can view notification',19,'view_notification'),
(77,'Can add message',22,'add_message'),
(78,'Can change message',22,'change_message'),
(79,'Can delete message',22,'delete_message'),
(80,'Can view message',22,'view_message'),
(81,'Can add conversation',20,'add_conversation'),
(82,'Can change conversation',20,'change_conversation'),
(83,'Can delete conversation',20,'delete_conversation'),
(84,'Can view conversation',20,'view_conversation'),
(85,'Can add conversation participant',21,'add_conversationparticipant'),
(86,'Can change conversation participant',21,'change_conversationparticipant'),
(87,'Can delete conversation participant',21,'delete_conversationparticipant'),
(88,'Can view conversation participant',21,'view_conversationparticipant'),
(89,'Can add group join request',23,'add_groupjoinrequest'),
(90,'Can change group join request',23,'change_groupjoinrequest'),
(91,'Can delete group join request',23,'delete_groupjoinrequest'),
(92,'Can view group join request',23,'view_groupjoinrequest'),
(93,'Can add asistencia a evento',24,'add_eventattendance'),
(94,'Can change asistencia a evento',24,'change_eventattendance'),
(95,'Can delete asistencia a evento',24,'delete_eventattendance'),
(96,'Can view asistencia a evento',24,'view_eventattendance'),
(97,'Can add valoración de vendedor',26,'add_sellerreview'),
(98,'Can change valoración de vendedor',26,'change_sellerreview'),
(99,'Can delete valoración de vendedor',26,'delete_sellerreview'),
(100,'Can view valoración de vendedor',26,'view_sellerreview'),
(101,'Can add anuncio',25,'add_listing'),
(102,'Can change anuncio',25,'change_listing'),
(103,'Can delete anuncio',25,'delete_listing'),
(104,'Can view anuncio',25,'view_listing'),
(105,'Can add medalla de usuario',28,'add_userbadge'),
(106,'Can change medalla de usuario',28,'change_userbadge'),
(107,'Can delete medalla de usuario',28,'delete_userbadge'),
(108,'Can view medalla de usuario',28,'view_userbadge'),
(109,'Can add medalla',27,'add_badge'),
(110,'Can change medalla',27,'change_badge'),
(111,'Can delete medalla',27,'delete_badge'),
(112,'Can view medalla',27,'view_badge'),
(113,'Can add artículo/caso de estudio',29,'add_article'),
(114,'Can change artículo/caso de estudio',29,'change_article'),
(115,'Can delete artículo/caso de estudio',29,'delete_article'),
(116,'Can view artículo/caso de estudio',29,'view_article'),
(117,'Can add comentario',30,'add_articlecomment'),
(118,'Can change comentario',30,'change_articlecomment'),
(119,'Can delete comentario',30,'delete_articlecomment'),
(120,'Can view comentario',30,'view_articlecomment'),
(121,'Can add valoración',31,'add_articlerating'),
(122,'Can change valoración',31,'change_articlerating'),
(123,'Can delete valoración',31,'delete_articlerating'),
(124,'Can view valoración',31,'view_articlerating');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `auth_user_email_1c89df09_uniq` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES
(1,'pbkdf2_sha256$1200000$RDM3M6P6QeqfqnWFRVHTEs$nGvvgw80sH4PYbmWqqnw0kUqfYMFwhK03Fz20OX4QnA=','2026-06-18 10:23:45.771637',1,'root','','','0y1informatica@gmail.com',1,1,'2026-01-17 18:01:41.000000'),
(2,'pbkdf2_sha256$1200000$eQ96zoP7M533RgQUgJQNfd$j++M/HjEyE1A6yj3ag/STitCRNYKNR4PRTek1elY5vk=','2026-06-17 10:08:58.450032',1,'admin','','','jmdclair@gmail.com',1,1,'2026-01-17 19:11:55.000000'),
(3,'pbkdf2_sha256$1200000$DUKwyYU1BjE2eSVpqKxzXE$BIkbQXfukblRy6M+eglJHW0ml4skm/tc8I6XkC4k9D4=','2026-06-15 10:16:36.307837',0,'Juan','','','jose@gmail.com',0,1,'2026-01-18 09:59:26.000000'),
(4,'pbkdf2_sha256$1200000$514hZhObg1YARK8ZOmvDq1$SafqulaXt9eg6kVAb2keuRwD7x7sza2znUP8sx6U/Fw=','2026-06-07 18:44:30.987675',0,'pepe','pepe','pepinillo','pepe@gmail.com',0,1,'2026-01-18 10:14:08.000000');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
INSERT INTO `auth_user_groups` VALUES
(2,1,1),
(1,2,1);
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chat_conversation`
--

DROP TABLE IF EXISTS `chat_conversation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `chat_conversation` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `is_group` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `admin_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `chat_conversation_admin_id_24935e6c_fk_auth_user_id` (`admin_id`),
  CONSTRAINT `chat_conversation_admin_id_24935e6c_fk_auth_user_id` FOREIGN KEY (`admin_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chat_conversation`
--

LOCK TABLES `chat_conversation` WRITE;
/*!40000 ALTER TABLE `chat_conversation` DISABLE KEYS */;
/*!40000 ALTER TABLE `chat_conversation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chat_conversationparticipant`
--

DROP TABLE IF EXISTS `chat_conversationparticipant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `chat_conversationparticipant` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `joined_at` datetime(6) NOT NULL,
  `last_read_timestamp` datetime(6) NOT NULL,
  `conversation_id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `chat_conversationpartici_conversation_id_user_id_79a6b8c0_uniq` (`conversation_id`,`user_id`),
  KEY `chat_conversationparticipant_user_id_534d53ea_fk_auth_user_id` (`user_id`),
  CONSTRAINT `chat_conversationpar_conversation_id_8a6499f0_fk_chat_conv` FOREIGN KEY (`conversation_id`) REFERENCES `chat_conversation` (`id`),
  CONSTRAINT `chat_conversationparticipant_user_id_534d53ea_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chat_conversationparticipant`
--

LOCK TABLES `chat_conversationparticipant` WRITE;
/*!40000 ALTER TABLE `chat_conversationparticipant` DISABLE KEYS */;
/*!40000 ALTER TABLE `chat_conversationparticipant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chat_groupjoinrequest`
--

DROP TABLE IF EXISTS `chat_groupjoinrequest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `chat_groupjoinrequest` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `status` varchar(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `conversation_id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `chat_groupjoinrequest_conversation_id_user_id_b99c6ba7_uniq` (`conversation_id`,`user_id`),
  KEY `chat_groupjoinrequest_user_id_5b2293fc_fk_auth_user_id` (`user_id`),
  CONSTRAINT `chat_groupjoinreques_conversation_id_8e8eae61_fk_chat_conv` FOREIGN KEY (`conversation_id`) REFERENCES `chat_conversation` (`id`),
  CONSTRAINT `chat_groupjoinrequest_user_id_5b2293fc_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chat_groupjoinrequest`
--

LOCK TABLES `chat_groupjoinrequest` WRITE;
/*!40000 ALTER TABLE `chat_groupjoinrequest` DISABLE KEYS */;
/*!40000 ALTER TABLE `chat_groupjoinrequest` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chat_message`
--

DROP TABLE IF EXISTS `chat_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `chat_message` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `content` longtext DEFAULT NULL,
  `timestamp` datetime(6) NOT NULL,
  `conversation_id` bigint(20) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `attachment` varchar(100) DEFAULT NULL,
  `attachment_type` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `chat_message_conversation_id_a1207bf4_fk_chat_conversation_id` (`conversation_id`),
  KEY `chat_message_sender_id_991c686c_fk_auth_user_id` (`sender_id`),
  CONSTRAINT `chat_message_conversation_id_a1207bf4_fk_chat_conversation_id` FOREIGN KEY (`conversation_id`) REFERENCES `chat_conversation` (`id`),
  CONSTRAINT `chat_message_sender_id_991c686c_fk_auth_user_id` FOREIGN KEY (`sender_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chat_message`
--

LOCK TABLES `chat_message` WRITE;
/*!40000 ALTER TABLE `chat_message` DISABLE KEYS */;
/*!40000 ALTER TABLE `chat_message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chat_message_hidden_by`
--

DROP TABLE IF EXISTS `chat_message_hidden_by`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `chat_message_hidden_by` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `message_id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `chat_message_hidden_by_message_id_user_id_4b232329_uniq` (`message_id`,`user_id`),
  KEY `chat_message_hidden_by_user_id_08baf273_fk_auth_user_id` (`user_id`),
  CONSTRAINT `chat_message_hidden_by_message_id_13c18950_fk_chat_message_id` FOREIGN KEY (`message_id`) REFERENCES `chat_message` (`id`),
  CONSTRAINT `chat_message_hidden_by_user_id_08baf273_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chat_message_hidden_by`
--

LOCK TABLES `chat_message_hidden_by` WRITE;
/*!40000 ALTER TABLE `chat_message_hidden_by` DISABLE KEYS */;
/*!40000 ALTER TABLE `chat_message_hidden_by` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=115 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES
(1,'2026-01-18 09:43:10.346000','2','Perfil de admin',1,'[{\"added\": {}}]',17,1),
(2,'2026-01-18 09:59:27.176000','3','Juan',1,'[{\"added\": {}}]',4,1),
(3,'2026-01-18 09:59:51.998000','3','Juan',2,'[{\"changed\": {\"fields\": [\"First name\", \"Last name\", \"Email address\", \"Last login\"]}}]',4,1),
(4,'2026-01-18 10:02:54.237000','3','Perfil de Juan',2,'[{\"changed\": {\"fields\": [\"Biograf\\u00eda\", \"Fecha de nacimiento\", \"Ubicaci\\u00f3n\", \"Sitio web\"]}}]',17,1),
(5,'2026-01-18 18:03:28.640000','3','Leanne Graham - asunto de prueba desde formulario  de contacto',3,'',18,1),
(6,'2026-01-18 18:03:28.640000','2','Leanne Graham - asunto de prueba desde formulario  de contacto',3,'',18,1),
(7,'2026-01-18 18:03:28.640000','1','Leanne Graham - asunto de prueba desde formulario  de contacto',3,'',18,1),
(8,'2026-01-18 18:27:16.538000','6','José Manuel Declara Lanzas - nuevo prueba 333  de email',2,'[{\"changed\": {\"fields\": [\"Le\\u00eddo\"]}}]',18,1),
(9,'2026-01-18 18:46:57.646000','3','Perfil de pepe sigue a Perfil de root',3,'',13,1),
(10,'2026-01-18 18:46:57.646000','1','Perfil de pepe sigue a Perfil de Juan',3,'',13,1),
(11,'2026-01-18 19:15:46.210000','1','Hubs&Clicks',2,'[{\"changed\": {\"fields\": [\"Domain name\", \"Display name\"]}}]',7,1),
(12,'2026-01-18 19:20:34.623000','1','/legal/ -- Aviso Legal',1,'[{\"added\": {}}]',8,1),
(13,'2026-01-18 19:39:38.553000','1','/legal/ -- Aviso Legal',2,'[{\"changed\": {\"fields\": [\"Content\"]}}]',8,1),
(14,'2026-01-18 19:40:52.656000','1','/legal/ -- Aviso Legal',2,'[{\"changed\": {\"fields\": [\"Content\"]}}]',8,1),
(15,'2026-01-18 19:42:14.168000','1','/legal/ -- Aviso Legal',2,'[{\"changed\": {\"fields\": [\"Content\"]}}]',8,1),
(16,'2026-01-18 19:43:18.813000','1','/legal/ -- Aviso Legal',2,'[{\"changed\": {\"fields\": [\"Content\"]}}]',8,1),
(17,'2026-01-18 19:45:32.070000','1','/legal/ -- Aviso Legal',2,'[{\"changed\": {\"fields\": [\"Content\"]}}]',8,1),
(18,'2026-01-18 19:57:43.199000','2','/cookies/ -- Política de Cookies',1,'[{\"added\": {}}]',8,1),
(19,'2026-01-18 20:42:22.326000','1','Juan -> root (Me gusta)',1,'[{\"added\": {}}]',19,1),
(20,'2026-01-18 21:13:28.687000','2','admin -> root (Comentario)',1,'[{\"added\": {}}]',19,1),
(21,'2026-01-20 17:50:31.174000','3','root -> Juan (Comentario)',1,'[{\"added\": {}}]',19,1),
(22,'2026-01-20 17:50:55.843000','4','pepe -> Juan (Seguimiento)',1,'[{\"added\": {}}]',19,1),
(23,'2026-01-22 21:28:24.209000','9','pepe -> root (Seguimiento)',3,'',19,1),
(24,'2026-01-22 21:28:34.690000','8','root -> pepe (Seguimiento)',3,'',19,1),
(25,'2026-01-22 21:28:34.690000','7','pepe -> Juan (Me gusta)',3,'',19,1),
(26,'2026-01-22 21:28:34.690000','6','root -> Juan (Me gusta)',3,'',19,1),
(27,'2026-01-22 21:28:34.690000','5','root -> Juan (Comentario)',3,'',19,1),
(28,'2026-01-22 21:28:34.690000','4','pepe -> Juan (Seguimiento)',3,'',19,1),
(29,'2026-01-22 21:28:34.690000','3','root -> Juan (Comentario)',3,'',19,1),
(30,'2026-01-22 21:28:34.690000','2','admin -> root (Comentario)',3,'',19,1),
(31,'2026-01-22 21:28:34.690000','1','Juan -> root (Me gusta)',3,'',19,1),
(32,'2026-01-22 21:28:51.739000','7','YO-JOSE MANUEL - nuevo prueba formulario de contacto',2,'[]',18,1),
(33,'2026-01-22 21:28:58.186000','7','YO-JOSE MANUEL - nuevo prueba formulario de contacto',2,'[{\"changed\": {\"fields\": [\"Le\\u00eddo\"]}}]',18,1),
(34,'2026-01-22 21:29:30.756000','7','Perfil de root sigue a Perfil de Juan',3,'',13,1),
(35,'2026-01-24 09:44:38.957000','1','Ajedrez',1,'[{\"added\": {}}]',14,1),
(36,'2026-01-24 09:45:30.516000','2','Senderismo',1,'[{\"added\": {}}]',14,1),
(37,'2026-01-24 09:47:09.893000','3','Fotografía',1,'[{\"added\": {}}]',14,1),
(38,'2026-01-24 10:00:04.886000','1','UserHobby object (1)',1,'[{\"added\": {}}]',16,1),
(39,'2026-01-24 10:00:19.875000','2','UserHobby object (2)',1,'[{\"added\": {}}]',16,1),
(40,'2026-01-24 10:00:31.365000','3','UserHobby object (3)',1,'[{\"added\": {}}]',16,1),
(41,'2026-01-24 10:00:43.932000','4','UserHobby object (4)',1,'[{\"added\": {}}]',16,1),
(42,'2026-01-24 10:01:54.264000','5','UserHobby object (5)',1,'[{\"added\": {}}]',16,1),
(43,'2026-01-24 10:28:28.755000','4','Desarrollo en Django',1,'[{\"added\": {}}]',14,1),
(44,'2026-01-24 10:46:56.613000','5','Publicación de pepe - 18/01/2026',2,'[{\"changed\": {\"fields\": [\"Ubicaci\\u00f3n\", \"Category\"]}}]',12,1),
(45,'2026-01-24 10:47:30.284000','3','Aprendiendo Django - 18/01/2026',2,'[{\"changed\": {\"fields\": [\"T\\u00edtulo\", \"Ubicaci\\u00f3n\", \"Category\"]}}]',12,1),
(46,'2026-01-24 10:49:53.378000','3','Aprendiendo Django - 18/01/2026',2,'[]',12,1),
(47,'2026-01-24 10:50:11.490000','2','Publicación de Juan - 18/01/2026',2,'[{\"changed\": {\"fields\": [\"Ubicaci\\u00f3n\", \"Category\"]}}]',12,1),
(48,'2026-01-24 10:50:57.076000','5','Publicación de pepe - 18/01/2026',2,'[]',12,1),
(49,'2026-01-24 10:53:35.556000','4','Publicación de admin - 18/01/2026',2,'[{\"changed\": {\"fields\": [\"Category\"]}}]',12,1),
(50,'2026-01-24 10:53:51.066000','1','Publicación de root - 17/01/2026',2,'[{\"changed\": {\"fields\": [\"Category\"]}}]',12,1),
(51,'2026-01-24 11:47:01.031000','1','Almorzar - Senderismo',1,'[{\"added\": {}}]',10,1),
(52,'2026-01-24 11:47:11.295000','1','Almorzar - Senderismo',2,'[]',10,1),
(53,'2026-01-24 21:21:49.953000','1','Almorzar - Senderismo',2,'[]',10,1),
(54,'2026-01-24 22:31:40.141000','4','pepe',2,'[{\"changed\": {\"fields\": [\"Email address\"]}}]',4,1),
(55,'2026-01-24 22:32:45.370000','1','root',2,'[{\"changed\": {\"fields\": [\"Email address\"]}}]',4,1),
(56,'2026-01-24 23:11:04.594000','3','Juan',2,'[{\"changed\": {\"fields\": [\"Email address\"]}}]',4,1),
(57,'2026-01-25 13:37:35.781000','4','AJEDREZ - Ajedrez',2,'[{\"changed\": {\"fields\": [\"Fecha y hora del evento\"]}}]',10,1),
(58,'2026-01-29 20:15:18.448000','2','admin',2,'[{\"changed\": {\"fields\": [\"password\"]}}]',4,1),
(59,'2026-01-29 20:20:46.999000','4','Viva la PEPA!!! - 18/01/2026',2,'[{\"changed\": {\"fields\": [\"T\\u00edtulo\", \"Ubicaci\\u00f3n\"]}}]',12,1),
(60,'2026-01-29 20:21:04.577000','1','ROOT es le mejor - 17/01/2026',2,'[{\"changed\": {\"fields\": [\"T\\u00edtulo\", \"Ubicaci\\u00f3n\"]}}]',12,1),
(61,'2026-01-31 09:18:30.767000','3','Juan',2,'[{\"changed\": {\"fields\": [\"Email address\"]}}]',4,1),
(62,'2026-02-01 16:07:36.496000','1','127.0.0.1:8000',2,'[{\"changed\": {\"fields\": [\"Domain name\"]}}]',7,1),
(63,'2026-02-01 16:08:29.400000','5','boss',3,'',4,1),
(64,'2026-02-01 16:10:25.052000','6','boss',3,'',4,1),
(65,'2026-02-01 16:17:06.684000','8','usuario1',3,'',4,1),
(66,'2026-02-01 16:26:05.558000','9','usuario',3,'',4,1),
(67,'2026-02-01 16:45:08.639000','10','usuario',3,'',4,1),
(68,'2026-02-01 16:47:06.081000','11','usuario',3,'',4,1),
(69,'2026-02-01 16:52:38.865000','12','usuario',3,'',4,1),
(70,'2026-02-01 16:58:10.735000','13','usuario',3,'',4,1),
(71,'2026-02-01 17:07:52.040000','14','usuario',3,'',4,1),
(72,'2026-02-01 17:09:26.778000','15','usuario',3,'',4,1),
(73,'2026-02-01 17:15:04.705000','16','usuario',3,'',4,1),
(74,'2026-02-01 17:16:28.433000','17','usuario',3,'',4,1),
(75,'2026-02-15 19:35:00.162000','2','/cookies/ -- Política de Cookies',2,'[]',8,1),
(76,'2026-05-26 11:17:25.716205','8','YO-JOSE MANUEL - asunto de prueba desde formulario  de contacto',2,'[{\"changed\": {\"fields\": [\"Le\\u00eddo\"]}}]',18,1),
(77,'2026-05-26 11:21:57.889282','3','Juan',2,'[{\"changed\": {\"fields\": [\"First name\", \"Last name\"]}}]',4,1),
(78,'2026-06-04 11:37:48.899291','5','Boss',2,'[{\"changed\": {\"fields\": [\"Email address\"]}}]',4,1),
(79,'2026-06-04 11:38:07.585995','2','admin',2,'[{\"changed\": {\"fields\": [\"Email address\"]}}]',4,1),
(80,'2026-06-04 11:38:20.518759','3','Juan',2,'[{\"changed\": {\"fields\": [\"Email address\"]}}]',4,1),
(81,'2026-06-04 11:38:29.598913','4','pepe',2,'[{\"changed\": {\"fields\": [\"Email address\"]}}]',4,1),
(82,'2026-06-04 11:39:02.307762','2','admin',2,'[{\"changed\": {\"fields\": [\"Email address\"]}}]',4,1),
(83,'2026-06-04 11:39:53.426011','2','admin',2,'[{\"changed\": {\"fields\": [\"First name\", \"Last name\"]}}]',4,2),
(84,'2026-06-04 11:40:12.892220','5','Boss',2,'[{\"changed\": {\"fields\": [\"First name\", \"Last name\"]}}]',4,2),
(85,'2026-06-04 11:40:25.602196','4','pepe',2,'[{\"changed\": {\"fields\": [\"First name\", \"Last name\"]}}]',4,2),
(86,'2026-06-04 11:40:42.931670','1','root',2,'[{\"changed\": {\"fields\": [\"First name\", \"Last name\"]}}]',4,2),
(87,'2026-06-04 11:40:53.781801','6','usuario',2,'[{\"changed\": {\"fields\": [\"Last name\"]}}]',4,2),
(88,'2026-06-04 12:20:54.735978','1','ADMINISTRADORES',1,'[{\"added\": {}}]',2,1),
(89,'2026-06-04 12:21:13.324930','2','admin',2,'[{\"changed\": {\"fields\": [\"Groups\"]}}]',4,1),
(90,'2026-06-04 12:21:34.200576','1','root',2,'[{\"changed\": {\"fields\": [\"Groups\"]}}]',4,1),
(91,'2026-06-11 11:13:33.545929','2','/cookies/ -- Política de Cookies',2,'[{\"changed\": {\"fields\": [\"Content\"]}}]',8,2),
(92,'2026-06-11 11:15:03.715365','2','/cookies/ -- Política de Cookies',2,'[{\"changed\": {\"fields\": [\"Content\"]}}]',8,2),
(93,'2026-06-11 11:19:44.419999','2','127.0.0.1/8000',1,'[{\"added\": {}}]',7,2),
(94,'2026-06-11 11:19:51.161021','3','/privacy/ -- Política de Privacidad',1,'[{\"added\": {}}]',8,2),
(95,'2026-06-15 12:46:07.498998','35','Cuellopuntura canaria',2,'[]',14,2),
(96,'2026-06-15 12:47:13.870932','36','Otras terapias',2,'[{\"changed\": {\"fields\": [\"Description\"]}}]',14,2),
(97,'2026-06-16 11:29:39.748833','4','Leanne Graham - asunto de prueba desde formulario  de contacto',3,'',18,1),
(98,'2026-06-16 11:29:50.596084','5','José Manuel Declara Lanzas - nuevo prueba de email',2,'[{\"changed\": {\"fields\": [\"Le\\u00eddo\"]}}]',18,1),
(99,'2026-06-16 11:30:10.348737','9','Jose Manuel - asunto',2,'[{\"changed\": {\"fields\": [\"Le\\u00eddo\"]}}]',18,1),
(100,'2026-06-16 11:30:26.005581','10','Jose Manuel - asunto de prueba',2,'[{\"changed\": {\"fields\": [\"Le\\u00eddo\"]}}]',18,1),
(101,'2026-06-16 11:30:34.008825','11','Jose Manuel - asunto de prueba',2,'[{\"changed\": {\"fields\": [\"Le\\u00eddo\"]}}]',18,1),
(102,'2026-06-16 11:30:36.594446','11','Jose Manuel - asunto de prueba',2,'[]',18,1),
(103,'2026-06-16 11:30:41.779422','11','Jose Manuel - asunto de prueba',2,'[]',18,1),
(104,'2026-06-16 11:30:49.663646','14','Jose Manuel - asunto de prueba',2,'[{\"changed\": {\"fields\": [\"Le\\u00eddo\"]}}]',18,1),
(105,'2026-06-16 11:30:56.037049','14','Jose Manuel - asunto de prueba',2,'[]',18,1),
(106,'2026-06-16 11:31:03.408773','12','Jose Manuel - asunto de pruebas',2,'[{\"changed\": {\"fields\": [\"Le\\u00eddo\"]}}]',18,1),
(107,'2026-06-16 11:31:06.064964','12','Jose Manuel - asunto de pruebas',2,'[]',18,1),
(108,'2026-06-16 11:31:11.864083','13','Jose Manuel - asunto de pruebas',2,'[{\"changed\": {\"fields\": [\"Le\\u00eddo\"]}}]',18,1),
(109,'2026-06-16 11:31:16.947545','5','José Manuel Declara Lanzas - nuevo prueba de email',2,'[{\"changed\": {\"fields\": [\"Le\\u00eddo\"]}}]',18,1),
(110,'2026-06-16 11:45:18.717536','6','usuario',2,'[{\"changed\": {\"fields\": [\"Active\"]}}]',4,1),
(111,'2026-06-16 11:45:32.653870','6','usuario',3,'',4,1),
(112,'2026-06-16 11:45:45.006565','5','Boss',3,'',4,1),
(113,'2026-06-16 12:37:05.849340','8','UsuarioPrueba',2,'[{\"changed\": {\"fields\": [\"Active\"]}}]',4,1),
(114,'2026-06-16 12:41:24.611994','8','UsuarioPrueba',3,'',4,1);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES
(1,'admin','logentry'),
(18,'aficionados_network','contactmessage'),
(2,'auth','group'),
(3,'auth','permission'),
(4,'auth','user'),
(20,'chat','conversation'),
(21,'chat','conversationparticipant'),
(23,'chat','groupjoinrequest'),
(22,'chat','message'),
(5,'contenttypes','contenttype'),
(8,'flatpages','flatpage'),
(27,'gamification','badge'),
(28,'gamification','userbadge'),
(29,'library','article'),
(30,'library','articlecomment'),
(31,'library','articlerating'),
(25,'marketplace','listing'),
(26,'marketplace','sellerreview'),
(19,'notifications','notification'),
(9,'posts','comment'),
(10,'posts','event'),
(24,'posts','eventattendance'),
(11,'posts','eventcomment'),
(12,'posts','posts'),
(13,'profiles','follow'),
(14,'profiles','hobby'),
(15,'profiles','review'),
(16,'profiles','userhobby'),
(17,'profiles','userprofile'),
(6,'sessions','session'),
(7,'sites','site');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_flatpage`
--

DROP TABLE IF EXISTS `django_flatpage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_flatpage` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(100) NOT NULL,
  `title` varchar(200) NOT NULL,
  `content` longtext NOT NULL,
  `enable_comments` tinyint(1) NOT NULL,
  `template_name` varchar(70) NOT NULL,
  `registration_required` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_flatpage_url_41612362` (`url`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_flatpage`
--

LOCK TABLES `django_flatpage` WRITE;
/*!40000 ALTER TABLE `django_flatpage` DISABLE KEYS */;
INSERT INTO `django_flatpage` VALUES
(1,'/legal/','Aviso Legal','\n<p>Hubs&Clicks es una plataforma desarrollada como proyecto académico para facilitar la conexión entre personas con terapias compartidas.</p>\n\n<h3 class=\"h5 mt-4 fw-bold\">Responsable</h3>\n<p>Este sitio forma parte de un proyecto de fin de máster. Para cualquier consulta relacionada con el servicio, puedes usar el formulario de contacto.</p>\n\n<h3 class=\"h5 mt-4 fw-bold\">Uso del sitio</h3>\n<p>Las personas usuarias se comprometen a utilizar la plataforma de forma respetuosa, sin publicar contenido ofensivo, ilegal o que vulnere derechos de terceros.</p>\n\n<h3 class=\"h5 mt-4 fw-bold\">Propiedad intelectual</h3>\n<p>Los contenidos, textos, logotipos y elementos visuales del sitio pertenecen a Hubs&Clicks o a sus autores correspondientes.</p>\n',0,'',0),
(2,'/cookies/','Política de Cookies','<p>Este sitio web utiliza cookies para mejorar su experiencia de navegación. Las cookies son pequeños archivos de texto que se almacenan en su dispositivo cuando visita una página web. Estas tecnologías nos permiten ofrecer servicios más personalizados, analizar el tráfico del sitio y mejorar su funcionamiento.</p>\r\n\r\n<h3 class=\"h5 mt-4 fw-bold\">Tipos de cookies que utilizamos:</h3>\r\n<ul>\r\n    <li class=\"mb-2\"><strong>Cookies técnicas:</strong> Son necesarias para el correcto funcionamiento del sitio, como mantener su sesión activa o recordar elementos de una compra.</li>\r\n    <li class=\"mb-2\"><strong>Cookies de análisis:</strong> Recogen información anónima sobre cómo los usuarios interactúan con el sitio, como páginas visitadas o tiempo de permanencia, para mejorar su experiencia.</li>\r\n    <li class=\"mb-2\"><strong>Cookies de personalización:</strong> Permiten recordar sus preferencias, como idioma o configuración del sitio.</li>\r\n    <li class=\"mb-2\"><strong>Cookies publicitarias y de comportamiento:</strong> Se utilizan para mostrar publicidad relacionada con sus intereses, basándose en su comportamiento de navegación.</li>\r\n</ul>\r\n\r\n<h3 class=\"h5 mt-4 fw-bold\">Consentimiento y control:</h3>\r\n<p>El uso de cookies no técnicas requiere su consentimiento previo. Puede aceptar o rechazar el uso de estas cookies a través del banner que aparece al acceder al sitio. También puede gestionar o eliminar las cookies desde la configuración de su navegador en cualquier momento.</p>\r\n<p><strong>Puede cambiar su configuración cuantas veces quiera</strong>, desde el footer de la web (al final de esta web), haciendo click en \"Configurar Cookies\".\r\n\r\n<h3 class=\"h5 mt-4 fw-bold\">Información adicional:</h3>\r\n<ul>\r\n    <li>Las cookies de terceros (como Google Analytics o redes sociales) están sujetas a sus propias políticas de privacidad.</li>\r\n    <li>Puede obtener más información sobre cómo gestionar las cookies en su navegador visitando la sección de ayuda del mismo.</li>\r\n    <li>Para cualquier duda sobre el uso de cookies, puede contactarnos a través de los datos de contacto disponibles en el sitio.</li>\r\n</ul>',0,'',0),
(3,'/privacy/','Política de Privacidad','\n<p>En Hubs&Clicks tratamos los datos necesarios para crear cuentas, gestionar perfiles, publicar contenido, organizar eventos y enviar notificaciones relacionadas con la actividad de la plataforma.</p>\n\n<h3 class=\"h5 mt-4 fw-bold\">Datos que se pueden tratar</h3>\n<p>Nombre de usuario, correo electrónico, datos de perfil, terapias, publicaciones, comentarios, participaciones en eventos y mensajes enviados mediante el formulario de contacto.</p>\n\n<h3 class=\"h5 mt-4 fw-bold\">Finalidad</h3>\n<p>Usamos estos datos para prestar el servicio, permitir la interacción entre usuarios, proteger la seguridad de la plataforma y responder solicitudes de soporte.</p>\n\n<h3 class=\"h5 mt-4 fw-bold\">Derechos</h3>\n<p>Puedes solicitar información, rectificación o eliminación de tus datos desde el formulario de contacto.</p>\n',0,'',0);
/*!40000 ALTER TABLE `django_flatpage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_flatpage_sites`
--

DROP TABLE IF EXISTS `django_flatpage_sites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_flatpage_sites` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `flatpage_id` int(11) NOT NULL,
  `site_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_flatpage_sites_flatpage_id_site_id_0d29d9d1_uniq` (`flatpage_id`,`site_id`),
  KEY `django_flatpage_sites_site_id_bfd8ea84_fk_django_site_id` (`site_id`),
  CONSTRAINT `django_flatpage_sites_flatpage_id_078bbc8b_fk_django_flatpage_id` FOREIGN KEY (`flatpage_id`) REFERENCES `django_flatpage` (`id`),
  CONSTRAINT `django_flatpage_sites_site_id_bfd8ea84_fk_django_site_id` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_flatpage_sites`
--

LOCK TABLES `django_flatpage_sites` WRITE;
/*!40000 ALTER TABLE `django_flatpage_sites` DISABLE KEYS */;
INSERT INTO `django_flatpage_sites` VALUES
(1,1,1),
(2,2,1),
(3,3,1),
(4,3,2);
/*!40000 ALTER TABLE `django_flatpage_sites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=67 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES
(1,'contenttypes','0001_initial','2026-05-25 13:16:56.880465'),
(2,'auth','0001_initial','2026-05-25 13:16:57.152546'),
(3,'admin','0001_initial','2026-05-25 13:16:57.210645'),
(4,'admin','0002_logentry_remove_auto_add','2026-05-25 13:16:57.219769'),
(5,'admin','0003_logentry_add_action_flag_choices','2026-05-25 13:16:57.230347'),
(6,'aficionados_network','0001_initial','2026-05-25 13:16:57.241850'),
(7,'contenttypes','0002_remove_content_type_name','2026-05-25 13:16:57.292518'),
(8,'auth','0002_alter_permission_name_max_length','2026-05-25 13:16:57.320623'),
(9,'auth','0003_alter_user_email_max_length','2026-05-25 13:16:57.340439'),
(10,'auth','0004_alter_user_username_opts','2026-05-25 13:16:57.349685'),
(11,'auth','0005_alter_user_last_login_null','2026-05-25 13:16:57.377974'),
(12,'auth','0006_require_contenttypes_0002','2026-05-25 13:16:57.380236'),
(13,'auth','0007_alter_validators_add_error_messages','2026-05-25 13:16:57.390494'),
(14,'auth','0008_alter_user_username_max_length','2026-05-25 13:16:57.412242'),
(15,'auth','0009_alter_user_last_name_max_length','2026-05-25 13:16:57.432359'),
(16,'auth','0010_alter_group_name_max_length','2026-05-25 13:16:57.452964'),
(17,'auth','0011_update_proxy_permissions','2026-05-25 13:16:57.465222'),
(18,'auth','0012_alter_user_first_name_max_length','2026-05-25 13:16:57.487931'),
(19,'sites','0001_initial','2026-05-25 13:16:57.498177'),
(20,'flatpages','0001_initial','2026-05-25 13:16:57.583364'),
(21,'profiles','0001_initial','2026-05-25 13:16:57.709341'),
(22,'profiles','0002_alter_follow_options_alter_userprofile_options_and_more','2026-05-25 13:16:57.823187'),
(23,'profiles','0003_hobby_userhobby_userprofile_hobbies','2026-05-25 13:16:57.912579'),
(24,'posts','0001_initial','2026-05-25 13:16:58.058719'),
(25,'posts','0002_alter_comment_options_alter_posts_options_and_more','2026-05-25 13:16:58.341723'),
(26,'posts','0003_posts_category','2026-05-25 13:16:58.413179'),
(27,'posts','0004_event','2026-05-25 13:16:58.525295'),
(28,'posts','0005_event_is_canceled','2026-05-25 13:16:58.557035'),
(29,'posts','0006_eventcomment','2026-05-25 13:16:58.614149'),
(30,'profiles','0004_review','2026-05-25 13:16:58.705971'),
(31,'notifications','0001_initial','2026-05-25 13:16:58.784270'),
(32,'notifications','0002_alter_notification_options_notification_comment_and_more','2026-05-25 13:16:58.932020'),
(33,'notifications','0003_notification_event_and_more','2026-05-25 13:16:58.986409'),
(34,'notifications','0004_notification_review_and_more','2026-05-25 13:16:59.048192'),
(35,'posts','0007_event_image','2026-05-25 13:16:59.077971'),
(36,'posts','0008_alter_event_image','2026-05-25 13:16:59.098325'),
(37,'posts','0009_event_level','2026-05-25 13:16:59.137196'),
(38,'posts','0010_alter_event_level','2026-05-25 13:16:59.156294'),
(39,'profiles','0005_hobby_slug','2026-05-25 13:16:59.184507'),
(40,'sessions','0001_initial','2026-05-25 13:16:59.205885'),
(41,'sites','0002_alter_domain_unique','2026-05-25 13:16:59.226059'),
(42,'chat','0001_initial','2026-06-03 19:59:46.140232'),
(43,'chat','0002_conversation_name','2026-06-05 11:13:13.293658'),
(44,'chat','0003_conversation_admin_groupjoinrequest','2026-06-05 11:39:00.286750'),
(45,'chat','0004_message_attachment_message_attachment_type_and_more','2026-06-05 12:52:42.422362'),
(46,'auth','0013_alter_user_email','2026-06-05 13:13:50.492046'),
(47,'chat','0005_message_hidden_by','2026-06-05 13:13:50.563750'),
(48,'posts','0011_event_is_online_event_stream_url_and_more','2026-06-07 12:04:08.524338'),
(49,'posts','0012_eventattendance','2026-06-07 15:57:51.972878'),
(50,'posts','0013_auto_20260607_1557','2026-06-07 15:57:52.032229'),
(51,'posts','0014_alter_event_participants','2026-06-07 15:58:36.409332'),
(52,'posts','0015_posts_video_posts_video_url','2026-06-07 17:40:36.085570'),
(53,'profiles','0006_userprofile_address_userprofile_mobile_and_more','2026-06-08 13:51:12.731498'),
(54,'posts','0016_alter_eventcomment_options','2026-06-11 10:18:11.326886'),
(55,'posts','0017_alter_comment_options','2026-06-11 10:45:46.543684'),
(56,'marketplace','0001_initial','2026-06-12 12:29:24.742059'),
(57,'marketplace','0002_alter_listing_hobby','2026-06-12 12:46:24.823002'),
(58,'marketplace','0003_listing_video','2026-06-15 09:55:39.299605'),
(59,'marketplace','0004_alter_listing_video','2026-06-15 10:11:29.267518'),
(60,'gamification','0001_initial','2026-06-15 10:44:32.320120'),
(61,'notifications','0005_notification_message_and_more','2026-06-15 11:01:56.110713'),
(62,'library','0001_initial','2026-06-15 11:52:19.729139'),
(63,'notifications','0006_alter_notification_notification_type','2026-06-15 11:52:19.753475'),
(64,'posts','0018_alter_event_image','2026-06-15 12:35:02.786708'),
(65,'posts','0019_alter_posts_category','2026-06-15 12:41:08.864973'),
(66,'profiles','0007_userprofile_numero_socio_userprofile_razon_social','2026-06-16 11:59:17.059981');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES
('1383sqtivjnu3olwdhn0dipg3qylnfek','.eJxVjMEOwiAQRP-FsyFAoSwevfsNZGFXqRpISnsy_rtt0oPOcd6beYuI61Li2nmOE4mzGMTpt0uYn1x3QA-s9yZzq8s8Jbkr8qBdXhvx63K4fwcFe9nWrB3cvPUZnU5byIxsYSRSg9GBKGtNAMpblRQEdg58Bms4IFlP3ojPF-k4N68:1wUP2P:YGQRo2GvkNqjyy5VemKmjy9P03R6adwG3esYbGNJoPA','2026-06-02 14:20:09.804049'),
('51ichomdw5965o9k45cfwxt9ciuqyeb4','.eJxVjMEOwiAQRP-FsyFAoSwevfsNZGFXqRpISnsy_rtt0oPOcd6beYuI61Li2nmOE4mzGMTpt0uYn1x3QA-s9yZzq8s8Jbkr8qBdXhvx63K4fwcFe9nWrB3cvPUZnU5byIxsYSRSg9GBKGtNAMpblRQEdg58Bms4IFlP3ojPF-k4N68:1wZ7MP:uf9HXossA7qGNsPRlqv5RviChlDZTLJe3J7JgBjm-bg','2026-06-15 14:28:17.747094'),
('5drfuqclpsacor1deczyqkrtepiqe8t4','.eJxVjDsOwjAQBe_iGlnyNzYlPWew1rtrHEC2FCcV4u4QKQW0b2beSyTY1pq2wUuaSZyFEqffLQM-uO2A7tBuXWJv6zJnuSvyoENeO_Hzcrh_BxVG_dY6W0eKvEc1eWsCcYjaco5TwUIBUCO46E30GEomtsFpRwjWG5WNM-L9AevdOBg:1wV9d6:DWTA5Q143GN3rwbWpllcOv8TywFtVN_Bl-IxUGqjqrE','2026-06-04 16:05:08.998593'),
('5gwmfv6r0g70uhfzptkgmscvjkvminmx','.eJxVjEEOwiAQRe_C2pACZRhcuvcMZGCmUjVtUtqV8e7apAvd_vfef6lE21rT1mRJI6uzsur0u2UqD5l2wHeabrMu87QuY9a7og_a9HVmeV4O9--gUqvf2pXYy8DAEANm30djIncFPaGD4PosxDagcGeiAGWH1uXCCIDFDw7U-wPfZzfF:1wWJix:XyU02_2cQasn63xaHoZr1qg5brdGCr2EPtTWLBuMXDU','2026-06-07 21:03:59.090486'),
('5j8ydwpru56v6vlneq7nnsdg9e92t1o4','.eJxVjEEOwiAQRe_C2pACZRhcuvcMZGCmUjVtUtqV8e7apAvd_vfef6lE21rT1mRJI6uzsur0u2UqD5l2wHeabrMu87QuY9a7og_a9HVmeV4O9--gUqvf2pXYy8DAEANm30djIncFPaGD4PosxDagcGeiAGWH1uXCCIDFDw7U-wPfZzfF:1wZ7Mc:tUvpwwl-OG84RtJ1B0wsJSLjtLRxPIGDlYI4ZPxj_T0','2026-06-15 14:28:30.083125'),
('69h6ns9ngdujk8bhvof568c2neq8j4wj','.eJxVjDsOwjAQBe_iGlnyNzYlPWew1rtrHEC2FCcV4u4QKQW0b2beSyTY1pq2wUuaSZyFEqffLQM-uO2A7tBuXWJv6zJnuSvyoENeO_Hzcrh_BxVG_dY6W0eKvEc1eWsCcYjaco5TwUIBUCO46E30GEomtsFpRwjWG5WNM-L9AevdOBg:1wUMAk:H87FNN0EXYbDkubY-vWpPE9_UEQUpbBXYXMRCeaw52c','2026-06-16 10:16:34.624940'),
('6mmn0fsksm30wfhmhol2p37ugikxabf7','.eJxVjDsOwjAQBe_iGlnyNzYlPWew1rtrHEC2FCcV4u4QKQW0b2beSyTY1pq2wUuaSZyFEqffLQM-uO2A7tBuXWJv6zJnuSvyoENeO_Hzcrh_BxVG_dY6W0eKvEc1eWsCcYjaco5TwUIBUCO46E30GEomtsFpRwjWG5WNM-L9AevdOBg:1wV74o:AnK7UJuUoGxcATfgeA-OShOQqKdZckomAKGw2m5Xg5c','2026-06-04 13:21:34.278742'),
('6p6zen5e4bhkvx03q1r2wxydo7qytlyf','.eJxVjMEOwiAQRP-FsyFAoSwevfsNZGFXqRpISnsy_rtt0oPOcd6beYuI61Li2nmOE4mzGMTpt0uYn1x3QA-s9yZzq8s8Jbkr8qBdXhvx63K4fwcFe9nWrB3cvPUZnU5byIxsYSRSg9GBKGtNAMpblRQEdg58Bms4IFlP3ojPF-k4N68:1wXe9K:AGL-ntMQpDHoCdMTA5FmeezSf5-3xBrN5e8ZIc_5Q-o','2026-06-11 13:04:42.042076'),
('6qbhi6zlsg1ap7b1wv5f1rhxam3rbnhg','.eJxVjEEOwiAQRe_C2hAG2qG4dO8ZyAxMpWpoUtqV8e7apAvd_vfef6lI21ri1mSJU1Zn1anT78aUHlJ3kO9Ub7NOc12XifWu6IM2fZ2zPC-H-3dQqJVvTQToOKc-jIDsICT0KCNYcGI8DuyM7zNKYEyIVsijDexw6AQMZFHvD92KN3g:1wWIN2:G31IW-BsV5s6NHdjaJunhiCyIqBjvzX4pw-Ca7eziyU','2026-06-07 19:37:16.094004'),
('79k1wyv12h9d00v0cznesf4nm1sfh2yy','.eJxVjDsOwjAQBe_iGlnyNzYlPWew1rtrHEC2FCcV4u4QKQW0b2beSyTY1pq2wUuaSZyFEqffLQM-uO2A7tBuXWJv6zJnuSvyoENeO_Hzcrh_BxVG_dY6W0eKvEc1eWsCcYjaco5TwUIBUCO46E30GEomtsFpRwjWG5WNM-L9AevdOBg:1wV9bH:ADhN05zRk40xnQ9KGkd3LmWPU4Ob-EjXtWkSMrnes74','2026-06-04 16:03:15.661044'),
('8l490e2x4c4mdywq85bn3dzhoua06xkd','.eJxVjDsOwjAQBe_iGllrG_8o6XMGy95d4wCKpXwqxN0hUgpo38y8l0h5W1vaFp7TSOIinDj9biXjg6cd0D1Pty6xT-s8Frkr8qCLHDrx83q4fwctL-1bn53T2jNHQNKZomavnSeyQMUzAmC1NoA1AUNABdUo7WqEiMEon6t4fwDcZDd_:1wWD5m:DTyPn0XtiqadV7KYDsOg0QDoUeYjC07cu09gAxjyUbA','2026-06-07 13:59:06.420829'),
('91o1lwegdm2imowyhidfyvnoyxopqx7k','.eJxVjEEOwiAQRe_C2pACZRhcuvcMZGCmUjVtUtqV8e7apAvd_vfef6lE21rT1mRJI6uzsur0u2UqD5l2wHeabrMu87QuY9a7og_a9HVmeV4O9--gUqvf2pXYy8DAEANm30djIncFPaGD4PosxDagcGeiAGWH1uXCCIDFDw7U-wPfZzfF:1wWXGI:L_SBviWR-6SZIm_PTgyGt6TIfQ5t6_9V1FfywZ4SjtM','2026-06-08 11:31:18.683425'),
('9r8kt9eovd1ry5tjtryk1kg1vk6msqq7','.eJxVjMsKwjAQRf8laynkNU1cCn5HmMwkJFQTaFpciP-uQhe6Pefc-xQB962EfaQ1VBZnIcXpl0WkJbWvwFyp9obcR2hpe_R1mQ47pusd6-1ytH8HBUf5rFU0liUDkJzBaMfJeWVS9HOmzA5JEVoP2gO5HDkZZ5VlQgNaRm21eL0BHn04hg:1waABj:DVd3NtBzN-Roj9Oi9obJU8ypjX5qCdhGUWVtiOEsQPY','2026-06-18 11:41:35.632344'),
('ahfo1c3slob2ea8elpae12aidodwml46','.eJxVjMEOwiAQRP-FsyFAoSwevfsNZGFXqRpISnsy_rtt0oPOcd6beYuI61Li2nmOE4mzGMTpt0uYn1x3QA-s9yZzq8s8Jbkr8qBdXhvx63K4fwcFe9nWrB3cvPUZnU5byIxsYSRSg9GBKGtNAMpblRQEdg58Bms4IFlP3ojPF-k4N68:1wWXFX:1V9x-v9XOrPZIdxXct1wZVC-9PInEkn1HlR_HpwCxls','2026-06-08 11:30:31.039783'),
('ale7aq0v5nzt24kxpwytmuozryh2bqb0','.eJxVjDsOwjAQBe_iGllrG_8o6XMGy95d4wCKpXwqxN0hUgpo38y8l0h5W1vaFp7TSOIinDj9biXjg6cd0D1Pty6xT-s8Frkr8qCLHDrx83q4fwctL-1bn53T2jNHQNKZomavnSeyQMUzAmC1NoA1AUNABdUo7WqEiMEon6t4fwDcZDd_:1wWD5v:tENLBFom_tMC_PMo5flYsmNK7iiR1NFEGCrMh-Rujos','2026-06-07 13:59:15.203722'),
('as1fhgldrxgh1n1z5akll1syj85q0yld','.eJxVjDsOwjAQBe_iGlnyNzYlPWew1rtrHEC2FCcV4u4QKQW0b2beSyTY1pq2wUuaSZyFEqffLQM-uO2A7tBuXWJv6zJnuSvyoENeO_Hzcrh_BxVG_dY6W0eKvEc1eWsCcYjaco5TwUIBUCO46E30GEomtsFpRwjWG5WNM-L9AevdOBg:1wWBXh:UaOCI9fvHWwsnNbxu8sJyevY21ldpsZ5aATY8OHjLqA','2026-06-07 12:19:49.602116'),
('b4ayp7rds2tq065o2pu095ukcabfi7nn','.eJxVjDsOwjAQBe_iGlnyNzYlPWew1rtrHEC2FCcV4u4QKQW0b2beSyTY1pq2wUuaSZyFEqffLQM-uO2A7tBuXWJv6zJnuSvyoENeO_Hzcrh_BxVG_dY6W0eKvEc1eWsCcYjaco5TwUIBUCO46E30GEomtsFpRwjWG5WNM-L9AevdOBg:1wXJWl:T4B9KmzE44_6uJ2IXQq3WZ1CwqqcoIaCteyp4KOCZjA','2026-06-10 15:03:31.064651'),
('bxpxu4iyfz6juypidjbq69uplkgxdinj','.eJxVjMEOwiAQRP-FsyFAoSwevfsNZGFXqRpISnsy_rtt0oPOcd6beYuI61Li2nmOE4mzGMTpt0uYn1x3QA-s9yZzq8s8Jbkr8qBdXhvx63K4fwcFe9nWrB3cvPUZnU5byIxsYSRSg9GBKGtNAMpblRQEdg58Bms4IFlP3ojPF-k4N68:1wXGmE:6AVbaMdfwSONptL7rbzgahPmH1WaPjdbC1DNKjBUNgM','2026-06-10 12:07:18.690048'),
('c19nlkaui7qyzlaxtvjuyhg28ghpnejs','.eJxVjDsOwjAQBe_iGlnyNzYlPWew1rtrHEC2FCcV4u4QKQW0b2beSyTY1pq2wUuaSZyFEqffLQM-uO2A7tBuXWJv6zJnuSvyoENeO_Hzcrh_BxVG_dY6W0eKvEc1eWsCcYjaco5TwUIBUCO46E30GEomtsFpRwjWG5WNM-L9AevdOBg:1wV7w8:bXAFRMZjmyw3c8WfgCgFUKQFnxHc5OOiZso3BcS7Kr0','2026-06-04 14:16:40.114103'),
('cult45u2h0rvp3bda7odf9em12ovf1ga','.eJxVjEEOwiAQRe_C2pACZRhcuvcMZGCmUjVtUtqV8e7apAvd_vfef6lE21rT1mRJI6uzsur0u2UqD5l2wHeabrMu87QuY9a7og_a9HVmeV4O9--gUqvf2pXYy8DAEANm30djIncFPaGD4PosxDagcGeiAGWH1uXCCIDFDw7U-wPfZzfF:1wY27N:hIAO7LjECleXekCNrzwTjYLSeqb0y6rJ6-D9DJXTNvI','2026-06-12 14:40:17.423659'),
('dfmtfj29b2m3psoi9qmgdss2m71uhgqw','.eJxVjEEOwiAQRe_C2hAG2qG4dO8ZyAxMpWpoUtqV8e7apAvd_vfef6lI21ri1mSJU1Zn1anT78aUHlJ3kO9Ub7NOc12XifWu6IM2fZ2zPC-H-3dQqJVvTQToOKc-jIDsICT0KCNYcGI8DuyM7zNKYEyIVsijDexw6AQMZFHvD92KN3g:1wWJ24:c5a178_-K040VDgeOCIpNfnKSjE2Z2XvUZTk2X1lt2E','2026-06-07 20:19:40.087889'),
('dmenkjuwvqqhnbyef0605pfesj3wy6li','.eJxVjMEOwiAQRP-FsyFAoSwevfsNZGFXqRpISnsy_rtt0oPOcd6beYuI61Li2nmOE4mzGMTpt0uYn1x3QA-s9yZzq8s8Jbkr8qBdXhvx63K4fwcFe9nWrB3cvPUZnU5byIxsYSRSg9GBKGtNAMpblRQEdg58Bms4IFlP3ojPF-k4N68:1wV9dA:mrecCd5riDNOoscittst8h-ARu-dFSUFX1q2QMLrKGo','2026-06-04 16:05:12.190690'),
('fx6tklmfcwsbfoygkqvb20xna949pnof','.eJxVjMEOwiAQRP-FsyFAoSwevfsNZGFXqRpISnsy_rtt0oPOcd6beYuI61Li2nmOE4mzGMTpt0uYn1x3QA-s9yZzq8s8Jbkr8qBdXhvx63K4fwcFe9nWrB3cvPUZnU5byIxsYSRSg9GBKGtNAMpblRQEdg58Bms4IFlP3ojPF-k4N68:1wXexN:D8842DAIYTrWlP0VhNxB3wCmMdgrXYYvU0Tx5qJSXrQ','2026-06-11 13:56:25.611932'),
('gontlvd6yho42fut89fjbhkgzooy295q','.eJxVjMEOwiAQRP-FsyFAoSwevfsNZGFXqRpISnsy_rtt0oPOcd6beYuI61Li2nmOE4mzGMTpt0uYn1x3QA-s9yZzq8s8Jbkr8qBdXhvx63K4fwcFe9nWrB3cvPUZnU5byIxsYSRSg9GBKGtNAMpblRQEdg58Bms4IFlP3ojPF-k4N68:1wRqPc:7whj2OG1X0bbPOjoRqLqigWDPSxgjT0zOFNyaTUaC14','2026-06-09 11:57:32.289247'),
('iar4xvne8ierd745hr0pjsegz4kulho6','.eJxVjMEOwiAQRP-FsyFAoSwevfsNZGFXqRpISnsy_rtt0oPOcd6beYuI61Li2nmOE4mzGMTpt0uYn1x3QA-s9yZzq8s8Jbkr8qBdXhvx63K4fwcFe9nWrB3cvPUZnU5byIxsYSRSg9GBKGtNAMpblRQEdg58Bms4IFlP3ojPF-k4N68:1wUP2R:ZoybFJBXLpCF4kjw2zB4bNpsDHxux1NtlxSunIHZ-qE','2026-06-02 14:20:11.153445'),
('jaac1zswvrm6j1ba3uqwfmz2p15niman','.eJxVjMEOwiAQRP-FsyFAoSwevfsNZGFXqRpISnsy_rtt0oPOcd6beYuI61Li2nmOE4mzGMTpt0uYn1x3QA-s9yZzq8s8Jbkr8qBdXhvx63K4fwcFe9nWrB3cvPUZnU5byIxsYSRSg9GBKGtNAMpblRQEdg58Bms4IFlP3ojPF-k4N68:1wY272:3jkHeB4ABSRD5Z909-HfwW2KDNx6tBmboGMnp5mIrKg','2026-06-12 14:39:56.785926'),
('l47wb7erptl7zudxzkvwggke0gs6ytfi','.eJxVjMsKwjAQRf8laynkNU1cCn5HmMwkJFQTaFpciP-uQhe6Pefc-xQB962EfaQ1VBZnIcXpl0WkJbWvwFyp9obcR2hpe_R1mQ47pusd6-1ytH8HBUf5rFU0liUDkJzBaMfJeWVS9HOmzA5JEVoP2gO5HDkZZ5VlQgNaRm21eL0BHn04hg:1wZTsu:qKn0Xf95QSPv2fTX3rPiDOqXg5FzrEmbeWCGBnVds6c','2026-06-16 14:31:20.641947'),
('lcch08z0y0mmpou1dlle2rfp3ddugsgv','.eJxVjMEOwiAQRP-FsyFAoSwevfsNZGFXqRpISnsy_rtt0oPOcd6beYuI61Li2nmOE4mzGMTpt0uYn1x3QA-s9yZzq8s8Jbkr8qBdXhvx63K4fwcFe9nWrB3cvPUZnU5byIxsYSRSg9GBKGtNAMpblRQEdg58Bms4IFlP3ojPF-k4N68:1wWaRC:3jJNYKMpW_JDB5yUeC-POaP3SMKJITkHf8oEQlSgrr8','2026-06-08 14:54:46.841330'),
('lm74tn9kxhc67c0n3o8aica1jec6l7hc','.eJxVjEEOwiAQRe_C2hAG2qG4dO8ZyAxMpWpoUtqV8e7apAvd_vfef6lI21ri1mSJU1Zn1anT78aUHlJ3kO9Ub7NOc12XifWu6IM2fZ2zPC-H-3dQqJVvTQToOKc-jIDsICT0KCNYcGI8DuyM7zNKYEyIVsijDexw6AQMZFHvD92KN3g:1wWJiq:UZc5lxBWgIg7wDkyW7Ox66JGCxxKRW5380V1rPNKDiY','2026-06-07 21:03:52.233936'),
('m0yts9jk5ej2w5rirf3x25z669qs4ong','.eJxVjMEOwiAQRP-FsyFAoSwevfsNZGFXqRpISnsy_rtt0oPOcd6beYuI61Li2nmOE4mzGMTpt0uYn1x3QA-s9yZzq8s8Jbkr8qBdXhvx63K4fwcFe9nWrB3cvPUZnU5byIxsYSRSg9GBKGtNAMpblRQEdg58Bms4IFlP3ojPF-k4N68:1wWJim:WUwdiZ6lnqZpktI-AZMENMkJzjv49wy4UaXLJWob2-A','2026-06-07 21:03:48.613312'),
('m3gyv4mh85gz5s1yh99rgacpr1qilq3r','.eJxVjEEKwjAQRe-StZQ2SScTl4LnCJPMhIRqC02LC_HuKnSh2_fe_08VaN9K2JusobI6K61OvyxSmmT-Cso11WUmXlqYZXss69QdtnXXO9Xb5Wj_Dgq18lmb5K1kBgbvMI7WD4PnPuFIaMAZG4VYOxTuBy9A0aA2MTECYBqzAfV6AxIHODM:1wZnie:iWANxBzdT0wtAuxtGEqmvoIOih9JinXa88ofiP4dxFc','2026-06-17 11:42:04.242525'),
('ns0qzrwwxwqswfa7ka2twx38sacnywnd','.eJxVjEEOwiAQRe_C2pACZRhcuvcMZGCmUjVtUtqV8e7apAvd_vfef6lE21rT1mRJI6uzsur0u2UqD5l2wHeabrMu87QuY9a7og_a9HVmeV4O9--gUqvf2pXYy8DAEANm30djIncFPaGD4PosxDagcGeiAGWH1uXCCIDFDw7U-wPfZzfF:1wWXGG:LleVpDLA1KResN8MJNo2lGRmh4VWDznJhofJUgCZ7b8','2026-06-08 11:31:16.110052'),
('nwl6zmfrcy6umx320ek67jo7g949kxb7','.eJxVjDsOwjAQBe_iGlnyNzYlPWew1rtrHEC2FCcV4u4QKQW0b2beSyTY1pq2wUuaSZyFEqffLQM-uO2A7tBuXWJv6zJnuSvyoENeO_Hzcrh_BxVG_dY6W0eKvEc1eWsCcYjaco5TwUIBUCO46E30GEomtsFpRwjWG5WNM-L9AevdOBg:1wU2BH:bZ0g2VZ6xEztZZRQvq8BmGCdDqT24mqUdIUtbey6Tpc','2026-06-15 12:55:47.268126'),
('odcr6ejia0zgl14ymyeqz8k6hhnuulmj','.eJxVjEEOwiAQRe_C2pACZRhcuvcMZGCmUjVtUtqV8e7apAvd_vfef6lE21rT1mRJI6uzsur0u2UqD5l2wHeabrMu87QuY9a7og_a9HVmeV4O9--gUqvf2pXYy8DAEANm30djIncFPaGD4PosxDagcGeiAGWH1uXCCIDFDw7U-wPfZzfF:1wWIJN:1S3hpf-CkUAXjh9pDpHwy_XE-wj3LzouLZQ5FISpxK8','2026-06-07 19:33:29.010578'),
('sdvvghedj9xr99k8cpwsuhmg894cqvfe','.eJxVjDsOwjAQBe_iGlnyNzYlPWew1rtrHEC2FCcV4u4QKQW0b2beSyTY1pq2wUuaSZyFEqffLQM-uO2A7tBuXWJv6zJnuSvyoENeO_Hzcrh_BxVG_dY6W0eKvEc1eWsCcYjaco5TwUIBUCO46E30GEomtsFpRwjWG5WNM-L9AevdOBg:1wWaRC:h8AMVPYAzsK-VDtUjpQA12TyMwbfCIq_uOBlyGcb5ZQ','2026-06-08 14:54:46.712838'),
('skj1lep0g1k1tvmt5ph3lgjdkw79ydl5','.eJxVjMEOwiAQRP-FsyFAoSwevfsNZGFXqRpISnsy_rtt0oPOcd6beYuI61Li2nmOE4mzGMTpt0uYn1x3QA-s9yZzq8s8Jbkr8qBdXhvx63K4fwcFe9nWrB3cvPUZnU5byIxsYSRSg9GBKGtNAMpblRQEdg58Bms4IFlP3ojPF-k4N68:1wUP4g:a7lsjUUUwy0pDnnZvyZB2xzxSaTJHpD0R5HM2VBEIlY','2026-06-02 14:22:30.586370'),
('skzbmsk33c257rnjisv7cbsqibtg7l0s','.eJxVjEEOwiAQRe_C2hAG2qG4dO8ZyAxMpWpoUtqV8e7apAvd_vfef6lI21ri1mSJU1Zn1anT78aUHlJ3kO9Ub7NOc12XifWu6IM2fZ2zPC-H-3dQqJVvTQToOKc-jIDsICT0KCNYcGI8DuyM7zNKYEyIVsijDexw6AQMZFHvD92KN3g:1wWHxY:oVEB8VRRfLnxE2VaVpeb84MgMQ5K1QCWPXHyYKxUNEs','2026-06-07 19:10:56.491701'),
('ujzlkbkhlsc274h0xxo56d61v28tipai','.eJxVjEEKwjAQRe-StZQ2SScTl4LnCJPMhIRqC02LC_HuKnSh2_fe_08VaN9K2JusobI6K61OvyxSmmT-Cso11WUmXlqYZXss69QdtnXXO9Xb5Wj_Dgq18lmb5K1kBgbvMI7WD4PnPuFIaMAZG4VYOxTuBy9A0aA2MTECYBqzAfV6AxIHODM:1wZnjC:z5s_qDDoTuRvqTPqhOV1nrSjyXF2RRKdjCJgmayvOtw','2026-06-17 11:42:38.572993'),
('v160c0yw4fm6oen0ioa4ep9qv36ry6oi','.eJxVjEEOwiAQRe_C2pACZRhcuvcMZGCmUjVtUtqV8e7apAvd_vfef6lE21rT1mRJI6uzsur0u2UqD5l2wHeabrMu87QuY9a7og_a9HVmeV4O9--gUqvf2pXYy8DAEANm30djIncFPaGD4PosxDagcGeiAGWH1uXCCIDFDw7U-wPfZzfF:1wXJXD:UbLzZfazi-JOSzjB1JvmZJ8HLLeTBv224O40JlgcVbo','2026-06-10 15:03:59.436681'),
('wfjd11i5jvlggonr4rg55pa9gtf3s3ym','.eJxVjEEOwiAQRe_C2hAG2qG4dO8ZyAxMpWpoUtqV8e7apAvd_vfef6lI21ri1mSJU1Zn1anT78aUHlJ3kO9Ub7NOc12XifWu6IM2fZ2zPC-H-3dQqJVvTQToOKc-jIDsICT0KCNYcGI8DuyM7zNKYEyIVsijDexw6AQMZFHvD92KN3g:1wWIR1:wW8ndwUqmOfkT7vSCHbQkJm619IS3_kOtLHTHKFeXWs','2026-06-07 19:41:23.422512'),
('x5g7rbmv8tojg7k09v8jrsj30688dsxh','.eJxVjMEOwiAQRP-FsyFAoSwevfsNZGFXqRpISnsy_rtt0oPOcd6beYuI61Li2nmOE4mzGMTpt0uYn1x3QA-s9yZzq8s8Jbkr8qBdXhvx63K4fwcFe9nWrB3cvPUZnU5byIxsYSRSg9GBKGtNAMpblRQEdg58Bms4IFlP3ojPF-k4N68:1wVUTz:4aCbejVuf5ScfQ38PrY0XUgr9sVLKqvBLU0bzCwdjDM','2026-06-05 14:21:07.504061'),
('xccjjsxxe8uzdvewgi78exnzbwd7yxd2','.eJxVjEEOwiAQRe_C2pACZRhcuvcMZGCmUjVtUtqV8e7apAvd_vfef6lE21rT1mRJI6uzsur0u2UqD5l2wHeabrMu87QuY9a7og_a9HVmeV4O9--gUqvf2pXYy8DAEANm30djIncFPaGD4PosxDagcGeiAGWH1uXCCIDFDw7U-wPfZzfF:1wVUTq:Go1VDfMMYz8drUYQ469X1z_PUZiv-HV_Q-Dyrfp9zV0','2026-06-05 14:20:58.035821'),
('y5e317ngr13zjm21vquoe2fuowmys5t4','.eJxVjMEOwiAQRP-FsyFAoSwevfsNZGFXqRpISnsy_rtt0oPOcd6beYuI61Li2nmOE4mzGMTpt0uYn1x3QA-s9yZzq8s8Jbkr8qBdXhvx63K4fwcFe9nWrB3cvPUZnU5byIxsYSRSg9GBKGtNAMpblRQEdg58Bms4IFlP3ojPF-k4N68:1wWvOH:zD352479hm6lBlJZfqSc6BHohs6eaDpLs6eW4ngATH4','2026-06-09 13:17:09.024058'),
('ycvvwfpw5gbbbzlh7pjwv5mdmpjfu1s2','.eJxVjEEOwiAQRe_C2pACZRhcuvcMZGCmUjVtUtqV8e7apAvd_vfef6lE21rT1mRJI6uzsur0u2UqD5l2wHeabrMu87QuY9a7og_a9HVmeV4O9--gUqvf2pXYy8DAEANm30djIncFPaGD4PosxDagcGeiAGWH1uXCCIDFDw7U-wPfZzfF:1wWISs:Jma8u-qPBBuFQDTrxKP3xcJFAx9zEAIZpYYMqPEG1jg','2026-06-07 19:43:18.756837'),
('yrnsw5nj2njsp731mmlwvw08b2hvh2vu','.eJxVjDsOwjAQBe_iGlnyNzYlPWew1rtrHEC2FCcV4u4QKQW0b2beSyTY1pq2wUuaSZyFEqffLQM-uO2A7tBuXWJv6zJnuSvyoENeO_Hzcrh_BxVG_dY6W0eKvEc1eWsCcYjaco5TwUIBUCO46E30GEomtsFpRwjWG5WNM-L9AevdOBg:1wWvOl:FnQ7TY_3LclzBLjOYokTDyPo1oPYjqs2gJIVOjdTqog','2026-06-09 13:17:39.329539');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_site`
--

DROP TABLE IF EXISTS `django_site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_site_domain_a2e37b91_uniq` (`domain`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_site`
--

LOCK TABLES `django_site` WRITE;
/*!40000 ALTER TABLE `django_site` DISABLE KEYS */;
INSERT INTO `django_site` VALUES
(1,'127.0.0.1:8000','127.0.0.1:8000'),
(2,'127.0.0.1/8000','localhost');
/*!40000 ALTER TABLE `django_site` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gamification_badge`
--

DROP TABLE IF EXISTS `gamification_badge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `gamification_badge` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` longtext NOT NULL,
  `icon` varchar(50) NOT NULL,
  `code_name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code_name` (`code_name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gamification_badge`
--

LOCK TABLES `gamification_badge` WRITE;
/*!40000 ALTER TABLE `gamification_badge` DISABLE KEYS */;
INSERT INTO `gamification_badge` VALUES
(1,'Voz Holística','Has iluminado a la comunidad. Otorgada por recibir 50 likes en total.','fas fa-leaf text-success','voz-holistica'),
(2,'Maestro Facilitador','Líder en naturopatía. Otorgada por organizar 3 eventos con alta asistencia.','fas fa-sun text-warning','maestro-facilitador'),
(3,'Guía de Luz','Excelencia reconocida. Otorgada por conseguir 5 valoraciones con promedio de excelencia (mayor a 4.5 estrellas).','fas fa-star-of-life text-info','guia-de-luz');
/*!40000 ALTER TABLE `gamification_badge` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gamification_userbadge`
--

DROP TABLE IF EXISTS `gamification_userbadge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `gamification_userbadge` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `earned_at` datetime(6) NOT NULL,
  `badge_id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gamification_userbadge_user_id_badge_id_4ed312f7_uniq` (`user_id`,`badge_id`),
  KEY `gamification_userbad_badge_id_d544c9cb_fk_gamificat` (`badge_id`),
  CONSTRAINT `gamification_userbad_badge_id_d544c9cb_fk_gamificat` FOREIGN KEY (`badge_id`) REFERENCES `gamification_badge` (`id`),
  CONSTRAINT `gamification_userbadge_user_id_6f451a69_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gamification_userbadge`
--

LOCK TABLES `gamification_userbadge` WRITE;
/*!40000 ALTER TABLE `gamification_userbadge` DISABLE KEYS */;
/*!40000 ALTER TABLE `gamification_userbadge` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `library_article`
--

DROP TABLE IF EXISTS `library_article`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `library_article` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `slug` varchar(255) NOT NULL,
  `content` longtext NOT NULL,
  `cover_image` varchar(100) DEFAULT NULL,
  `attached_video` varchar(100) DEFAULT NULL,
  `attached_document` varchar(100) DEFAULT NULL,
  `external_video_url` varchar(200) DEFAULT NULL,
  `external_document_url` varchar(200) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `views_count` int(10) unsigned NOT NULL CHECK (`views_count` >= 0),
  `author_id` int(11) NOT NULL,
  `hobby_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `library_article_author_id_b9d0f189_fk_auth_user_id` (`author_id`),
  KEY `library_article_hobby_id_f97c83cf_fk_profiles_hobby_id` (`hobby_id`),
  CONSTRAINT `library_article_author_id_b9d0f189_fk_auth_user_id` FOREIGN KEY (`author_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `library_article_hobby_id_f97c83cf_fk_profiles_hobby_id` FOREIGN KEY (`hobby_id`) REFERENCES `profiles_hobby` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `library_article`
--

LOCK TABLES `library_article` WRITE;
/*!40000 ALTER TABLE `library_article` DISABLE KEYS */;
INSERT INTO `library_article` VALUES
(1,'Primer artículo','primer-articulo-2','<p>&nbsp;<strong>Lorem ipsum dolor </strong>sit amet, consectetur adipiscing elit. Suspendisse blandit imperdiet purus quis egestas. Nulla eget felis vel magna malesuada consequat in in lorem. Vivamus eget nulla nec nisl gravida semper. In nisi ante, elementum eget nisl vel, blandit auctor neque. Quisque dolor lorem, rutrum et porta vel, pretium eget elit. Quisque facilisis semper faucibus. Integer venenatis auctor lectus at faucibus. Sed viverra est velit, id egestas urna semper eu. <em><strong>Cras felis neque, pharetra quis enim a</strong></em>, scelerisque posuere ex. Maecenas rutrum elit neque, eu consectetur arcu volutpat facilisis. Suspendisse elementum arcu at purus pretium, eget efficitur mauris cursus. In sit amet risus condimentum, consectetur ligula a, ullamcorper risus. Integer semper metus sed nunc porta, nec rhoncus enim blandit. Morbi magna lacus, pulvinar a rhoncus eu, aliquam eget sapien. Cras placerat massa nec velit ornare venenatis. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae;</p>\r\n<p><strong>Aenean porttitor laoreet tortor et fermentum. </strong>Nam dignissim ipsum vitae ante interdum viverra. Ut ornare eros eget arcu volutpat, ac accumsan lectus aliquam. Ut varius ullamcorper nibh at commodo. Phasellus ut eleifend orci. Praesent metus libero, malesuada ac lacus vitae, mollis suscipit nulla. Aliquam nisl eros, suscipit ut lacus in, fermentum sagittis nulla. Mauris eget turpis eget ligula mollis volutpat quis sit amet diam. Maecenas vel nisl est. Donec non velit id ex sodales sollicitudin. Nam fermentum urna ligula, eu pretium nulla aliquam ac. Duis vitae ullamcorper est, nec consequat lectus. Quisque ac sapien ac mauris sagittis venenatis auctor eget sapien. Curabitur tellus elit, feugiat malesuada convallis a, bibendum at justo. Ut commodo rhoncus nulla sit amet blandit.</p>\r\n<p><strong>Aliquam non nunc ex. </strong><em>Morbi tellus diam, </em>aliquet eu auctor sit amet, rutrum ac leo. Aenean eleifend viverra ligula et tincidunt. Vivamus ac nisl a arcu pharetra ullamcorper sed eget odio. Nunc venenatis nisl scelerisque, imperdiet leo a, aliquam ante. Aenean bibendum, quam sed hendrerit tempus, nibh velit mollis lectus, ut ornare lectus tellus at ligula. Nunc tristique risus justo, et iaculis odio imperdiet non. Cras non justo feugiat, vehicula ante aliquam, dignissim magna. Duis suscipit mi vel condimentum fermentum. Aliquam nec lobortis purus. Quisque diam arcu, convallis quis urna in, tincidunt dapibus metus. Aenean mollis blandit dolor, vel pretium purus bibendum at.&nbsp;</p>\r\n<p><a title=\"Cuello puntura canaria\" href=\"https://www.lipsum.com/feed/html\">Art&iacute;culo completo</a></p>','library_covers/2026/06/15/hero-img.png','library_videos/2026/06/15/3499958-hd_1280_720_30fps.mp4','',NULL,NULL,'2026-06-15 12:08:22.758743','2026-06-15 12:08:22.758784',8,2,35),
(4,'Neque porro quisquam est qui dolorem ipsum','neque-porro-quisquam-est-qui-dolorem-ipsum-2','<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse blandit imperdiet purus quis egestas. Nulla eget felis vel magna malesuada consequat in in lorem. Vivamus eget nulla nec nisl gravida semper. In nisi ante, elementum eget nisl vel, <a href=\"https://images.unsplash.com/photo-1689308271305-58e75832289b?fm=jpg&amp;q=60&amp;w=3000&amp;auto=format&amp;fit=crop&amp;ixlib=rb-4.1.0&amp;ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D\">https://images.unsplash.com/photo-1689308271305-58e75832289b?fm=jpg&amp;q=60&amp;w=3000&amp;auto=format&amp;fit=crop&amp;ixlib=rb-4.1.0&amp;ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D</a>blandit auctor neque. Quisque dolor lorem, rutrum et porta vel, pretium eget elit. Quisque facilisis semper faucibus. Integer venenatis auctor lectus at faucibus. Sed viverra est velit, id egestas urna semper eu. Cras felis neque, pharetra quis enim a, scelerisque posuere ex. Maecenas rutrum elit neque, eu consectetur arcu volutpat facilisis. Suspendisse elementum arcu at purus pretium, eget efficitur mauris cursus. In sit amet risus condimentum, consectetur ligula a, ullamcorper risus. Integer semper metus sed nunc porta, nec rhoncus enim blandit. Morbi magna lacus, pulvinar a rhoncus eu, aliquam eget sapien. Cras placerat massa nec velit ornare venenatis. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; e</p>','library_covers/2026/06/15/pingu_linux.jpg','','',NULL,NULL,'2026-06-15 12:24:04.158338','2026-06-15 12:29:44.005683',11,2,5);
/*!40000 ALTER TABLE `library_article` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `library_articlecomment`
--

DROP TABLE IF EXISTS `library_articlecomment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `library_articlecomment` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `content` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `article_id` bigint(20) NOT NULL,
  `author_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `library_articlecomment_article_id_3efe9727_fk_library_article_id` (`article_id`),
  KEY `library_articlecomment_author_id_d2cd0de9_fk_auth_user_id` (`author_id`),
  CONSTRAINT `library_articlecomment_article_id_3efe9727_fk_library_article_id` FOREIGN KEY (`article_id`) REFERENCES `library_article` (`id`),
  CONSTRAINT `library_articlecomment_author_id_d2cd0de9_fk_auth_user_id` FOREIGN KEY (`author_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `library_articlecomment`
--

LOCK TABLES `library_articlecomment` WRITE;
/*!40000 ALTER TABLE `library_articlecomment` DISABLE KEYS */;
INSERT INTO `library_articlecomment` VALUES
(1,'Que chuclada!!!','2026-06-16 13:00:36.542134',4,2),
(2,'OK, makey!','2026-06-16 13:06:03.066292',1,2);
/*!40000 ALTER TABLE `library_articlecomment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `library_articlerating`
--

DROP TABLE IF EXISTS `library_articlerating`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `library_articlerating` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `rating` smallint(5) unsigned NOT NULL CHECK (`rating` >= 0),
  `created_at` datetime(6) NOT NULL,
  `article_id` bigint(20) NOT NULL,
  `author_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `library_articlerating_article_id_author_id_1032c48b_uniq` (`article_id`,`author_id`),
  KEY `library_articlerating_author_id_bd6d4c77_fk_auth_user_id` (`author_id`),
  CONSTRAINT `library_articlerating_article_id_dcc9e83a_fk_library_article_id` FOREIGN KEY (`article_id`) REFERENCES `library_article` (`id`),
  CONSTRAINT `library_articlerating_author_id_bd6d4c77_fk_auth_user_id` FOREIGN KEY (`author_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `library_articlerating`
--

LOCK TABLES `library_articlerating` WRITE;
/*!40000 ALTER TABLE `library_articlerating` DISABLE KEYS */;
/*!40000 ALTER TABLE `library_articlerating` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `marketplace_listing`
--

DROP TABLE IF EXISTS `marketplace_listing`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `marketplace_listing` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `slug` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `listing_type` varchar(20) NOT NULL,
  `status` varchar(20) NOT NULL,
  `image` varchar(100) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `hobby_id` bigint(20) DEFAULT NULL,
  `seller_id` int(11) NOT NULL,
  `video` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `marketplace_listing_hobby_id_eedce9ba_fk_profiles_hobby_id` (`hobby_id`),
  KEY `marketplace_listing_seller_id_56a0f16d_fk_auth_user_id` (`seller_id`),
  CONSTRAINT `marketplace_listing_hobby_id_eedce9ba_fk_profiles_hobby_id` FOREIGN KEY (`hobby_id`) REFERENCES `profiles_hobby` (`id`),
  CONSTRAINT `marketplace_listing_seller_id_56a0f16d_fk_auth_user_id` FOREIGN KEY (`seller_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `marketplace_listing`
--

LOCK TABLES `marketplace_listing` WRITE;
/*!40000 ALTER TABLE `marketplace_listing` DISABLE KEYS */;
INSERT INTO `marketplace_listing` VALUES
(1,'Camilla plegable','camilla-plegable-2','Camilla plegable en buen estado.',90.50,'SALE','AVAILABLE','marketplace_images/2026/06/12/camilla_plegable.jpg','2026-06-12 12:38:05.273251','2026-06-12 12:38:05.273306',5,2,NULL),
(2,'Alquiler de sala de yoga','alquiler-de-sala-de-yoga-3','Alquiler de sala de yoga o usos múltiples por horas o días completos.',12.20,'SPACE','AVAILABLE','marketplace_images/2026/06/12/camilla_plegable_O5IdR9Z.jpg','2026-06-12 12:49:51.961646','2026-06-12 12:49:51.961726',NULL,3,NULL),
(3,'Caña de bambú para aplicación Okiu sistema Toyohari','cana-de-bambu-para-aplicacion-okiu-sistema-toyohari-2','Caña de bambú para aplicación Okiu sistema Toyohari',1.50,'RENT','AVAILABLE','marketplace_images/2026/06/12/caña-okiu.jpg','2026-06-12 13:02:07.533309','2026-06-12 13:02:07.533367',24,2,NULL),
(4,'alquiler sala multiusos','alquiler-sala-multiusos-1','Alquiler de sala multiusos.',12.50,'SPACE','AVAILABLE','marketplace_images/2026/06/15/camilla_plegable.jpg','2026-06-15 10:14:39.059473','2026-06-15 10:14:39.059488',NULL,1,'marketplace_videos/2026/06/15/bono_regalo_navidad.mp4');
/*!40000 ALTER TABLE `marketplace_listing` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `marketplace_sellerreview`
--

DROP TABLE IF EXISTS `marketplace_sellerreview`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `marketplace_sellerreview` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `rating` smallint(5) unsigned NOT NULL CHECK (`rating` >= 0),
  `comment` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `reviewer_id` int(11) NOT NULL,
  `seller_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `marketplace_sellerreview_seller_id_reviewer_id_8e52c895_uniq` (`seller_id`,`reviewer_id`),
  KEY `marketplace_sellerreview_reviewer_id_424ffbad_fk_auth_user_id` (`reviewer_id`),
  CONSTRAINT `marketplace_sellerreview_reviewer_id_424ffbad_fk_auth_user_id` FOREIGN KEY (`reviewer_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `marketplace_sellerreview_seller_id_69cc9bb2_fk_auth_user_id` FOREIGN KEY (`seller_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `marketplace_sellerreview`
--

LOCK TABLES `marketplace_sellerreview` WRITE;
/*!40000 ALTER TABLE `marketplace_sellerreview` DISABLE KEYS */;
INSERT INTO `marketplace_sellerreview` VALUES
(1,5,'Vendedor genial, camilla no la compro por que es negra','2026-06-12 12:40:33.111122',3,2),
(2,3,'Es muy grande y bonita. Soy envidioso.','2026-06-12 12:50:30.718012',2,3),
(3,5,'Que guay, de paraguay.','2026-06-15 10:17:14.340850',3,1);
/*!40000 ALTER TABLE `marketplace_sellerreview` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications_notification`
--

DROP TABLE IF EXISTS `notifications_notification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications_notification` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `notification_type` varchar(20) NOT NULL,
  `is_read` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `post_id` bigint(20) DEFAULT NULL,
  `recipient_id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `comment_id` bigint(20) DEFAULT NULL,
  `event_id` bigint(20) DEFAULT NULL,
  `review_id` bigint(20) DEFAULT NULL,
  `message` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `notifications_notification_post_id_d84e1970_fk_posts_posts_id` (`post_id`),
  KEY `notifications_notification_recipient_id_d055f3f0_fk_auth_user_id` (`recipient_id`),
  KEY `notifications_notification_sender_id_feea9ca3_fk_auth_user_id` (`sender_id`),
  KEY `notifications_notifi_comment_id_12aa885f_fk_posts_com` (`comment_id`),
  KEY `notifications_notification_event_id_28551f97_fk_posts_event_id` (`event_id`),
  KEY `notifications_notifi_review_id_5ca0adf8_fk_profiles_` (`review_id`),
  CONSTRAINT `notifications_notifi_comment_id_12aa885f_fk_posts_com` FOREIGN KEY (`comment_id`) REFERENCES `posts_comment` (`id`),
  CONSTRAINT `notifications_notifi_review_id_5ca0adf8_fk_profiles_` FOREIGN KEY (`review_id`) REFERENCES `profiles_review` (`id`),
  CONSTRAINT `notifications_notification_event_id_28551f97_fk_posts_event_id` FOREIGN KEY (`event_id`) REFERENCES `posts_event` (`id`),
  CONSTRAINT `notifications_notification_post_id_d84e1970_fk_posts_posts_id` FOREIGN KEY (`post_id`) REFERENCES `posts_posts` (`id`),
  CONSTRAINT `notifications_notification_recipient_id_d055f3f0_fk_auth_user_id` FOREIGN KEY (`recipient_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `notifications_notification_sender_id_feea9ca3_fk_auth_user_id` FOREIGN KEY (`sender_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=272 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications_notification`
--

LOCK TABLES `notifications_notification` WRITE;
/*!40000 ALTER TABLE `notifications_notification` DISABLE KEYS */;
INSERT INTO `notifications_notification` VALUES
(11,'comment',1,'2026-01-24 09:13:22.341000',1,1,4,9,NULL,NULL,NULL),
(13,'comment',1,'2026-01-24 11:37:04.805000',5,4,1,10,NULL,NULL,NULL),
(16,'comment',1,'2026-01-24 12:31:25.535000',NULL,1,4,NULL,NULL,NULL,NULL),
(17,'comment',1,'2026-01-24 12:31:37.442000',NULL,1,4,NULL,NULL,NULL,NULL),
(18,'event',1,'2026-01-24 13:22:11.874000',NULL,1,3,NULL,5,NULL,NULL),
(19,'event',1,'2026-01-24 15:01:15.961000',NULL,3,1,NULL,5,NULL,NULL),
(20,'event',1,'2026-01-24 15:01:38.899000',NULL,3,1,NULL,5,NULL,NULL),
(21,'event',1,'2026-01-24 15:06:48.848000',NULL,3,1,NULL,5,NULL,NULL),
(22,'event',1,'2026-01-24 15:13:41.455000',NULL,1,3,NULL,6,NULL,NULL),
(23,'event',1,'2026-01-24 15:14:00.206000',NULL,3,1,NULL,6,NULL,NULL),
(24,'event',1,'2026-01-24 15:16:56.789000',NULL,4,3,NULL,4,NULL,NULL),
(25,'comment',1,'2026-01-24 22:02:37.179000',NULL,1,4,NULL,2,NULL,NULL),
(26,'comment',1,'2026-01-24 22:32:57.245000',NULL,1,4,NULL,2,NULL,NULL),
(27,'comment',1,'2026-01-24 22:33:56.842000',NULL,1,4,NULL,2,NULL,NULL),
(28,'comment',1,'2026-01-24 22:35:48.709000',NULL,4,1,NULL,2,NULL,NULL),
(29,'comment',1,'2026-01-24 23:07:45.659000',NULL,4,3,NULL,4,NULL,NULL),
(30,'comment',1,'2026-01-24 23:09:27.038000',NULL,3,4,NULL,4,NULL,NULL),
(31,'comment',1,'2026-01-25 09:51:23.341000',5,4,1,15,NULL,NULL,NULL),
(32,'event',1,'2026-01-25 09:53:57.376000',NULL,1,4,NULL,7,NULL,NULL),
(33,'comment',1,'2026-01-25 09:54:22.208000',NULL,1,4,NULL,7,NULL,NULL),
(34,'comment',1,'2026-01-25 10:33:25.836000',NULL,1,4,NULL,7,NULL,NULL),
(35,'comment',1,'2026-01-25 10:43:33.491000',NULL,4,1,NULL,7,NULL,NULL),
(36,'event',1,'2026-01-25 10:54:03.085000',NULL,1,3,NULL,7,NULL,NULL),
(37,'comment',1,'2026-01-25 10:54:22.561000',NULL,1,3,NULL,7,NULL,NULL),
(38,'event',1,'2026-01-25 13:29:23.444000',NULL,3,1,NULL,4,NULL,NULL),
(39,'comment',1,'2026-01-25 14:58:44.865000',NULL,1,4,NULL,7,NULL,NULL),
(40,'comment',1,'2026-01-25 15:13:26.847000',1,1,4,16,NULL,NULL,NULL),
(41,'like',1,'2026-01-25 16:09:19.842000',1,1,4,NULL,NULL,NULL,NULL),
(42,'comment',1,'2026-01-25 16:15:37.334000',5,4,1,18,NULL,NULL,NULL),
(43,'comment',1,'2026-01-25 16:18:30.185000',5,4,1,19,NULL,NULL,NULL),
(44,'comment',1,'2026-01-25 16:18:56.721000',5,3,4,20,NULL,NULL,NULL),
(45,'comment',1,'2026-01-25 16:18:56.724000',5,1,4,20,NULL,NULL,NULL),
(46,'comment',1,'2026-01-25 16:18:56.726000',5,1,4,20,NULL,NULL,NULL),
(47,'comment',1,'2026-01-25 16:18:56.729000',5,1,4,20,NULL,NULL,NULL),
(48,'comment',1,'2026-01-25 16:18:56.731000',5,1,4,20,NULL,NULL,NULL),
(49,'comment',1,'2026-01-25 16:19:31.358000',5,3,4,21,NULL,NULL,NULL),
(50,'comment',1,'2026-01-25 16:19:31.362000',5,1,4,21,NULL,NULL,NULL),
(51,'comment',1,'2026-01-25 16:19:31.366000',5,1,4,21,NULL,NULL,NULL),
(52,'comment',1,'2026-01-25 16:19:31.369000',5,1,4,21,NULL,NULL,NULL),
(53,'comment',1,'2026-01-25 16:19:31.374000',5,1,4,21,NULL,NULL,NULL),
(54,'comment',1,'2026-01-25 16:25:23.906000',5,3,4,22,NULL,NULL,NULL),
(55,'comment',1,'2026-01-25 16:25:23.909000',5,1,4,22,NULL,NULL,NULL),
(56,'comment',1,'2026-01-25 16:26:19.159000',5,3,4,23,NULL,NULL,NULL),
(57,'comment',1,'2026-01-25 16:26:19.163000',5,1,4,23,NULL,NULL,NULL),
(58,'comment',1,'2026-01-25 16:29:35.890000',5,1,4,NULL,NULL,NULL,NULL),
(59,'comment',1,'2026-01-25 16:29:35.894000',5,3,4,NULL,NULL,NULL,NULL),
(60,'comment',1,'2026-01-25 16:30:15.249000',5,4,1,NULL,NULL,NULL,NULL),
(61,'comment',1,'2026-01-25 16:55:22.878000',NULL,1,4,NULL,7,NULL,NULL),
(62,'event',1,'2026-01-25 17:05:31.211000',NULL,3,1,NULL,7,NULL,NULL),
(63,'event',1,'2026-01-25 17:05:37.675000',NULL,4,1,NULL,7,NULL,NULL),
(64,'event',1,'2026-01-27 20:27:01.305000',NULL,4,3,NULL,10,NULL,NULL),
(65,'event',1,'2026-01-27 20:27:44.981000',NULL,4,3,NULL,11,NULL,NULL),
(66,'comment',1,'2026-01-27 20:28:54.728000',NULL,3,4,NULL,10,NULL,NULL),
(67,'comment',1,'2026-01-27 20:34:48.636000',NULL,3,4,NULL,10,NULL,NULL),
(68,'comment',1,'2026-01-27 20:35:06.177000',NULL,3,4,NULL,10,NULL,NULL),
(69,'comment',1,'2026-01-27 20:38:02.879000',NULL,3,4,NULL,10,NULL,NULL),
(70,'comment',1,'2026-01-27 20:41:44.928000',NULL,3,4,NULL,10,NULL,NULL),
(71,'comment',1,'2026-01-27 21:05:20.754000',NULL,4,3,NULL,11,NULL,NULL),
(72,'comment',1,'2026-01-27 21:10:43.858000',NULL,3,4,NULL,11,NULL,NULL),
(73,'comment',1,'2026-01-27 21:11:53.020000',NULL,3,4,NULL,11,NULL,NULL),
(74,'comment',1,'2026-01-27 21:13:28.285000',NULL,3,4,NULL,11,NULL,NULL),
(75,'comment',1,'2026-01-27 21:18:18.621000',NULL,4,3,NULL,11,NULL,NULL),
(76,'comment',1,'2026-01-27 21:22:03.100000',NULL,3,4,NULL,11,NULL,NULL),
(77,'comment',1,'2026-01-27 21:26:18.848000',NULL,4,3,NULL,11,NULL,NULL),
(78,'comment',1,'2026-01-27 21:28:11.671000',NULL,4,3,NULL,11,NULL,NULL),
(79,'comment',1,'2026-01-27 21:43:08.240000',NULL,3,4,NULL,11,NULL,NULL),
(80,'comment',1,'2026-01-29 18:10:17.127000',5,1,4,NULL,NULL,NULL,NULL),
(81,'comment',1,'2026-01-29 18:10:17.131000',5,3,4,NULL,NULL,NULL,NULL),
(95,'like',1,'2026-01-31 09:01:39.313000',4,2,1,NULL,NULL,NULL,NULL),
(96,'like',1,'2026-01-31 09:01:39.335000',4,2,1,NULL,NULL,NULL,NULL),
(98,'like',1,'2026-01-31 09:01:57.236000',1,1,3,NULL,NULL,NULL,NULL),
(99,'like',1,'2026-01-31 09:01:57.240000',1,1,3,NULL,NULL,NULL,NULL),
(100,'event',1,'2026-01-31 09:15:17.467000',NULL,1,3,NULL,12,NULL,NULL),
(101,'comment',1,'2026-01-31 09:16:04.443000',NULL,3,1,NULL,12,NULL,NULL),
(102,'comment',1,'2026-01-31 09:19:23.583000',NULL,1,3,NULL,12,NULL,NULL),
(103,'comment',1,'2026-01-31 09:23:54.358000',NULL,3,1,NULL,12,NULL,NULL),
(109,'event',1,'2026-01-31 09:46:26.162000',NULL,3,4,NULL,13,NULL,NULL),
(110,'comment',1,'2026-01-31 09:47:01.207000',NULL,3,4,NULL,13,NULL,NULL),
(111,'event',1,'2026-01-31 10:43:26.740000',NULL,3,1,NULL,13,NULL,NULL),
(112,'comment',1,'2026-01-31 10:56:15.286000',4,2,1,NULL,NULL,NULL,NULL),
(114,'comment',1,'2026-01-31 19:18:45.727000',NULL,3,4,NULL,13,NULL,NULL),
(115,'comment',1,'2026-01-31 19:35:52.942000',NULL,3,4,NULL,13,NULL,NULL),
(116,'comment',1,'2026-01-31 19:42:05.945000',NULL,1,3,NULL,12,NULL,NULL),
(117,'event',1,'2026-01-31 20:06:01.939000',NULL,3,1,NULL,13,NULL,NULL),
(120,'like',1,'2026-01-31 20:07:34.005000',5,4,1,NULL,NULL,NULL,NULL),
(121,'like',1,'2026-01-31 20:07:34.020000',5,4,1,NULL,NULL,NULL,NULL),
(122,'like',1,'2026-01-31 20:07:34.036000',5,4,1,NULL,NULL,NULL,NULL),
(123,'event',1,'2026-01-31 20:09:27.165000',NULL,3,1,NULL,13,NULL,NULL),
(124,'event',1,'2026-01-31 20:16:54.177000',NULL,1,3,NULL,12,NULL,NULL),
(125,'event',1,'2026-01-31 20:22:21.880000',NULL,3,1,NULL,13,NULL,NULL),
(126,'comment',1,'2026-01-31 20:24:32.194000',NULL,3,4,NULL,13,NULL,NULL),
(127,'event',1,'2026-01-31 20:39:36.007000',NULL,3,4,NULL,13,NULL,NULL),
(128,'comment',1,'2026-01-31 20:43:05.232000',NULL,3,4,NULL,13,NULL,NULL),
(129,'event',1,'2026-01-31 20:44:20.009000',NULL,3,4,NULL,13,NULL,NULL),
(130,'comment',1,'2026-01-31 20:57:02.723000',NULL,3,4,NULL,13,NULL,NULL),
(131,'event',1,'2026-01-31 20:57:08.008000',NULL,3,4,NULL,13,NULL,NULL),
(132,'event',1,'2026-01-31 21:01:20.557000',NULL,3,4,NULL,13,NULL,NULL),
(133,'comment',1,'2026-01-31 21:01:34.203000',NULL,3,4,NULL,13,NULL,NULL),
(134,'event',1,'2026-01-31 21:01:37.368000',NULL,3,4,NULL,13,NULL,NULL),
(135,'comment',1,'2026-01-31 21:23:16.074000',NULL,3,4,NULL,13,NULL,NULL),
(136,'event',1,'2026-01-31 21:34:58.885000',NULL,3,1,NULL,12,NULL,NULL),
(137,'event',1,'2026-01-31 21:47:14.972000',NULL,3,1,NULL,12,NULL,NULL),
(138,'comment',1,'2026-01-31 21:59:43.912000',2,3,4,NULL,NULL,NULL,NULL),
(139,'comment',1,'2026-01-31 22:00:35.983000',2,3,4,NULL,NULL,NULL,NULL),
(150,'comment',1,'2026-01-31 22:09:35.360000',3,3,4,NULL,NULL,NULL,NULL),
(157,'like',1,'2026-01-31 22:22:22.234000',2,3,4,NULL,NULL,NULL,NULL),
(158,'like',1,'2026-01-31 22:22:22.237000',2,3,4,NULL,NULL,NULL,NULL),
(159,'like',1,'2026-01-31 22:22:22.263000',2,3,4,NULL,NULL,NULL,NULL),
(160,'comment',1,'2026-01-31 22:22:36.747000',2,3,4,NULL,NULL,NULL,NULL),
(161,'comment',1,'2026-01-31 22:23:20.714000',2,3,4,NULL,NULL,NULL,NULL),
(162,'comment',1,'2026-01-31 22:35:42.924000',2,3,4,NULL,NULL,NULL,NULL),
(163,'comment',1,'2026-01-31 22:35:42.928000',2,3,4,NULL,NULL,NULL,NULL),
(164,'comment',1,'2026-01-31 22:36:41.591000',2,3,4,NULL,NULL,NULL,NULL),
(165,'review',1,'2026-01-31 22:54:35.965000',NULL,4,4,NULL,11,4,NULL),
(166,'review',1,'2026-01-31 22:54:46.183000',NULL,4,4,NULL,10,5,NULL),
(167,'review',1,'2026-01-31 23:27:36.493000',NULL,1,1,NULL,12,6,NULL),
(168,'comment',1,'2026-02-01 12:58:13.010000',NULL,3,4,NULL,15,NULL,NULL),
(169,'comment',1,'2026-02-01 12:59:22.972000',NULL,4,3,NULL,15,NULL,NULL),
(170,'review',1,'2026-02-01 13:20:32.864000',NULL,1,4,NULL,12,7,NULL),
(177,'comment',1,'2026-02-03 21:30:16.753000',13,4,1,NULL,NULL,NULL,NULL),
(178,'comment',1,'2026-02-03 21:31:41.299000',7,4,3,NULL,NULL,NULL,NULL),
(181,'comment',1,'2026-02-03 21:42:34.585000',13,4,1,NULL,NULL,NULL,NULL),
(187,'comment',1,'2026-02-05 18:07:56.703000',5,4,1,NULL,NULL,NULL,NULL),
(188,'comment',1,'2026-02-05 18:14:06.358000',1,1,4,NULL,NULL,NULL,NULL),
(189,'comment',1,'2026-02-05 18:15:08.312000',1,1,4,NULL,NULL,NULL,NULL),
(194,'comment',1,'2026-02-05 18:34:05.804000',13,1,4,NULL,NULL,NULL,NULL),
(197,'comment',1,'2026-02-05 18:37:07.813000',3,3,1,NULL,NULL,NULL,NULL),
(198,'comment',1,'2026-02-05 18:40:00.612000',1,1,4,NULL,NULL,NULL,NULL),
(199,'comment',1,'2026-02-05 18:40:23.344000',3,3,1,NULL,NULL,NULL,NULL),
(201,'comment',1,'2026-02-05 18:53:24.747000',3,3,1,NULL,NULL,NULL,NULL),
(202,'comment',1,'2026-02-05 18:56:53.665000',1,1,4,NULL,NULL,NULL,NULL),
(209,'comment',1,'2026-02-05 19:32:15.094000',3,3,1,NULL,NULL,NULL,NULL),
(213,'comment',1,'2026-02-05 19:38:42.748000',3,3,1,NULL,NULL,NULL,NULL),
(218,'review',1,'2026-02-07 12:22:25.249000',NULL,4,4,NULL,15,8,NULL),
(219,'review',1,'2026-02-07 12:22:36.828000',NULL,4,4,NULL,16,9,NULL),
(220,'review',1,'2026-02-07 12:22:49.227000',NULL,4,4,NULL,17,10,NULL),
(221,'review',1,'2026-02-07 13:13:15.020000',NULL,4,3,NULL,15,11,NULL),
(224,'like',0,'2026-05-26 10:59:42.584984',13,4,1,NULL,NULL,NULL,NULL),
(225,'like',0,'2026-05-26 10:59:42.586735',13,4,1,NULL,NULL,NULL,NULL),
(226,'like',0,'2026-05-26 10:59:42.589137',13,4,1,NULL,NULL,NULL,NULL),
(227,'review',1,'2026-05-26 11:00:19.954865',NULL,1,1,NULL,20,12,NULL),
(228,'comment',1,'2026-05-26 12:35:36.508411',NULL,3,1,NULL,26,NULL,NULL),
(229,'comment',1,'2026-05-26 12:37:39.693564',NULL,1,3,NULL,26,NULL,NULL),
(238,'review',1,'2026-06-02 10:09:12.798350',NULL,3,3,NULL,25,13,NULL),
(243,'like',0,'2026-06-07 17:30:44.264209',14,4,3,NULL,NULL,NULL,NULL),
(244,'like',0,'2026-06-07 17:30:44.265106',14,4,3,NULL,NULL,NULL,NULL),
(245,'like',1,'2026-06-07 17:30:44.266626',14,4,3,NULL,NULL,NULL,NULL),
(246,'event',1,'2026-06-10 12:27:42.992410',NULL,1,2,NULL,28,NULL,NULL),
(256,'comment',1,'2026-06-10 13:59:53.681893',15,3,2,NULL,NULL,NULL,NULL),
(264,'like',1,'2026-06-10 14:03:59.432663',15,3,2,NULL,NULL,NULL,NULL),
(265,'comment',1,'2026-06-11 10:09:11.194646',NULL,3,2,NULL,26,NULL,NULL),
(266,'comment',0,'2026-06-11 10:32:20.340761',13,4,2,NULL,NULL,NULL,NULL),
(267,'review',1,'2026-06-11 10:35:53.828108',NULL,2,2,NULL,27,14,NULL),
(268,'review',1,'2026-06-11 10:37:59.415451',NULL,2,3,NULL,27,15,NULL),
(269,'like',0,'2026-06-11 10:40:52.171029',13,4,2,NULL,NULL,NULL,NULL),
(270,'comment',0,'2026-06-11 10:47:01.944432',13,4,2,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `notifications_notification` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `posts_comment`
--

DROP TABLE IF EXISTS `posts_comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `posts_comment` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `comment` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` int(11) NOT NULL,
  `post_id` bigint(20) NOT NULL,
  `parent_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `posts_comment_user_id_ad949c47_fk_auth_user_id` (`user_id`),
  KEY `posts_comment_post_id_e81436d7_fk_posts_posts_id` (`post_id`),
  KEY `posts_comment_parent_id_ae76dcba_fk_posts_comment_id` (`parent_id`),
  KEY `posts_comme_created_f825cb_idx` (`created_at`),
  CONSTRAINT `posts_comment_parent_id_ae76dcba_fk_posts_comment_id` FOREIGN KEY (`parent_id`) REFERENCES `posts_comment` (`id`),
  CONSTRAINT `posts_comment_post_id_e81436d7_fk_posts_posts_id` FOREIGN KEY (`post_id`) REFERENCES `posts_posts` (`id`),
  CONSTRAINT `posts_comment_user_id_ad949c47_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=108 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `posts_comment`
--

LOCK TABLES `posts_comment` WRITE;
/*!40000 ALTER TABLE `posts_comment` DISABLE KEYS */;
INSERT INTO `posts_comment` VALUES
(1,'Me alegro que estéis de vacaciones.','2026-01-18 10:28:37.780000','2026-01-18 10:28:37.780000',4,2,NULL),
(2,'Segundo post, de otro usuario. Me parece bien','2026-01-18 11:12:46.901000','2026-01-18 11:12:46.901000',3,1,NULL),
(3,'Eso es otro comentario, de alguien: Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage,','2026-01-18 11:30:38.910000','2026-01-18 11:30:38.910000',1,3,NULL),
(4,'Me gusta mucho.','2026-01-18 12:20:43.718000','2026-01-18 12:20:43.718000',2,3,NULL),
(5,'No me gusta por eso no likes.','2026-01-18 12:21:06.638000','2026-01-18 12:21:06.638000',2,2,NULL),
(6,'no le doy a me gusta porque no me gusta','2026-01-18 21:01:06.689000','2026-01-18 21:01:06.689000',3,5,NULL),
(7,'probando, probando comentario','2026-01-20 20:09:51.957000','2026-01-20 20:09:51.957000',3,4,NULL),
(8,'Que buena foto Juan!!!','2026-01-22 20:17:42.430000','2026-01-22 20:17:42.430000',1,3,NULL),
(9,'UN comentario añadido, viendo como funciona las notificaciones','2026-01-24 09:13:22.335000','2026-01-24 09:13:22.335000',4,1,NULL),
(10,'Un nuevo comentario!!!!','2026-01-24 11:37:04.802000','2026-01-24 11:37:04.802000',1,5,NULL),
(11,'@pepe Gracias a Pepe','2026-01-24 22:11:27.626000','2026-01-24 22:11:27.626000',1,1,NULL),
(12,'@pepe Gracias a Pepe','2026-01-24 22:11:54.580000','2026-01-24 22:11:54.580000',1,1,NULL),
(13,'@pepe Gracias a Pepe','2026-01-24 22:13:37.804000','2026-01-24 22:13:37.804000',1,1,NULL),
(14,'@root gracias root','2026-01-24 22:24:48.164000','2026-01-24 22:24:48.164000',4,5,NULL),
(15,'Comentario para probar los emails.','2026-01-25 09:51:23.300000','2026-01-25 09:51:23.300000',1,5,NULL),
(16,'comentario señor ROot','2026-01-25 15:13:26.807000','2026-01-25 15:13:26.807000',4,1,NULL),
(17,'gracias señor pepe','2026-01-25 16:10:00.416000','2026-01-25 16:10:00.416000',1,1,NULL),
(18,'pepe un comentario para ti','2026-01-25 16:15:37.331000','2026-01-25 16:15:37.331000',1,5,NULL),
(19,'otro comentario pepe','2026-01-25 16:18:30.179000','2026-01-25 16:18:30.179000',1,5,NULL),
(20,'gracias Root','2026-01-25 16:18:56.683000','2026-01-25 16:18:56.683000',4,5,NULL),
(21,'otro comentario ROOT','2026-01-25 16:19:31.318000','2026-01-25 16:19:31.318000',4,5,NULL),
(22,'TERcer comentario espero no se repita 4 veces','2026-01-25 16:25:23.894000','2026-01-25 16:25:23.894000',4,5,NULL),
(23,'TERcer comentario espero no se repita 4 veces','2026-01-25 16:26:19.117000','2026-01-25 16:26:19.117000',4,5,NULL),
(24,'cuarto comentario ROOT','2026-01-25 16:29:35.880000','2026-01-25 16:29:35.880000',4,5,NULL),
(25,'DE Root, gracias pepe','2026-01-25 16:30:15.243000','2026-01-25 16:30:15.243000',1,5,NULL),
(26,'@root Soy pepe, hoy es 29 de enero','2026-01-29 18:10:17.107000','2026-01-29 18:10:17.107000',4,5,NULL),
(28,'Vaya con el admin!!!','2026-01-31 10:56:15.278000','2026-01-31 10:56:15.278000',1,4,NULL),
(29,'Comento algo para enviarse por email.','2026-01-31 21:57:26.675000','2026-01-31 21:57:26.675000',4,2,NULL),
(30,'Comento algo para enviarse por email.','2026-01-31 21:59:43.897000','2026-01-31 21:59:43.897000',4,2,NULL),
(31,'ok, otro comentario','2026-01-31 22:00:35.944000','2026-01-31 22:00:35.944000',4,2,NULL),
(32,'un comentario más, probando spinner y email','2026-01-31 22:09:35.309000','2026-01-31 22:09:35.309000',4,3,NULL),
(33,'COMENTARIO','2026-01-31 22:22:36.740000','2026-01-31 22:22:36.740000',4,2,NULL),
(34,'uno nuevo y más','2026-01-31 22:23:20.706000','2026-01-31 22:23:20.706000',4,2,NULL),
(35,'comentario por ajax','2026-01-31 22:35:42.919000','2026-01-31 22:35:42.919000',4,2,NULL),
(36,'comentario por ajax','2026-01-31 22:35:42.920000','2026-01-31 22:35:42.920000',4,2,NULL),
(37,'comentario sin ajax','2026-01-31 22:36:41.584000','2026-01-31 22:36:41.584000',4,2,NULL),
(57,'otrooo','2026-02-03 21:30:16.745000','2026-02-03 21:30:16.745000',1,13,NULL),
(58,'opcion1','2026-02-03 21:31:41.268000','2026-02-03 21:31:41.268000',3,7,NULL),
(61,'hola','2026-02-03 21:42:34.581000','2026-02-03 21:42:34.581000',1,13,NULL),
(71,'comentario desde el modal, no dsde la vista detalle, soy Root','2026-02-05 18:07:56.692000','2026-02-05 18:07:56.692000',1,5,NULL),
(72,'vamos a probarrr','2026-02-05 18:14:06.347000','2026-02-05 18:14:06.347000',4,1,NULL),
(73,'holaaaaa222','2026-02-05 18:15:08.284000','2026-02-05 18:15:08.284000',4,1,NULL),
(78,'12345678','2026-02-05 18:34:05.798000','2026-02-05 18:34:05.798000',4,13,NULL),
(81,'comentario desde el modal, no dsde la vista detalle, soy Root','2026-02-05 18:37:07.809000','2026-02-05 18:37:07.809000',1,3,NULL),
(82,'holaaaaa222','2026-02-05 18:40:00.608000','2026-02-05 18:40:00.608000',4,1,NULL),
(83,'no','2026-02-05 18:40:23.340000','2026-02-05 18:40:23.340000',1,3,NULL),
(85,'otrooo','2026-02-05 18:53:24.743000','2026-02-05 18:53:24.743000',1,3,NULL),
(86,'ultimo comentario desde aqui','2026-02-05 18:56:53.661000','2026-02-05 18:56:53.661000',4,1,NULL),
(93,'arribaaa','2026-02-05 19:32:15.090000','2026-02-05 19:32:15.090000',1,3,NULL),
(97,'ARRIBA2','2026-02-05 19:38:42.716000','2026-02-05 19:38:42.716000',1,3,NULL),
(101,'Comento yo','2026-02-07 12:11:40.070000','2026-02-07 12:11:40.070000',4,14,NULL),
(104,'Comentario 1','2026-06-07 18:05:32.359567','2026-06-07 18:05:32.359592',3,15,NULL),
(105,'Comentario 2','2026-06-10 13:59:53.675857','2026-06-10 13:59:53.675884',2,15,NULL),
(106,'Un comentario más','2026-06-11 10:32:20.334522','2026-06-11 10:32:20.334564',2,13,NULL),
(107,'@root  , Root tienes razón, hola','2026-06-11 10:47:01.938493','2026-06-11 10:47:01.938520',2,13,NULL);
/*!40000 ALTER TABLE `posts_comment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `posts_event`
--

DROP TABLE IF EXISTS `posts_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `posts_event` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `description` longtext NOT NULL,
  `location` varchar(255) DEFAULT NULL,
  `event_date` datetime(6) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `max_participants` int(10) unsigned NOT NULL CHECK (`max_participants` >= 0),
  `hobby_id` bigint(20) NOT NULL,
  `organizer_id` int(11) NOT NULL,
  `is_canceled` tinyint(1) NOT NULL,
  `image` varchar(100) DEFAULT NULL,
  `level` varchar(20) NOT NULL,
  `is_online` tinyint(1) NOT NULL,
  `stream_url` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `posts_event_hobby_id_b8ab5ba2_fk_profiles_hobby_id` (`hobby_id`),
  KEY `posts_event_organizer_id_bb06bd1c_fk_auth_user_id` (`organizer_id`),
  CONSTRAINT `posts_event_hobby_id_b8ab5ba2_fk_profiles_hobby_id` FOREIGN KEY (`hobby_id`) REFERENCES `profiles_hobby` (`id`),
  CONSTRAINT `posts_event_organizer_id_bb06bd1c_fk_auth_user_id` FOREIGN KEY (`organizer_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `posts_event`
--

LOCK TABLES `posts_event` WRITE;
/*!40000 ALTER TABLE `posts_event` DISABLE KEYS */;
INSERT INTO `posts_event` VALUES
(1,'OSTEOPATIA','jalar y no parar','santa clara','2026-01-24 12:00:00.000000','2026-01-24 11:47:01.028000',10,32,1,0,'','beginner',0,NULL),
(2,'Quedada nocturna para OKYU','Quedada nocturna para OKYU','Aqui','2026-01-24 22:37:00.000000','2026-01-24 11:57:21.994000',15,24,1,0,'','beginner',0,NULL),
(4,'QUIROMASAJE','QUIROMASAJE','santa clara','2026-01-25 08:59:00.000000','2026-01-24 12:05:03.827000',20,5,3,0,'','beginner',0,NULL),
(5,'Subir QUIROMASAJE','QUIROMASAJE al Teide de espaldas.','santa clara','2026-01-25 13:19:00.000000','2026-01-24 13:19:20.039000',5,5,1,1,'','beginner',0,NULL),
(6,'REIKY','REIKY entre todos','santa clara','2026-01-25 14:04:00.000000','2026-01-24 14:05:05.947000',2,29,1,1,'','beginner',0,NULL),
(7,'MANUPUNTURATODOS CONTRA TODOS','MANUPUNTURA TODOS CONTRA TODOS','aqui','2026-01-25 23:53:00.000000','2026-01-25 09:53:38.434000',10,16,1,1,'','beginner',0,NULL),
(8,'COPIA: KINESIOLOGIA','KINESIOLOGIA','santa clara','2026-01-25 23:59:00.000000','2026-01-25 10:53:12.899000',20,28,3,0,'','beginner',0,NULL),
(9,'SACROCRANEAL','SACROCRANEAL','Peloponeso','2026-01-26 12:45:00.000000','2026-01-25 12:52:01.544000',10,33,1,0,'events/portafolio1.png','beginner',0,NULL),
(10,'OSTEOP','OSTEOP','En Marte','2026-01-28 19:51:00.000000','2026-01-27 19:51:38.169000',10,32,4,0,'events/de_vacaciones2025.jpg','beginner',0,NULL),
(11,'quedada sin foto','quedada sinn foto','aqui','2026-01-28 20:06:00.000000','2026-01-27 20:06:39.285000',10,29,4,0,'','beginner',0,NULL),
(12,'QUEDADA DE PRUEBA x','UNA QUEDADA PARA PRUEBAS','santa clara','2026-01-31 23:14:00.000000','2026-01-31 09:14:31.665000',5,34,1,0,'','beginner',0,NULL),
(13,'Quedada nocturna para Senderismo a OVNIS','Quedada nocturna para Senderismo a OVNIS','VSK','2026-01-31 22:30:00.000000','2026-01-31 09:26:55.820000',10,10,3,0,'events/Foto_del_2025-02-16_11-29-07.078087.jpeg','beginner',0,NULL),
(14,'COPIA: quedada sin foto','quedada sinn foto','aqui','2026-02-28 20:06:00.000000','2026-02-01 12:04:03.794000',5,16,4,1,'','beginner',0,NULL),
(15,'PROPUESTA PROPONIDA','PROPONIDA LA PROPUESTA','VSK','2026-02-02 12:21:00.000000','2026-02-01 12:21:30.685000',3,7,4,0,'events/repository-open-graph-template_Wg3DGhG.png','beginner',0,NULL),
(16,'Cagar boca abajo','a ver quien puede hacerlo','aqui','2026-02-01 23:07:00.000000','2026-02-01 19:08:04.817000',3,25,4,0,'events/Elearning_land_page_Desktop.jpg','beginner',0,NULL),
(17,'Quedada para fotos nocturnas','Hoy hay luna llena y saldra el hombre lobo','VSK','2026-02-01 00:08:00.000000','2026-02-01 19:08:52.233000',3,34,4,0,'events/Grocery_Store.jpg','beginner',0,NULL),
(19,'Evento Django','Evento Django','aqui','2026-02-04 18:42:00.000000','2026-02-03 18:42:13.066000',3,25,1,0,'events/octocat_github.png','beginner',0,NULL),
(20,'PARTIDA DE AJEDREZ HOY','PARTIDA PARA EXPERTOS DE AJEDREZ','VSK','2026-02-07 20:20:00.000000','2026-02-07 12:25:21.184000',3,22,1,0,'events/fondo_navideño.png','expert',0,NULL),
(21,'queda propuesta hoy 7 de febrero','queda propuesta hoy 7 de febrero','VSK','2026-02-07 18:30:00.000000','2026-02-07 13:30:36.270000',6,21,4,0,'events/hubsclicks.png','beginner',0,NULL),
(22,'PATEADA A GUGUI','PATEADA A GUGUI','VSK','2026-02-07 20:19:00.000000','2026-02-07 15:18:20.679000',5,24,3,0,'events/IMG_0955.jpg','advanced',0,NULL),
(23,'AJEDREZ PRINCIPIANTE','AJEDREZ PRINCIPIANTE','aqui','2026-02-07 20:48:00.000000','2026-02-07 15:48:20.498000',5,27,3,0,'events/apple-icon-precomposed.png','beginner',0,NULL),
(24,'MIRAR LAS ESTRELLAS','MIRAR LAS ESTRELLAS','santa clara','2026-02-07 23:36:00.000000','2026-02-07 18:36:49.250000',10,5,3,0,'events/D7D-black.png','all',0,NULL),
(25,'CAMINAR POR EL CAMPO','CAMINAR POR EL CAMPO','aqui','2026-02-07 23:59:00.000000','2026-02-07 18:54:23.874000',5,6,3,0,'events/sftp.jpg','beginner',0,NULL),
(26,'QUIROMASAJE','Quiromasaje viendo el amanecer en Tamadaba.','Plaza Tifariti, Valsequillo','2026-07-27 13:33:00.000000','2026-05-26 12:33:33.851595',10,5,3,0,'events/comfyUI.png','expert',0,NULL),
(27,'Taller presencial y online para todos','Es un taller presencial y por streaming','Valsequillo de Gran Canaria (Centro de terapias Mari Pipi','2026-06-08 22:22:00.000000','2026-06-07 12:13:21.215891',10,10,2,0,'events/octocat_github_OJNfAX6.png','all',1,'https://www.youtube.com/watch?v=D_g88dbCFmE'),
(28,'Taller de prueba online y presencial','Taller de prueba online y presencial, para todos los niveles.','Valsequillo de Gran Canaria (Centro de terapias Mari Pipi).','2026-06-12 10:10:00.000000','2026-06-10 12:17:26.594407',10,10,2,1,'events/octocat_github_11EGwf1.png','all',1,'https://youtu.be/b4tE5aKhtlg'),
(29,'Taller presencial y online para todos','Taller presencial y online para todos','Valsequillo de Gran Canaria (Centro de terapias Mari Pipi)','2026-06-15 10:10:00.000000','2026-06-10 13:41:01.157367',10,8,2,0,'events/hubsclicks_apaisadTranspInvert.png','beginner',1,'https://www.youtube.com/watch?v=Z3oqQPLeLa4');
/*!40000 ALTER TABLE `posts_event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `posts_eventattendance`
--

DROP TABLE IF EXISTS `posts_eventattendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `posts_eventattendance` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `attendance_type` varchar(10) NOT NULL,
  `joined_at` datetime(6) NOT NULL,
  `event_id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `posts_eventattendance_event_id_user_id_7f3dd938_uniq` (`event_id`,`user_id`),
  KEY `posts_eventattendance_user_id_0a8f5d94_fk_auth_user_id` (`user_id`),
  CONSTRAINT `posts_eventattendance_event_id_db0f7dbd_fk_posts_event_id` FOREIGN KEY (`event_id`) REFERENCES `posts_event` (`id`),
  CONSTRAINT `posts_eventattendance_user_id_0a8f5d94_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `posts_eventattendance`
--

LOCK TABLES `posts_eventattendance` WRITE;
/*!40000 ALTER TABLE `posts_eventattendance` DISABLE KEYS */;
INSERT INTO `posts_eventattendance` VALUES
(1,'physical','2026-06-07 15:57:51.983458',2,4),
(2,'physical','2026-06-07 15:57:51.986005',4,1),
(3,'physical','2026-06-07 15:57:51.987742',4,3),
(4,'physical','2026-06-07 15:57:51.991037',4,4),
(5,'physical','2026-06-07 15:57:51.994885',5,1),
(6,'physical','2026-06-07 15:57:51.998424',6,1),
(7,'physical','2026-06-07 15:57:51.999707',6,3),
(8,'physical','2026-06-07 15:57:52.001486',7,1),
(9,'physical','2026-06-07 15:57:52.002212',7,3),
(10,'physical','2026-06-07 15:57:52.002774',7,4),
(11,'physical','2026-06-07 15:57:52.004136',9,1),
(13,'physical','2026-06-07 15:57:52.006040',10,3),
(14,'physical','2026-06-07 15:57:52.006887',10,4),
(15,'physical','2026-06-07 15:57:52.007960',11,3),
(16,'physical','2026-06-07 15:57:52.008506',11,4),
(17,'physical','2026-06-07 15:57:52.009402',13,1),
(18,'physical','2026-06-07 15:57:52.009905',13,3),
(19,'physical','2026-06-07 15:57:52.010847',12,1),
(20,'physical','2026-06-07 15:57:52.011403',12,3),
(21,'physical','2026-06-07 15:57:52.011915',12,4),
(22,'physical','2026-06-07 15:57:52.012763',17,4),
(23,'physical','2026-06-07 15:57:52.013658',16,4),
(25,'physical','2026-06-07 15:57:52.015045',15,3),
(26,'physical','2026-06-07 15:57:52.015555',15,4),
(28,'physical','2026-06-07 15:57:52.017784',19,1),
(30,'physical','2026-06-07 15:57:52.019882',21,4),
(31,'physical','2026-06-07 15:57:52.021205',22,3),
(32,'physical','2026-06-07 15:57:52.022324',20,1),
(33,'physical','2026-06-07 15:57:52.023214',23,3),
(34,'physical','2026-06-07 15:57:52.024091',24,3),
(35,'physical','2026-06-07 15:57:52.024671',24,4),
(36,'physical','2026-06-07 15:57:52.025561',25,3),
(37,'physical','2026-06-07 15:57:52.027105',27,2),
(39,'physical','2026-06-07 15:57:52.029112',26,1),
(40,'physical','2026-06-07 15:57:52.029761',26,3),
(43,'online','2026-06-07 16:25:14.028857',27,4),
(44,'physical','2026-06-07 16:26:02.497576',27,3),
(46,'physical','2026-06-10 12:17:26.597634',28,2),
(47,'online','2026-06-10 12:22:06.605439',28,1),
(48,'physical','2026-06-10 13:41:01.162525',29,2),
(49,'physical','2026-06-11 10:08:14.857776',26,2);
/*!40000 ALTER TABLE `posts_eventattendance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `posts_eventcomment`
--

DROP TABLE IF EXISTS `posts_eventcomment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `posts_eventcomment` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `content` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `event_id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `posts_eventcomment_event_id_5a4b1165_fk_posts_event_id` (`event_id`),
  KEY `posts_eventcomment_user_id_f9a166d1_fk_auth_user_id` (`user_id`),
  CONSTRAINT `posts_eventcomment_event_id_5a4b1165_fk_posts_event_id` FOREIGN KEY (`event_id`) REFERENCES `posts_event` (`id`),
  CONSTRAINT `posts_eventcomment_user_id_f9a166d1_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `posts_eventcomment`
--

LOCK TABLES `posts_eventcomment` WRITE;
/*!40000 ALTER TABLE `posts_eventcomment` DISABLE KEYS */;
INSERT INTO `posts_eventcomment` VALUES
(1,'Os recuerdo que lleveis linterna esta noche!!!','2026-01-24 21:58:05.294000',2,1),
(2,'ok, gracias','2026-01-24 21:59:20.815000',2,4),
(3,'ok, gracias','2026-01-24 22:02:37.173000',2,4),
(4,'Voy a estar alli!!','2026-01-24 22:32:57.239000',2,4),
(5,'Voy a estar alli!!','2026-01-24 22:33:56.836000',2,4),
(6,'PEPE, ya estoy','2026-01-24 22:35:48.700000',2,1),
(7,'PEPE, nos vemos allí, no faltes!!!','2026-01-24 22:59:38.667000',4,3),
(8,'POR FAVOR NO FALTES, PEPE!!!','2026-01-24 23:07:41.795000',4,3),
(9,'OK, llevate unas birras!!!','2026-01-24 23:09:24.916000',4,4),
(10,'Hay que llevar comida?','2026-01-25 09:54:17.353000',7,4),
(11,'Tengo dos tableros profesionales, los llevo?','2026-01-25 10:33:22.594000',7,4),
(12,'NO, ya llevo yo alcachofas!!!','2026-01-25 10:43:33.481000',7,1),
(13,'MA APUNTAO YO!','2026-01-25 10:54:17.558000',7,3),
(14,'Comentario pa probar nada mas','2026-01-25 14:58:38.316000',7,4),
(15,'PARA TODOS, LLEVO PISTACHOS?','2026-01-25 16:55:16.550000',7,4),
(16,'No os olvideis de llevar oxigeno, en la luna no hay','2026-01-27 20:28:54.720000',10,4),
(17,'No os olvideis de llevar oxigeno, en la luna no hay','2026-01-27 20:34:48.617000',10,4),
(18,'No os olvideis de llevar oxigeno, en la luna no hay','2026-01-27 20:35:06.128000',10,4),
(19,'No os olvideis de llevar oxigeno, en la luna no hay','2026-01-27 20:38:02.863000',10,4),
(20,'No os olvideis de llevar oxigeno, en la luna no hay','2026-01-27 20:41:44.915000',10,4),
(21,'que fotoazo!!!','2026-01-27 21:05:16.753000',11,3),
(22,'GRACIAS JUAN!!!','2026-01-27 21:10:43.854000',11,4),
(23,'GRACIAS JUAN!!!','2026-01-27 21:11:53.012000',11,4),
(24,'gracias Juan','2026-01-27 21:13:28.268000',11,4),
(25,'Gracias Pepe por responder tan pronto!','2026-01-27 21:18:13.695000',11,3),
(26,'De nada hombre!!!','2026-01-27 21:22:03.094000',11,4),
(27,'claro que si','2026-01-27 21:26:11.423000',11,3),
(28,'A descansar!!!','2026-01-27 21:28:05.511000',11,3),
(29,'Buenas noches Sr.!','2026-01-27 21:43:08.231000',11,4),
(30,'Juan llevate agua','2026-01-31 09:16:04.435000',12,1),
(31,'Gracias Root, llevaré también pistachos','2026-01-31 09:19:17.970000',12,3),
(32,'Valeee! :)','2026-01-31 09:23:54.318000',12,1),
(33,'Juan, soy Pepe, me llevo algo especial?','2026-01-31 09:46:56.570000',13,4),
(34,'Juan, parece que se va solucionando los estilos.','2026-01-31 19:18:39.899000',13,4),
(35,'comentarios alemail','2026-01-31 19:35:46.206000',13,4),
(36,'prueba','2026-01-31 19:42:00.176000',12,3),
(37,'tengo que dejar la quedada, imprevisto familiar','2026-01-31 20:24:27.452000',13,4),
(38,'comentario para recibir email','2026-01-31 20:43:01.761000',13,4),
(39,'hola','2026-01-31 20:56:59.347000',13,4),
(40,'hola','2026-01-31 21:01:30.476000',13,4),
(41,'enviando email prueba para ver los cambios en la View','2026-01-31 21:15:23.360000',13,4),
(42,'enviar comentario despues de limpiar la View y refactorizar emails','2026-01-31 21:23:16.066000',13,4),
(43,'Soy Pepe, comentando','2026-02-01 12:58:13.000000',15,4),
(44,'Soy Juan, Pepe','2026-02-01 12:59:22.967000',15,3),
(45,'Me apunto Juan a la partida viendo el amanecer en Tamadaba.','2026-05-26 12:35:36.502313',26,1),
(46,'Gracias Root, nos vemos en Tamadaba.','2026-05-26 12:37:39.688759',26,3),
(47,'Espero está muy bien el taller','2026-06-11 10:09:11.187396',26,2);
/*!40000 ALTER TABLE `posts_eventcomment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `posts_posts`
--

DROP TABLE IF EXISTS `posts_posts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `posts_posts` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `title` varchar(200) DEFAULT NULL,
  `image` varchar(100) DEFAULT NULL,
  `caption` longtext DEFAULT NULL,
  `location` varchar(100) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` int(11) NOT NULL,
  `slug` varchar(255) DEFAULT NULL,
  `category_id` bigint(20) DEFAULT NULL,
  `video` varchar(100) DEFAULT NULL,
  `video_url` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `posts_posts_created_f2a76c_idx` (`created_at` DESC),
  KEY `posts_posts_user_id_6fb39a_idx` (`user_id`),
  KEY `posts_posts_category_id_80ce22b1_fk_profiles_hobby_id` (`category_id`),
  CONSTRAINT `posts_posts_category_id_80ce22b1_fk_profiles_hobby_id` FOREIGN KEY (`category_id`) REFERENCES `profiles_hobby` (`id`),
  CONSTRAINT `posts_posts_user_id_b88d85ff_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `posts_posts`
--

LOCK TABLES `posts_posts` WRITE;
/*!40000 ALTER TABLE `posts_posts` DISABLE KEYS */;
INSERT INTO `posts_posts` VALUES
(1,'ROOT es le mejor','posts_images/2026/02/01/momento_perfecto.png','Primer post, me lo he inventado todo, es para ver como se hace.','aqui','2026-01-17 18:35:59.080000','2026-02-01 10:36:23.478000',1,'post-root-none',29,NULL,NULL),
(2,NULL,'posts_images/2026/01/18/de_vacaciones2025.jpg','De vacaciones: El texto se basa en un fragmento de la obra De finibus bonorum et malorum (Sobre los límites del bien y del mal) de Marco Tulio Cicerón, escrito en el siglo I a.C.  El pasaje original fue alterado al eliminar sílabas y letras, convirtiéndolo en un texto ininteligible en latín, pero con una distribución natural de letras que simula un texto legible. El fragmento más conocido comienza con:\r\n\"Lorem ipsum dolor sit amet, consectetur adipiscing elit...\"','santa clara','2026-01-18 10:08:26.275000','2026-01-24 10:50:11.489000',3,NULL,9,NULL,NULL),
(3,'Aprendiendo Django','posts_images/2026/01/18/conquer_academy.png','What is Lorem Ipsum?\r\nLorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry\'s standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.','santa clara','2026-01-18 11:14:21.949000','2026-01-24 10:49:53.377000',3,NULL,25,NULL,NULL),
(4,'Viva la PEPA!!!','posts_images/2026/01/18/Kazam_screenshot_00001.png','Lorem Ipsum\r\n\"Neque porro quisquam est qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit...\"\r\n\"There is no one who loves pain itself, who seeks after it and wants to have it, simply because it is pain...\"','aqui','2026-01-18 11:59:17.713000','2026-01-29 20:20:46.997000',2,NULL,31,NULL,NULL),
(5,NULL,'posts_images/2026/01/18/conquer_academy_ET009hv.png','What is Lorem Ipsum?\r\nLorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry\'s standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.','santa clara','2026-01-18 18:55:55.863000','2026-01-24 10:50:57.074000',4,NULL,21,NULL,NULL),
(7,'Titulo opcional 1','posts_images/2026/02/01/proyecto_css_gathsession.png','Es la opción 1 de publicaciones','VSK','2026-02-01 13:11:37.978000','2026-02-01 13:11:37.978000',4,NULL,28,NULL,NULL),
(11,'titulo 13 publicado','posts_images/2026/02/01/header_bussines_agency.jpg','estoy aqui y alli','aqui','2026-02-01 19:09:48.925000','2026-02-01 19:09:48.925000',4,NULL,31,NULL,NULL),
(12,'TITULO 14 PUBLICADO','posts_images/2026/02/01/NFT_marketplace_XFOuOEP.jpg','DESARROLLO POR DECIR ALGO','VSK','2026-02-01 19:10:30.771000','2026-02-01 19:10:30.771000',4,NULL,32,NULL,NULL),
(13,'OTRA PUBLICACION','posts_images/2026/02/01/I_bW.jpeg','AJEDREZ A PORRILLO VIVA!!!','santa clara','2026-02-01 19:37:03.837000','2026-02-01 19:37:03.837000',4,NULL,5,NULL,NULL),
(14,'AVER SI ES LA ULTIMA','posts_images/2026/02/01/Foto_del_2025-02-16_11-42-08.942916.jpeg','A VER SI ES LA ULTIMA FOTO POR HOY','VSK','2026-02-01 19:37:42.163000','2026-02-01 19:37:42.163000',4,NULL,10,NULL,NULL),
(15,'Primer video','','un video inexistente','En VSK','2026-06-07 17:53:12.367699','2026-06-07 17:53:12.367739',3,NULL,5,'posts_videos/2026/06/07/bono_regalo_navidad.mp4',NULL);
/*!40000 ALTER TABLE `posts_posts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `posts_posts_likes`
--

DROP TABLE IF EXISTS `posts_posts_likes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `posts_posts_likes` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `posts_id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `posts_posts_likes_posts_id_user_id_1b1c51fa_uniq` (`posts_id`,`user_id`),
  KEY `posts_posts_likes_user_id_3594de26_fk_auth_user_id` (`user_id`),
  CONSTRAINT `posts_posts_likes_posts_id_2a1b021c_fk_posts_posts_id` FOREIGN KEY (`posts_id`) REFERENCES `posts_posts` (`id`),
  CONSTRAINT `posts_posts_likes_user_id_3594de26_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `posts_posts_likes`
--

LOCK TABLES `posts_posts_likes` WRITE;
/*!40000 ALTER TABLE `posts_posts_likes` DISABLE KEYS */;
INSERT INTO `posts_posts_likes` VALUES
(1,1,1),
(2,1,3),
(3,1,4),
(4,2,1),
(6,2,4),
(7,3,1),
(8,3,2),
(9,4,1),
(56,4,2),
(10,4,3),
(12,5,1),
(13,5,3),
(14,5,4),
(19,13,1),
(55,13,2),
(35,14,3),
(16,14,4),
(54,15,2);
/*!40000 ALTER TABLE `posts_posts_likes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `profiles_follow`
--

DROP TABLE IF EXISTS `profiles_follow`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `profiles_follow` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `follower_id` bigint(20) NOT NULL,
  `following_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `profiles_follow_follower_id_following_id_a05b9ee1_uniq` (`follower_id`,`following_id`),
  KEY `profiles_follow_following_id_de27ec0e_fk_profiles_userprofile_id` (`following_id`),
  CONSTRAINT `profiles_follow_follower_id_e33ccfca_fk_profiles_userprofile_id` FOREIGN KEY (`follower_id`) REFERENCES `profiles_userprofile` (`id`),
  CONSTRAINT `profiles_follow_following_id_de27ec0e_fk_profiles_userprofile_id` FOREIGN KEY (`following_id`) REFERENCES `profiles_userprofile` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `profiles_follow`
--

LOCK TABLES `profiles_follow` WRITE;
/*!40000 ALTER TABLE `profiles_follow` DISABLE KEYS */;
INSERT INTO `profiles_follow` VALUES
(4,'2026-01-18 10:52:52.314000',3,4),
(6,'2026-01-18 10:53:29.576000',3,1),
(8,'2026-01-18 11:58:03.183000',1,2),
(9,'2026-01-18 12:20:14.531000',2,4),
(10,'2026-01-18 12:20:22.937000',2,3),
(11,'2026-01-22 19:09:13.562000',4,3),
(13,'2026-01-22 21:04:16.966000',1,4),
(14,'2026-01-22 21:05:07.296000',4,1);
/*!40000 ALTER TABLE `profiles_follow` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `profiles_hobby`
--

DROP TABLE IF EXISTS `profiles_hobby`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `profiles_hobby` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` longtext NOT NULL,
  `slug` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `profiles_hobby`
--

LOCK TABLES `profiles_hobby` WRITE;
/*!40000 ALTER TABLE `profiles_hobby` DISABLE KEYS */;
INSERT INTO `profiles_hobby` VALUES
(5,'Quiromasaje','Terapia natural','Quiromasaje'),
(6,'Masaje tradicional tailandeś','Terapia natural','MasajeTradicionalTailandes'),
(7,'Masaje miofascial','Terapia natural','MasajeMiofascial'),
(8,'Masaje Ayurveda2','Terapia natural','MasajeAyurveda'),
(9,'Masaje Abdominal','Terapia natural','MasajeAbdominal'),
(10,'Masaje tántrico','Terapia natural','MasajeTántrico'),
(11,'Acupuntura tradicional china','Terapia natural','AcupunturaTradicionalChina'),
(12,'Acupuntura Tung','Terapia natural','AcupunturaTung'),
(13,'Acupuntura Japonesa','Terapia natural','AcupunturaJaponesa'),
(14,'Acupuntura Toyohari','Terapia natural','AcupunturaToyohari'),
(15,'Acupuntura Coreana','Terapia natural','AcupunturaCoreana'),
(16,'Manupuntura Coreana','Terapia natural','ManupunturaCoreana'),
(17,'Acupuntura Distal','Terapia natural','AcupunturaDistal'),
(18,'Acupuntura de Meridianos','Terapia natural','AcupunturaMeridianos'),
(19,'Acupuntura Craneal','Terapia natural','AcupunturaCraneal'),
(20,'Acupuntura de Manos y tobillos','Terapia natural','AcupunturaManosTobillos'),
(21,'Acupuntura de Ombligo','Terapia natural','AcupunturaOmbligo'),
(22,'Terapia con Ventosas','Terapia natural','TerapiaVentosas'),
(23,'Moxibustión china','Terapia natural','MoxibustiónChina'),
(24,'Okyu','Terapia natural','Okyu'),
(25,'Ontake','Terapia natural','Ontake'),
(26,'Homeopatía','Terapia natural','Homeopatía'),
(27,'Flores de Bach','Terapia natural','Flores de Bach'),
(28,'Kinesiología','Terapia natural','Kinesiología'),
(29,'Reiky','Terapia natural','Reiky'),
(30,'Programación Neurolingüística (PNL)','Terapia natural','Programación Neurolingüística (PNL)'),
(31,'Terapia Avatar','Terapia natural','Terapia Avatar'),
(32,'Osteopatia','Terapia natural','osteopatia'),
(33,'Terapia Craneosacral/Sacrocraneal','Terapia natural','Terapia Craneosacral/Sacrocraneal'),
(34,'Masaje Ayurveda','Terapia natural','Masaje Ayurveda'),
(35,'Cuellopuntura canaria','Creada automáticamente desde biblioteca.','cuellopuntura-canaria'),
(36,'Otras terapias','Otras terapias o disciplinas naturales.','otras-terapias');
/*!40000 ALTER TABLE `profiles_hobby` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `profiles_review`
--

DROP TABLE IF EXISTS `profiles_review`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `profiles_review` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `rating` smallint(5) unsigned NOT NULL CHECK (`rating` >= 0),
  `comment` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `author_id` int(11) NOT NULL,
  `event_id` bigint(20) NOT NULL,
  `recipient_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `profiles_review_event_id_author_id_cf4fce58_uniq` (`event_id`,`author_id`),
  KEY `profiles_review_author_id_229f5ba6_fk_auth_user_id` (`author_id`),
  KEY `profiles_review_recipient_id_70225106_fk_auth_user_id` (`recipient_id`),
  CONSTRAINT `profiles_review_author_id_229f5ba6_fk_auth_user_id` FOREIGN KEY (`author_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `profiles_review_event_id_31c44cb3_fk_posts_event_id` FOREIGN KEY (`event_id`) REFERENCES `posts_event` (`id`),
  CONSTRAINT `profiles_review_recipient_id_70225106_fk_auth_user_id` FOREIGN KEY (`recipient_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `profiles_review`
--

LOCK TABLES `profiles_review` WRITE;
/*!40000 ALTER TABLE `profiles_review` DISABLE KEYS */;
INSERT INTO `profiles_review` VALUES
(1,5,'PArtida fue Genial!!!','2026-01-25 13:40:07.601000',1,4,3),
(2,5,'ok','2026-01-25 14:17:31.666000',4,4,3),
(3,1,'NO fue nadie!!!','2026-01-25 14:21:31.100000',4,2,1),
(4,4,'ok','2026-01-31 22:54:35.955000',4,11,4),
(5,3,'ok','2026-01-31 22:54:46.176000',4,10,4),
(6,4,'ok','2026-01-31 23:27:36.484000',1,12,1),
(7,3,'ok','2026-02-01 13:20:32.857000',4,12,1),
(8,3,'om','2026-02-07 12:22:25.244000',4,15,4),
(9,5,'muy ok','2026-02-07 12:22:36.821000',4,16,4),
(10,3,'opcional','2026-02-07 12:22:49.221000',4,17,4),
(11,5,'ok','2026-02-07 13:13:14.989000',3,15,4),
(12,5,'Super!!!','2026-05-26 11:00:19.950092',1,20,1),
(13,5,'25 km en hora y media, ni corriendo!!!','2026-06-02 10:09:12.793402',3,25,3),
(14,5,'Se merece 5 estrellas','2026-06-11 10:35:53.822896',2,27,2),
(15,3,'Para mi solo 3 estrellas','2026-06-11 10:37:59.410037',3,27,2);
/*!40000 ALTER TABLE `profiles_review` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `profiles_userhobby`
--

DROP TABLE IF EXISTS `profiles_userhobby`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `profiles_userhobby` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `level` varchar(20) NOT NULL,
  `hobby_id` bigint(20) NOT NULL,
  `profile_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `profiles_userhobby_profile_id_hobby_id_0837cf77_uniq` (`profile_id`,`hobby_id`),
  KEY `profiles_userhobby_hobby_id_cb8a975e_fk_profiles_hobby_id` (`hobby_id`),
  CONSTRAINT `profiles_userhobby_hobby_id_cb8a975e_fk_profiles_hobby_id` FOREIGN KEY (`hobby_id`) REFERENCES `profiles_hobby` (`id`),
  CONSTRAINT `profiles_userhobby_profile_id_8d956729_fk_profiles_` FOREIGN KEY (`profile_id`) REFERENCES `profiles_userprofile` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `profiles_userhobby`
--

LOCK TABLES `profiles_userhobby` WRITE;
/*!40000 ALTER TABLE `profiles_userhobby` DISABLE KEYS */;
INSERT INTO `profiles_userhobby` VALUES
(2,'intermediate',5,4),
(4,'advanced',24,3),
(5,'expert',5,3),
(9,'expert',5,1),
(15,'beginner',24,4),
(16,'expert',32,4),
(17,'advanced',5,2),
(19,'intermediate',11,2),
(20,'expert',11,4),
(21,'beginner',6,3),
(22,'beginner',6,2),
(23,'beginner',11,1);
/*!40000 ALTER TABLE `profiles_userhobby` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `profiles_userprofile`
--

DROP TABLE IF EXISTS `profiles_userprofile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `profiles_userprofile` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `profile_picture` varchar(100) NOT NULL,
  `bio` longtext DEFAULT NULL,
  `birth_date` date DEFAULT NULL,
  `location` varchar(100) DEFAULT NULL,
  `website` varchar(200) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` int(11) NOT NULL,
  `address` varchar(255) DEFAULT NULL,
  `mobile` varchar(20) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `numero_socio` varchar(50) DEFAULT NULL,
  `razon_social` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `profiles_userprofile_user_id_616bed88_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `profiles_userprofile`
--

LOCK TABLES `profiles_userprofile` WRITE;
/*!40000 ALTER TABLE `profiles_userprofile` DISABLE KEYS */;
INSERT INTO `profiles_userprofile` VALUES
(1,'profile_pictures/pingu_linux_I8b0QPw.png','Esta es la bio de Root',NULL,'Valsequillo de Gran Canaria','https://pingulinux.com','2026-01-18 09:40:28.755000','2026-06-12 11:06:07.138384',1,'C/ Isla de la Isla, S/N','622404040','928571324',NULL,NULL),
(2,'profile_pictures/Correos.png','Biogrqfia de Admin:El texto se basa en un fragmento de la obra De finibus bonorum et malorum (Sobre los límites del bien y del mal) de Marco Tulio Cicerón, escrito en el siglo I a.C.  El pasaje original fue alterado al eliminar sílabas y letras, convirtiéndolo en un texto ininteligible en latín, pero con una distribución natural de letras que simula un texto legible. El fragmento más conocido comienza con:\r\n\"Lorem ipsum dolor sit amet, consectetur adipiscing elit...\"',NULL,'santa clara','https://webside.com','2026-01-18 09:43:10.344000','2026-06-11 11:41:43.265280',2,NULL,NULL,NULL,NULL,NULL),
(3,'profile_pictures/devin-desktop.png','El texto se basa en un fragmento de la obra De finibus bonorum et malorum (Sobre los límites del bien y del mal) de Marco Tulio Cicerón, escrito en el siglo I a.C.  El pasaje original fue alterado al eliminar sílabas y letras, convirtiéndolo en un texto ininteligible en latín, pero con una distribución natural de letras que simula un texto legible. El fragmento más conocido comienza con:\r\n\"Lorem ipsum dolor sit amet, consectetur adipiscing elit...\"',NULL,'Valsequillo de Gran Canaria','https://webside.com','2026-01-18 09:59:27.175000','2026-06-08 13:53:46.384583',3,'Isla de la Graciosa, 3','679749603','928507721',NULL,NULL),
(4,'profile_pictures/ohm.jpg','class ProfileView(DetailView, FormView):\r\n    model = UserProfile\r\n    template_name = \"general/profile.html\"\r\n    context_object_name = \"user_prof',NULL,'santa clara','https://pingulinux.com','2026-01-18 10:14:09.014000','2026-02-01 13:09:42.419000',4,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `profiles_userprofile` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-18 14:01:33
