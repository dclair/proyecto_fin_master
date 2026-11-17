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
