from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskInputSerializer
from .scoring import analyze_tasks
from datetime import datetime
import json

class AnalyzeTasksView(APIView):
    def post(self, request):
        payload = request.data
        tasks = payload.get("tasks")
        strategy = payload.get("strategy", "smart_balance")
        if not isinstance(tasks, list):
            return Response({"error": "Provide 'tasks' as a JSON array in body under 'tasks'."}, status=status.HTTP_400_BAD_REQUEST)

        validated = []
        serializer_cls = TaskInputSerializer
        errors = []
        for i, t in enumerate(tasks):
            s = serializer_cls(data=t)
            if not s.is_valid():
                errors.append({"index": i, "errors": s.errors})
            else:
                validated.append(s.validated_data)
        if errors:
            return Response({"validation_errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        results = analyze_tasks(validated, strategy=strategy, today=datetime.utcnow().date())
        return Response({"strategy": strategy, "results": results})

class SuggestTasksView(APIView):
    def post(self, request):
        payload = request.data
        tasks = payload.get("tasks")
        strategy = payload.get("strategy", "smart_balance")
        if not isinstance(tasks, list):
            return Response({"error": "Provide 'tasks' as a JSON array in body under 'tasks'."}, status=status.HTTP_400_BAD_REQUEST)
        results = analyze_tasks(tasks, strategy=strategy)
        top3 = results[:3]
        suggestions = [{"id": r["id"], "title": r["title"], "score": r["score"], "why": r["explanation"]} for r in top3]
        return Response({"strategy": strategy, "suggestions": suggestions})
