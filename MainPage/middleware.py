from django.shortcuts import render

class ExceptionHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Если сервер хочет вернуть 405, мы подменяем его на твой красивый шаблон
        if response.status_code == 405:
            return render(request, 'users/auth/405.html', status=405)
            
        return response