from smtplib import SMTP
from typing import Any

import pytest
from pytest_mock import MockFixture

from flight_deals.email_client import EmailClient, make_message
from flight_deals.settings import EMAIL, SMTP_SERVER


@pytest.fixture
def message_data() -> dict[str, Any]:
    return {
        'from_address': EMAIL.SENDER,
        'to_address': EMAIL.RECIPIENTS,
        'subject': 'Test',
        'body': 'Testing the creation of a message',
    }


def test_create_message(message_data: dict[str, Any]) -> None:
    message = make_message(**message_data)
    body = message.get_body()
    content = body and str(body.get_payload()).rstrip()

    assert message['From'] == message_data['from_address']
    assert message['To'] == message_data['to_address']
    assert message['Subject'] == message_data['subject']
    assert content == message_data['body'].rstrip()


def test_create_message_must_throw_value_error_for_invalid_content_type(
    message_data: dict[str, Any]
) -> None:
    message_data['content_type'] = 'unknown'
    with pytest.raises(ValueError):
        make_message(**message_data)


def test_send_email(message_data: dict[str, Any], mocker: MockFixture) -> None:
    user = SMTP_SERVER.USERNAME.get_secret_value()
    password = SMTP_SERVER.PASSWORD.get_secret_value()

    email_client = EmailClient(
        smtp_server=SMTP(f'{SMTP_SERVER.HOST}:{SMTP_SERVER.PORT}'),
        credentials=(user, password),
    )

    fake_smtp = mocker.MagicMock(
        **{
            'connect.return_value': (
                220,
                f'{SMTP_SERVER.HOST} ESMTP ready'.encode(),
            ),
            'starttls.return_value': (220, b'2.0.0 Start TLS'),
            'login.return_value': (235, b'2.0.0 OK'),
            'sendmail.return_value': {},
            'quit.return_value': (221, b'2.0.0 Bye'),
        }
    )
    mocker.patch.object(email_client, '_server', fake_smtp)

    msg = make_message(**message_data)
    email_client.send_message(msg)

    assert fake_smtp.connect() == (
        220,
        f'{SMTP_SERVER.HOST} ESMTP ready'.encode(),
    )
    assert fake_smtp.starttls() == (220, b'2.0.0 Start TLS')
    assert fake_smtp.login(user, password) == (235, b'2.0.0 OK')
    assert (
        fake_smtp.sendmail(
            from_addr=msg['From'], to_addrs=msg['To'], msg=msg.as_string()
        )
        == {}
    )

    assert fake_smtp.quit() == (221, b'2.0.0 Bye')
