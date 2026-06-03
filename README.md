# 🎂 Avisos de Cumpleaños

App web para que cada persona se registre con su email y fecha de cumpleaños.
Cuando llega el día, **todos reciben un aviso por email y/o Microsoft Teams**.

---

## Arquitectura

```
index.html  →  Netlify (hosting gratuito)
              ↕ Supabase (DB + Auth)
notify.py   →  GitHub Actions (cron diario 8am)
              ↕ SMTP Email + Teams Webhook
```

---

## Setup paso a paso

### 1. Supabase (base de datos + auth)

1. Crear cuenta en [supabase.com](https://supabase.com) → **New project**
2. Ir a **SQL Editor** y ejecutar el contenido de `supabase_setup.sql`
3. Ir a **Settings → API** y copiar:
   - `Project URL` → será tu `SUPABASE_URL`
   - `anon public` → será tu `SUPABASE_ANON_KEY`
   - `service_role` → será tu `SUPABASE_SERVICE_KEY` (¡mantenerla secreta!)
4. En `index.html`, reemplazar las dos constantes al inicio del script:
   ```js
   const SUPABASE_URL = 'https://TU_PROYECTO.supabase.co'
   const SUPABASE_ANON_KEY = 'TU_ANON_KEY'
   ```

### 2. Microsoft Teams (webhook)

1. En el canal de Teams donde querés recibir avisos:
   **→ ··· → Conectores → Webhooks entrantes → Agregar**
2. Darle un nombre ("Cumpleaños") y copiar la URL generada
3. Esa URL es tu `TEAMS_WEBHOOK_URL`

### 3. Email (Gmail SMTP)

1. En tu cuenta de Google: **Seguridad → Contraseñas de aplicación**
   (Necesitás tener verificación en 2 pasos activada)
2. Crear una contraseña para "Correo > Otro dispositivo"
3. Copiar la clave de 16 caracteres → es tu `SMTP_PASS`

### 4. GitHub (cron automático)

1. Subir esta carpeta a un repositorio en [github.com](https://github.com)
2. Ir a **Settings → Secrets and variables → Actions → New repository secret**
3. Agregar estos secrets:

| Secret               | Valor                              |
|----------------------|------------------------------------|
| `SUPABASE_URL`       | URL de tu proyecto Supabase        |
| `SUPABASE_SERVICE_KEY` | Service Role Key de Supabase     |
| `SMTP_HOST`          | `smtp.gmail.com`                   |
| `SMTP_PORT`          | `587`                              |
| `SMTP_USER`          | tu email de Gmail                  |
| `SMTP_PASS`          | contraseña de aplicación           |
| `TEAMS_WEBHOOK_URL`  | URL del webhook de Teams           |

El workflow corre automáticamente a las **8:00 AM (Argentina)**. También podés correrlo manualmente desde **Actions → Birthday Notifications → Run workflow**.

### 5. Netlify (hosting del frontend)

1. Ir a [netlify.com](https://netlify.com) → **Add new site → Deploy manually**
2. Arrastrar la carpeta del proyecto
3. La app queda disponible en una URL tipo `https://tu-app.netlify.app`

---

## Flujo de usuario

1. Usuario entra a la web → se registra con email, contraseña y fecha de cumpleaños
2. Confirma el email (Supabase lo envía automáticamente)
3. Puede loguearse y ver todos los cumpleaños del equipo
4. Cada mañana, GitHub Actions verifica si hay cumpleaños y envía los avisos

---

## Estructura de archivos

```
├── index.html              # App web (frontend completo)
├── notify.py               # Script de notificaciones
├── requirements.txt        # Dependencias Python
├── supabase_setup.sql      # SQL para crear la tabla en Supabase
└── .github/
    └── workflows/
        └── birthday_check.yml  # Cron de GitHub Actions
```
