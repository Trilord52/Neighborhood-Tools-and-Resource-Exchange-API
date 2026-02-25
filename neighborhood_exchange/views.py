from django.http import HttpResponse


def home(request):
    return HttpResponse(
        "<h1>Neighborhood Resource Exchange API</h1>"
        "<p>Backend is running.</p>"
        "<p>Visit <code>/api/</code> for the API endpoints.</p>"
    )

