from email.message import EmailMessage


def make_message(
    from_address: str,
    to_address: str | list[str],
    subject: str = 'No subject',
    body: str = '',
    content_type: str = 'plain',
) -> EmailMessage:
    msg = EmailMessage()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject

    if content_type not in ('plain', 'html'):
        raise ValueError(f'{content_type!a} is an unknown content type.')

    msg.add_alternative(body, subtype=content_type)

    return msg
