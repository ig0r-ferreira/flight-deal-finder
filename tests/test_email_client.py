from typing import Any

import pytest

from flight_deals.email_client import make_message
from flight_deals.settings import get_settings

EMAIL_SETTINGS = get_settings().EMAIL


@pytest.fixture
def message_data() -> dict[str, Any]:
    return {
        'from_address': EMAIL_SETTINGS.SENDER,
        'to_address': EMAIL_SETTINGS.RECIPIENTS,
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
