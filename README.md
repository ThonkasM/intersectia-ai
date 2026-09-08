# IntersectIA AI

AI service for the IntersectIA autonomous intersection demo.

FastAPI service exposing two internal endpoints:

- `/decision` — low-latency traffic-light decision policy called by the NestJS backend.
- `/chat` — educational RAG chatbot about IoT and autonomous vehicles.

Both endpoints are protected by an internal token and are only reachable from the backend.