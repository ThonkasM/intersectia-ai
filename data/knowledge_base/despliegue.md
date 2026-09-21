# Despliegue y costos

IntersectIA se despliega con Docker y AWS, priorizando el costo bajo para una demo. Hay tres caminos **alternativos** (no se mezclan):

## Opción A — VM única (la más barata)

Una sola instancia (EC2 **t3.small** o Lightsail) corre **todo** con `docker compose`: nginx (frontend estático + proxy), backend, IA y **Postgres en contenedor**. Un único puerto público (80) y **mismo origen**, así que no hay CORS ni *mixed content*.

## Opción A+ — CloudFormation (EC2 + RDS + CloudFront)

Igual que A pero aprovisionado con CloudFormation; incluye **RDS PostgreSQL** gestionado, **CloudFront (HTTPS sin dominio propio)** e **IAM con permiso de Bedrock**. Cuesta como A más el RDS (unos 13 USD/mes).

## Opción B — Terraform (S3+CloudFront + ECS Fargate + RDS + ALB)

Para escala/producción: el frontend estático va a **S3 + CloudFront** y el **backend + IA** corren como **dos contenedores en la misma task de ECS Fargate** (la IA se llama por `localhost:8000`, por eso van juntos), detrás de un **ALB**. RDS en subred privada.

## IA y Bedrock

- La **decisión** (`/decision`) es una política en memoria (CPU, sin red ni GPU): **$0 extra**, corre junto al backend y **nunca** en AWS Lambda (Lambda no encaja por las conexiones WebSocket persistentes y el estado en memoria).
- El **chat** usa **Amazon Bedrock** solo cuando hay generación; el retriever TF-IDF y la base de conocimiento son locales y gratis. Sin credenciales de Bedrock, el chat degrada offline.
- La política se **entrena durante el build** de la imagen de IA, así no depende de un archivo gitignored.

> El frontend es un export estático de Next.js; se sirve desde nginx, S3+CloudFront o CloudFront delante de la VM. No hay `next start` en producción.
