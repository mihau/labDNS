def client_ip(request, handler):
    client_address = handler.client_address[0]

    return client_address

keymaker = client_ip
