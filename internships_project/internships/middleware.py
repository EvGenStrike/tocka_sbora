from django.shortcuts import redirect
from django.urls import reverse


class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.login_url = reverse('login')
        self.exempt_urls = [
            self.login_url,
            reverse('register'),
        ]

    def __call__(self, request):
        if not request.user.is_authenticated and request.path not in self.exempt_urls:
            return redirect(f'{self.login_url}?next={request.path}')

        response = self.get_response(request)
        return response