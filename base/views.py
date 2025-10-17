# base/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import datetime

class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "status": "ok",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "message": "API lista"
        })
