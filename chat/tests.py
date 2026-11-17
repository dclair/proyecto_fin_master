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

    def test_create_group_conversation(self):
        url = reverse("api-groups-create")
        payload = {
            "name": "Grupo de Acupuntura",
            "user_ids": [self.user1.id, self.user2.id, self.user3.id]
        }
        response = self.client.post(url, payload, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["is_group"])
        self.assertEqual(response.data["name"], "Grupo de Acupuntura")

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
