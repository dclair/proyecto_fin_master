from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from chat.models import Conversation, ConversationParticipant, Message


class ChatAPITests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="terapeuta_1", email="t1@test.com", password="PassComplex123!")
        self.user2 = User.objects.create_user(username="terapeuta_2", email="t2@test.com", password="PassComplex123!")
        self.user3 = User.objects.create_user(username="terapeuta_3", email="t3@test.com", password="PassComplex123!")
        self.client.force_login(self.user1)

    def test_create_one_on_one_conversation(self):
        url = reverse("api-conversations-create")
        response = self.client.post(url, {"user_id": self.user2.id}, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        
        conv_id = response.data["id"]
        conv = Conversation.objects.get(id=conv_id)
        self.assertFalse(conv.is_group)
        self.assertEqual(conv.participants.count(), 2)

    def test_cannot_chat_with_oneself(self):
        url = reverse("api-conversations-create")
        response = self.client.post(url, {"user_id": self.user1.id}, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    def test_group_join_request_creates_notification_and_manage(self):
        from notifications.models import Notification
        from chat.models import GroupJoinRequest

        # Grupo creado por user1 (admin)
        conv = Conversation.objects.create(is_group=True, name="Taller Masaje", admin=self.user1)
        ConversationParticipant.objects.create(conversation=conv, user=self.user1)

        # user2 solicita unirse
        self.client.force_login(self.user2)
        request_url = reverse("api-groups-request-join", kwargs={"conversation_id": conv.id})
        res_req = self.client.post(request_url)
        self.assertEqual(res_req.status_code, 200)

        # Verificar que se creó la notificación para user1 (admin)
        notif = Notification.objects.filter(recipient=self.user1, sender=self.user2, notification_type="chat_request").first()
        self.assertIsNotNone(notif)
        self.assertIn("ha solicitado unirse a tu grupo de chat", notif.message)

        # user1 acepta la solicitud
        self.client.force_login(self.user1)
        join_req = GroupJoinRequest.objects.get(conversation=conv, user=self.user2)
        manage_url = reverse("api-groups-manage-request", kwargs={"request_id": join_req.id})
        res_manage = self.client.post(manage_url, {"action": "accept"}, content_type="application/json")
        self.assertEqual(res_manage.status_code, 200)

        # Verificar que user2 fue añadido al grupo
        self.assertTrue(ConversationParticipant.objects.filter(conversation=conv, user=self.user2).exists())

        # Verificar que user2 recibió notificación de que fue aceptado
        notif_accepted = Notification.objects.filter(recipient=self.user2, sender=self.user1, notification_type="chat_accepted").first()
        self.assertIsNotNone(notif_accepted)
        self.assertIn("ha aceptado tu solicitud", notif_accepted.message)

    def test_event_attendance_physical_adds_to_chat_group(self):
        from posts.models import Event, EventAttendance
        from profiles.models import Hobby

        hobby, _ = Hobby.objects.get_or_create(name="Masaje")
        event = Event.objects.create(
            title="Taller Presencial",
            organizer=self.user1,
            hobby=hobby,
            is_online=True,
            location="Madrid",
            event_date="2027-01-01 10:00:00",
            max_participants=10
        )
        self.assertIsNotNone(event.chat_group)

        # user2 se apunta de forma presencial (physical)
        EventAttendance.objects.create(event=event, user=self.user2, attendance_type="physical")

        # Debe estar en el chat automáticamente
        self.assertTrue(ConversationParticipant.objects.filter(conversation=event.chat_group, user=self.user2).exists())

    def test_message_upload_security_whitelist(self):
        # Crear conversacion
        conv = Conversation.objects.create(is_group=False)
        ConversationParticipant.objects.create(conversation=conv, user=self.user1)
        ConversationParticipant.objects.create(conversation=conv, user=self.user2)

        upload_url = reverse("api-messages-upload", kwargs={"conversation_id": conv.id})

        # 1. Archivo permitido (PDF)
        valid_pdf = SimpleUploadedFile("informe.pdf", b"%PDF-1.4...", content_type="application/pdf")
        res_ok = self.client.post(upload_url, {"file": valid_pdf, "content": "Adjunto informe"})
        self.assertEqual(res_ok.status_code, 201)
        self.assertEqual(res_ok.data["attachment_type"], "document")

        # 2. Archivo peligroso / no permitido (.html o .exe)
        malicious_file = SimpleUploadedFile("exploit.html", b"<script>alert(1)</script>", content_type="text/html")
        res_bad = self.client.post(upload_url, {"file": malicious_file, "content": "Script"})
        self.assertEqual(res_bad.status_code, 400)
        self.assertIn("error", res_bad.data)

    def test_message_delete_permissions(self):
        conv = Conversation.objects.create(is_group=False)
        ConversationParticipant.objects.create(conversation=conv, user=self.user1)
        ConversationParticipant.objects.create(conversation=conv, user=self.user2)

        msg = Message.objects.create(conversation=conv, sender=self.user1, content="Hola")

        delete_url = reverse("api-messages-delete", kwargs={"message_id": msg.id})

        # User2 intenta borrar el mensaje de User1 -> 403 Forbidden
        self.client.force_login(self.user2)
        res_forbidden = self.client.delete(delete_url)
        self.assertEqual(res_forbidden.status_code, 403)

        # User1 (autor) lo borra -> 200 OK
        self.client.force_login(self.user1)
        res_ok = self.client.delete(delete_url)
        self.assertEqual(res_ok.status_code, 200)
        self.assertFalse(Message.objects.filter(id=msg.id).exists())

    def test_protected_attachment_download_permissions(self):
        conv = Conversation.objects.create(is_group=False)
        ConversationParticipant.objects.create(conversation=conv, user=self.user1)
        ConversationParticipant.objects.create(conversation=conv, user=self.user2)

        file = SimpleUploadedFile("informe.pdf", b"%PDF-1.4 test document", content_type="application/pdf")
        msg = Message.objects.create(conversation=conv, sender=self.user1, attachment=file, attachment_type="document")

        download_url = reverse("api-message-attachment", kwargs={"message_id": msg.id})

        # User 1 (participante) -> 200 OK
        self.client.force_login(self.user1)
        res_ok = self.client.get(download_url)
        self.assertEqual(res_ok.status_code, 200)

        # User 3 (NO participante) -> 403 Forbidden
        self.client.force_login(self.user3)
        res_denied = self.client.get(download_url)
        self.assertEqual(res_denied.status_code, 403)

    def test_magic_bytes_rejects_disguised_file(self):
        conv = Conversation.objects.create(is_group=False)
        ConversationParticipant.objects.create(conversation=conv, user=self.user1)
        ConversationParticipant.objects.create(conversation=conv, user=self.user2)

        upload_url = reverse("api-messages-upload", kwargs={"conversation_id": conv.id})

        # Archivo con extension .png pero contenido texto/script (sin magic bytes PNG)
        fake_png = SimpleUploadedFile("fake.png", b"echo 'hack'", content_type="image/png")
        res = self.client.post(upload_url, {"file": fake_png, "content": "Fake"})
        self.assertEqual(res.status_code, 400)
        self.assertIn("firma de bytes", res.data["error"].lower())

    def test_valid_image_reencoded_with_pillow(self):
        import io
        from PIL import Image
        conv = Conversation.objects.create(is_group=False)
        ConversationParticipant.objects.create(conversation=conv, user=self.user1)
        ConversationParticipant.objects.create(conversation=conv, user=self.user2)

        upload_url = reverse("api-messages-upload", kwargs={"conversation_id": conv.id})

        img_io = io.BytesIO()
        image = Image.new("RGB", (100, 100), color="blue")
        image.save(img_io, format="JPEG")
        img_io.seek(0)

        valid_jpg = SimpleUploadedFile("foto.jpg", img_io.getvalue(), content_type="image/jpeg")
        res = self.client.post(upload_url, {"file": valid_jpg, "content": "Foto segura"})
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["attachment_type"], "image")

    def test_message_upload_pdf_includes_attachment_name(self):
        conv = Conversation.objects.create(is_group=False)
        ConversationParticipant.objects.create(conversation=conv, user=self.user1)
        ConversationParticipant.objects.create(conversation=conv, user=self.user2)

        upload_url = reverse("api-messages-upload", kwargs={"conversation_id": conv.id})
        pdf_file = SimpleUploadedFile("documento_importante.pdf", b"%PDF-1.4 sample content", content_type="application/pdf")
        res = self.client.post(upload_url, {"file": pdf_file, "content": "Mira este documento"})
        
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["attachment_type"], "document")
        self.assertIn("attachment_name", res.data)
        self.assertEqual(res.data["attachment_name"], "documento_importante.pdf")

    def test_protected_attachment_download_disposition_options(self):
        conv = Conversation.objects.create(is_group=False)
        ConversationParticipant.objects.create(conversation=conv, user=self.user1)
        ConversationParticipant.objects.create(conversation=conv, user=self.user2)

        pdf_file = SimpleUploadedFile("guia_usuario.pdf", b"%PDF-1.4 sample content", content_type="application/pdf")
        msg = Message.objects.create(conversation=conv, sender=self.user1, attachment=pdf_file, attachment_type="document")

        download_url = reverse("api-message-attachment", kwargs={"message_id": msg.id})
        self.client.force_login(self.user1)

        # Inline view default
        res_inline = self.client.get(download_url)
        self.assertEqual(res_inline.status_code, 200)
        self.assertIn('inline', res_inline.headers.get("Content-Disposition", ""))
        self.assertIn('guia_usuario.pdf', res_inline.headers.get("Content-Disposition", ""))

        # Force download
        res_download = self.client.get(f"{download_url}?download=1")
        self.assertEqual(res_download.status_code, 200)
        self.assertIn('attachment', res_download.headers.get("Content-Disposition", ""))
        self.assertIn('guia_usuario.pdf', res_download.headers.get("Content-Disposition", ""))
