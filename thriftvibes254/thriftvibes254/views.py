from django.http import HttpResponse
from django.templatetags.static import static
import os
from django.shortcuts import render
from django.contrib.auth import logout




def service_worker(request):
    sw_path = static("pwa/service-worker.js")
    file_path = os.path.join(os.getcwd(), sw_path.strip("/"))

    with open(file_path, "r") as f:
        return HttpResponse(
            f.read(),
            content_type="application/javascript"
        )
        
def offline_view(request):
    return render(request, "offline.html")

