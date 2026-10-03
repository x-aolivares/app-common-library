import requests


def obtener_status_red(url: str = "https://httpbin.org/status/200") -> int:
    """
    Realiza una llamada GET a una API pública (httpbin) y devuelve
    el código de estado HTTP de la respuesta.

    Args:
        url: URL de la API pública a consultar. Por defecto apunta a un
             endpoint que devuelve 200 OK.

    Returns:
        int: El código de estado HTTP devuelto por el servidor.

    Raises:
        requests.exceptions.RequestException: Si la solicitud falla.
    """
    response = requests.get(url, timeout=10)
    return response.status_code
