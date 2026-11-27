from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from profiles.models import Hobby
from marketplace.models import Listing, SellerReview


class MarketplaceTests(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user(username="vendedor", email="vendedor@test.com", password="PassComplex123!")
        self.buyer = User.objects.create_user(username="comprador", email="comprador@test.com", password="PassComplex123!")
        self.hobby = Hobby.objects.create(name="Fitoterapia", slug="fitoterapia")

        self.listing = Listing.objects.create(
            seller=self.seller,
            hobby=self.hobby,
            title="Camilla de Masaje",
            slug="camilla-de-masaje",
            description="Camilla plegable en perfecto estado",
            price=150.00,
            listing_type="SALE",
            status="AVAILABLE"
        )

    def test_listing_detail_view(self):
        self.client.force_login(self.buyer)
        response = self.client.get(reverse("marketplace:listing_detail", kwargs={"slug": self.listing.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Camilla de Masaje")

    def test_listing_update_permissions(self):
        update_url = reverse("marketplace:listing_update", kwargs={"slug": self.listing.slug})

        # Comprador no es el vendedor -> 403 Forbidden
        self.client.force_login(self.buyer)
        res_forbidden = self.client.get(update_url)
        self.assertEqual(res_forbidden.status_code, 403)

        # Vendedor es el dueño -> 200 OK
        self.client.force_login(self.seller)
        res_ok = self.client.get(update_url)
        self.assertEqual(res_ok.status_code, 200)

    def test_add_seller_review_and_open_redirect_protection(self):
        self.client.force_login(self.buyer)
        review_url = reverse("marketplace:add_seller_review", kwargs={"username": self.seller.username})

        # 1. Enviar reseña con intento de Open Redirect malicioso
        payload = {
            "rating": 5,
            "comment": "Gran vendedor, muy puntual.",
            "next": "https://sitio-malicioso-phishing.com/login"
        }
        response = self.client.post(review_url, payload)

        # Debe crear la reseña
        self.assertTrue(SellerReview.objects.filter(seller=self.seller, reviewer=self.buyer).exists())

        # Debe RECHAZAR la URL externa y redirigir a listing_list
        self.assertRedirects(response, reverse("marketplace:listing_list"), fetch_redirect_response=False)

    def test_cannot_review_oneself(self):
        self.client.force_login(self.seller)
        review_url = reverse("marketplace:add_seller_review", kwargs={"username": self.seller.username})
        response = self.client.post(review_url, {"rating": 5, "comment": "Soy el mejor"})
        
        self.assertFalse(SellerReview.objects.filter(seller=self.seller, reviewer=self.seller).exists())
        self.assertRedirects(response, reverse("marketplace:listing_list"), fetch_redirect_response=False)

    def test_non_staff_cannot_select_or_submit_agora_in_marketplace(self):
        agora, _ = Hobby.objects.get_or_create(name="Ágora", slug="agora")
        from marketplace.forms import ListingForm

        # 1. El queryset del formulario no debe incluir Ágora para usuario común
        form = ListingForm(user=self.seller)
        self.assertNotIn(agora, form.fields["hobby"].queryset)

        # 2. Si intenta forzar Ágora en el POST
        form_post = ListingForm(
            data={
                "hobby": agora.pk,
                "title": "Intento venta institucional",
                "description": "Descripción de prueba para verificar seguridad",
                "price": 99.00,
                "listing_type": "SALE",
                "status": "AVAILABLE",
            },
            user=self.seller,
        )
        self.assertFalse(form_post.is_valid())
        self.assertIn("hobby", form_post.errors)

    def test_staff_can_select_agora_in_marketplace(self):
        agora, _ = Hobby.objects.get_or_create(name="Ágora", slug="agora")
        staff_user = User.objects.create_user(
            username="staff_market", email="staff_m@test.com", password="PassComplex123!", is_staff=True
        )
        from marketplace.forms import ListingForm

        form = ListingForm(user=staff_user)
        self.assertIn(agora, form.fields["hobby"].queryset)

        form_post = ListingForm(
            data={
                "hobby": agora.pk,
                "title": "Publicación Oficial de Equipamiento",
                "description": "Donación institucional o venta oficial",
                "price": 0.00,
                "listing_type": "OTHER",
                "status": "AVAILABLE",
            },
            user=staff_user,
        )
        self.assertTrue(form_post.is_valid(), form_post.errors)
