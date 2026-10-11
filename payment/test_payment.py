from unittest.mock import patch
import pytest
from django.core import mail


@pytest.mark.django_db
@patch('stripe.checkout.Session.create')
def test_stripe_payment_mock(mock_stripe_create):
    mock_stripe_create.return_value = {
        'id': 'cs_test_mocked_id',
        'url': 'https://checkout.stripe.com/test'
    }

    session = mock_stripe_create(
        payment_method_types=['card'],
        mode='payment',
        success_url='http://localhost/success/',
        cancel_url='http://localhost/cancel/',
    )

    assert session['id'] == 'cs_test_mocked_id'
    mock_stripe_create.assert_called_once()


@pytest.mark.django_db
def test_email_sending():
    mail.send_mail(
        subject='Оплата успішна',
        message='Дякуємо за ваше замовлення в книгарні.',
        from_email='admin@bookstore.com',
        recipient_list=['client@example.com'],
    )

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == 'Оплата успішна'