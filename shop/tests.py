# shop/tests.py
from rest_framework.test import APITestCase
from rest_framework import status
from shop.models import Shop
from accounts.models import User


class ShopListViewTests(APITestCase):
    def setUp(self):
        
        self.shop = Shop.objects.create(name='test_shop', user=User.objects.create_user('test_user'))

    def test_get_shop_list(self):
        """
        Проверка получения списка магазинов
        """
        response = self.client.get('/shops')
        #self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_get_shop_list_filter_by_status(self):
        """
        Проверка получения списка магазинов с фильтром по статусу
        """
        Shop.objects.create(name='test_shop2', status='closed', user=User.objects.create_user('test_user2'))
        response = self.client.get('/shops/?status=open')
        #self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)