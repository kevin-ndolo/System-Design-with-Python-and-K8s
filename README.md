# 🎧 System Design with Python and Kubernetes

A full-stack media conversion pipeline built with Python microservices, RabbitMQ, MongoDB GridFS, and Kubernetes. Upload a video, convert it to MP3, and receive an email when it’s ready—all orchestrated across containerized services.

---

## 📦 Project Overview

This demo showcases:

- **Microservice architecture** with clear service boundaries
- **Asynchronous task processing** using RabbitMQ
- **Binary file storage** via MongoDB GridFS
- **Media conversion** using MoviePy
- **JWT-based authentication**
- **Email notifications** via SMTP
- **Kubernetes deployment** with ConfigMaps, Secrets, and Ingress

---

## 🗂️ Folder Structure

```
python/src/
├── auth/           # JWT login service backed by MySQL
├── gateway/        # API entrypoint for upload/download
├── converter/      # RabbitMQ consumer that converts videos to MP3
├── notification/   # RabbitMQ consumer that sends email alerts
├── rabbit/         # RabbitMQ StatefulSet and service manifests
```

---

## 🧠 Architecture Diagram

```
[Client] → [Gateway] → [RabbitMQ] → [Converter] → [RabbitMQ] → [Notification]
              ↓                          ↓              ↓
         [MongoDB GridFS] ← [Video]   [MP3] ← [Conversion] ← [Email]
```

---

## 🔐 Authentication Service (`auth`)

- Flask app with MySQL backend
- `/login` issues JWTs
- `/validate` verifies JWTs
- Credentials stored in `auth.user` table
- JWT secret injected via Kubernetes Secret

---

## 🚪 Gateway Service (`gateway`)

- Uploads video files to MongoDB GridFS
- Publishes conversion jobs to RabbitMQ
- Validates JWTs via `auth` service
- Future: `/download` route for MP3 retrieval

**Upload Flow:**
1. User logs in → receives JWT
2. JWT sent with `Authorization` header
3. Gateway validates token
4. Video stored in GridFS
5. Job published to `video` queue

---

## 🎬 Converter Service (`converter`)

- RabbitMQ consumer for `video` queue
- Retrieves video from GridFS
- Converts to MP3 using MoviePy
- Stores MP3 in GridFS
- Publishes message to `mp3` queue

**Highlights:**
- Uses `VideoFileClip` from MoviePy
- Handles temp files with cleanup
- Publishes durable messages with `delivery_mode=2`

---

## 📧 Notification Service (`notification`)

- RabbitMQ consumer for `mp3` queue
- Sends email via Gmail SMTP
- Credentials injected via Secret
- Uses `email.message.EmailMessage`

**Message Format:**
```json
{
  "video_fid": "<ObjectId>",
  "mp3_fid": "<ObjectId>",
  "username": "user@email.com"
}
```

---

## 🗃️ MongoDB GridFS

- `videos` DB stores raw uploads
- `mp3s` DB stores converted audio
- Accessed via `gridfs.GridFS`
- Files stored in `fs.files` and `fs.chunks`

---

## 🕸️ RabbitMQ

- Deployed as a StatefulSet
- Exposes AMQP (5672) and HTTP UI (15672)
- Queues:
  - `video`: for conversion jobs
  - `mp3`: for notification jobs

---

## 🚀 Deployment Guide

### 1. Build and Push Images
```bash
docker build -t kevindev1/gateway:latest ./gateway
docker build -t kevindev1/converter:latest ./converter
docker build -t kevindev1/notification:latest ./notification
docker build -t kevindev1/auth:latest ./auth

docker push kevindev1/gateway:latest
docker push kevindev1/converter:latest
docker push kevindev1/notification:latest
docker push kevindev1/auth:latest
```

### 2. Apply Kubernetes Manifests
```bash
kubectl apply -f rabbit/manifests/
kubectl apply -f auth/manifests/
kubectl apply -f gateway/manifests/
kubectl apply -f converter/manifests/
kubectl apply -f notification/manifests/
```

---

## 🧪 Demo Commands

### Login
```bash
curl -X POST http://mp3converter.com/login -u kevin@email.com:Qwerty123
```

### Upload
```bash
curl -X POST -F "file=@./test.mp4" \
  -H "Authorization: Bearer <JWT>" \
  http://mp3converter.com/upload
```

### Download (coming soon)
```bash
curl -X GET http://mp3converter.com/download?id=<mp3_fid>
```

---

## 🧠 Design Insights

- **Minikube-friendly**: Uses `host.minikube.internal` to access host services
- **Resilient consumers**: `basic_nack` on failure, `basic_ack` on success
- **Modular manifests**: Each service has its own ConfigMap, Secret, and Deployment
- **GridFS for binary storage**: Avoids filesystem mounts or S3 complexity
- **RabbitMQ for decoupling**: Enables async processing and retry logic

---

## 📚 Future Enhancements

- Implement `/download` route in gateway
- Add MP3 filename metadata
- Add retry logic for failed conversions
- Add user-facing dashboard or status endpoint

---

## 🔐 Secrets & Initialization

This project uses sensitive credentials (e.g. Gmail SMTP, JWT secrets, MySQL passwords) that are **not pushed to GitHub**. You’ll need to create your own Kubernetes Secret manifests for each service:

### Required Secrets

| Service        | Secret Name           | Keys Required                       |
|----------------|----------------------|-------------------------------------|
| `auth`         | `auth-secret`        | `MYSQL_PASSWORD`, `JWT_SECRET`      |
| `gateway`      | `gateway-secret`     | `JWT_SECRET`, `MONGO_URI`           |
| `converter`    | `converter-secret`   | `MONGO_URI`, `RABBITMQ_URI`         |
| `notification` | `notification-secret`| `GMAIL_ADDRESS`, `GMAIL_PASSWORD`   |

These are injected via `envFrom: secretRef:` in each deployment manifest. Example:

```yaml
envFrom:
  - secretRef:
      name: notification-secret
```

> ⚠️ **Note**: Secrets are not included in this repo. You must create them manually using `kubectl create secret` or apply your own manifest files.

---

## 🛠️ MySQL Setup

Before launching the `auth` service, you must initialize the MySQL database manually:

```bash
sudo mysql -u root < auth/init.sql
```

This creates the `auth` database and `user` table required for JWT login. The `auth` container expects this schema to exist before startup.

---

## 🌐 Local Domain Setup (`/etc/hosts`)

To simulate production-like domain routing on your local Minikube cluster, add the following entries to your `/etc/hosts` file:

```plaintext
192.168.49.2 mp3converter.com         # Gateway service domain for uploads/downloads
192.168.49.2 rabbitmq-manager.com    # RabbitMQ UI access via browser
```

> ⚠️ Replace `192.168.49.2` with your actual Minikube IP:
```bash
minikube ip
```

These domains are used by:
- `mp3converter.com`: for `curl` requests to the Gateway service
- `rabbitmq-manager.com`: to open the RabbitMQ dashboard in your browser

This setup allows Ingress to route traffic correctly and lets you test the full flow using real URLs.

---

## 🧠 Expanded Architecture Diagram

Here’s the full orchestration in glorious ASCII:

```
┌────────────┐
│   Client   │
└────┬───────┘
     │
     ▼
┌──────────────┐
│   Gateway    │
│  (Flask API) │
└────┬─────────┘
     │
     │ JWT Validation
     ▼
┌──────────────┐
│    Auth      │
│ (MySQL + JWT)│
└──────────────┘

     ▼
 Video Upload
     ▼
┌────────────────────┐
│ MongoDB GridFS     │
│ - videos DB        │
│ - mp3s DB          │
└────┬───────────────┘
     │
     │ Publish to "video" queue
     ▼
┌────────────────────┐
│   RabbitMQ         │
│ - video queue      │
│ - mp3 queue        │
└────┬───────────────┘
     │
     ▼
┌────────────────────┐
│   Converter        │
│ (MoviePy + GridFS) │
└────┬───────────────┘
     │
     │ Publish to "mp3" queue
     ▼
┌────────────────────┐
│  Notification      │
│ (SMTP via Gmail)   │
└────────────────────┘
     │
     ▼
 Email Sent to User
```

---

## 🧑‍💻 Author

**Kevin** — pragmatic backend builder, DevOps enthusiast, and documentation-first educator.
