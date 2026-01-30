# Gesture Presentation System

A fast, responsive gesture and voice-controlled presentation system. Use hand gestures and voice commands to control slide presentations in real-time with a modern, secure web interface.

## Features

- **Hand Gesture Recognition**: Recognize swipes and hand movements to navigate presentations.
- **Voice Commands**: Say "Next" or "Previous" to advance slides via voice recognition.
- **Web UI Dashboard**: Real-time video feed and action feedback in a responsive web interface.
- **Secure Authentication**: PBKDF2-SHA256 password hashing, rate-limited login, admin-only settings.
- **Admin Password Manager**: Change the admin password securely from the web UI (/admin).
- **Performance Optimized**: Asynchronous detection worker, adaptive frame processing, and low-latency voice recognition.
- **Virtual Camera Support**: Output to a virtual camera for integration with presentation software.

---

## Project Structure

```
GesturePresentationSystem/
├── main.py                    # Legacy entry point (use web_app/backend.py instead)
├── hand_tracker.py            # Hand detection using MediaPipe
├── gesture_controller.py       # Gesture recognition logic
├── voice_controller.py         # Voice command recognition
├── ges.py                     # Gesture enumerations
├── requirements.txt           # Python dependencies
├── .env                       # Environment config (SECRET_KEY, ADMIN_PASSWORD) [KEEP SECRET]
├── .gitignore                 # Git ignore rules (protects secrets)
├── auth.db                    # SQLite credentials store [AUTO-CREATED] [KEEP SECRET]
├── web_app/
│   ├── backend.py             # FastAPI server (main entry point)
│   ├── auth.py                # Authentication & credential storage
│   ├── reset_admin_password.py # Legacy admin password reset script
│   ├── templates/
│   │   ├── login.html         # Login form with password visibility toggle
│   │   ├── index.html         # Dashboard with gesture/voice feedback
│   │   └── admin.html         # Admin settings (change password)
│   └── static/
│       └── css/
│           └── style.css       # Styling
└── scripts/
    ├── hash_password.py        # Utility to generate password hashes
    └── reset_admin_password.py # Reset admin password script
```

---

## Installation

### Prerequisites

- **Python 3.8+** (tested with 3.10)
- **Webcam** (for hand detection)
- **Microphone** (for voice commands)
- **Windows** (pyvirtualcam works best on Windows; macOS/Linux support varies)

### Setup

1. **Clone or download** the repository:
   ```bash
   git clone <repo-url>
   cd GesturePresentationSystem
   ```

2. **(Optional) Create a Python virtual environment**:
   ```powershell
   py -3.10 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```powershell
   py -3.10 -m pip install --upgrade pip
   py -3.10 -m pip install -r requirements.txt
   ```

4. **Configure environment** (recommended):
   - You must set a secure `SECRET_KEY` in your environment before starting the app. Example (PowerShell):
     ```powershell
     # Set a secure random SECRET_KEY for this shell session
     $env:SECRET_KEY = "$(python -c "import secrets; print(secrets.token_urlsafe(32))")"
     # Optionally set the initial admin password (only for first run)
     $env:ADMIN_PASSWORD = "MyP@ssw0rd"
     ```
   - Alternatively, create a `.env` file for local development containing those values—but do not commit `.env` to source control (it's already listed in `.gitignore`).
   - On first run, if `ADMIN_PASSWORD` is provided in the environment it will be migrated into `auth.db` and securely hashed.

---

## Quick Start

### Run the Server

```powershell
cd C:\Users\dell\GesturePresentationSystem
py -3.10 web_app/backend.py
```

**Expected output:**
- Server starts on `http://127.0.0.1:8000`
- Default browser automatically opens to the login page
- You may see console messages about virtual camera, hand detection, and voice initialization

### Log In

- Open **http://127.0.0.1:8000/login** (or your browser should already have it open)
- **Username**: `admin` (not used in current setup, but required by form)
- **Password**: Use the password from your `.env` file (default: `QWERTY@0987`)
- Click **"Show"** to reveal the password as you type

### Use the Dashboard

- **Dashboard** (/): Shows real-time video feed and action feedback
- **Gesture Control**: Perform hand swipes to navigate:
  - Swipe **right** → Next Slide
  - Swipe **left** → Previous Slide
- **Voice Control**: Say **"Next"** or **"Previous"** within earshot of the microphone
- **Admin** (/admin): Change your admin password (requires current password)

### Logout

- Click the **"Logout"** button to end your session
- Or close the browser to automatically expire your session

---

## Password Management

### Change Password (Recommended)

1. Go to **http://127.0.0.1:8000/admin** (after logging in)
2. Enter your current password and your new password (with confirmation)
3. Click **"Change password"**
4. Your new password is hashed and stored in `auth.db` (SQLite)

### Reset Password (Command Line)

If you forget your password, use the command-line helper:

```powershell
# Generate a password hash
py -3.10 scripts/hash_password.py "MyNewP@ssw0rd"
# Output: $pbkdf2-sha256$29000$...

# Apply the hash to the admin account (requires access to the system)
py -3.10 -c "import sys; sys.path.append(r'C:\Users\dell\GesturePresentationSystem'); from web_app import auth; print(auth.set_admin_password(r'$pbkdf2-sha256$29000$...'))"
```

Or use the simpler one-liner:

```powershell
py -3.10 -c "import sys; sys.path.append(r'C:\Users\dell\GesturePresentationSystem'); from web_app import auth; print(auth.set_admin_password('MyNewP@ssw0rd'))"
```

---

## Performance Tuning

The system is optimized for smooth responsiveness on modern hardware:

- **Async Detection Worker**: Hand detection runs in a background thread to keep the video feed responsive
- **Lower Camera Resolution**: Captures at 640×480 (instead of full HD) for faster processing
- **Fast Voice Recognition**: Reduced latency in voice command recognition via shorter phrase limits and pause thresholds
- **Virtual Camera Support**: Outputs to a virtual camera for OBS or presentation software integration

### For Slower Machines

If you experience lag, adjust these settings in `web_app/backend.py`:

```python
# Lower resolution further (try 480 or 320 width)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)

# Reduce virtual camera FPS
fps = 15  # or lower
```

In `voice_controller.py`:

```python
# Longer phrase timeout (trade latency for accuracy)
phrase_time_limit = 3
```

---

## Security Notes

**This project is designed for local development and small-scale use.**

### Current Security Measures

- ✅ Passwords stored as **PBKDF2-SHA256 hashes** (one-way, not reversible)
- ✅ **Rate limiting** on login and admin password-change endpoints (in-memory)
- ✅ **Admin-only access** to `/admin` page
- ✅ **Secure cookies** with HTTPOnly flag (session tokens)
- ✅ **Basic audit logging** of auth events

### For Production Use

⚠️ **Not recommended for public deployment without:**

- Use **HTTPS** (enable `secure=True`, `samesite='Lax'` in `response.set_cookie()`)
- Move credentials to a **managed secrets store** (Azure Key Vault, AWS Secrets Manager, HashiCorp Vault)
- Use a **dedicated auth service** (OAuth 2.0, SAML, or enterprise SSO)
- Move from SQLite to a **production database** with user roles and audit tables
- Implement **Redis-backed rate limiting** (survive process restarts)
- Enable **CSRF protection** and session timeout policies
- Regularly **rotate SECRET_KEY** and audit logs
- Restrict **file permissions** on `.env`, `auth.db`, and logs
- Run behind a **reverse proxy** (nginx, Traefik) with firewall rules

---

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| GET | `/login` | Login page | No |
| POST | `/token` | Authenticate and get session token | No |
| POST | `/logout` | End session | Yes |
| GET | `/` | Dashboard (main page) | Yes |
| GET | `/admin` | Admin settings page | Yes (admin only) |
| POST | `/admin/change_password` | Change admin password | Yes (admin only) |
| GET | `/video_feed` | MJPEG video stream | Yes |
| GET | `/status` | Current action status | Yes |
| POST | `/shutdown` | Gracefully stop the server | Yes |

---

## Troubleshooting

### Server Won't Start

- Ensure Python 3.8+ is installed: `py -3.10 --version`
- Check if port 8000 is available: `netstat -ano | findstr :8000`
- Try a different port: Modify `uvicorn.run(app, host="127.0.0.1", port=8001)` in `backend.py`

### Hand Detection Not Working

- Ensure your webcam is connected and not in use by another app
- Try restarting the server
- Check that `mediapipe` is installed: `py -3.10 -m pip list | grep mediapipe`

### Voice Commands Not Recognized

- Check microphone levels (Windows Settings → Sound)
- Ensure you have an internet connection (Google Speech Recognition requires internet)
- Try speaking louder and more clearly
- For offline use, swap the recognizer in `voice_controller.py` to use `pocketsphinx` (less accurate, but offline)

### Browser Doesn't Open Automatically

- Manually navigate to **http://127.0.0.1:8000/login**
- Or set the default browser and restart the server

### Rate-Limit Errors (429)

- You've made too many login or password-change attempts in a short time
- Wait a few minutes and try again (or restart the server)

---

## Contributing & Extending

- **Add more gestures**: Modify `gesture_controller.py` and `ges.py`
- **Add more voice commands**: Extend `voice_controller.py`
- **Use different detection models**: Replace MediaPipe with YOLOv8 or other frameworks in `hand_tracker.py`
- **Deploy to the cloud**: Containerize with Docker and deploy to Azure, AWS, or similar

---

## License

This project is provided as-is for educational and personal use. Modify and distribute as needed within your organization.

---

## Contact & Support

For issues, questions, or contributions:
- Check the project README for setup guidance
- Review the source code comments for implementation details
- Test in a local environment before deploying to production

---

## Changelog

### Version 1.0 (Current)
- ✅ Async detection worker for smooth responsiveness
- ✅ Secure PBKDF2-SHA256 password hashing with SQLite storage
- ✅ Rate-limited authentication with audit logging
- ✅ Admin web UI for password management
- ✅ Password visibility toggle and strength meter
- ✅ Performance optimized (low resolution, fast voice)
- ✅ Virtual camera support
- ✅ Ready for local sharing and demo use

---

## FAQ

**Q: Can I use this on macOS or Linux?**
A: The core gesture/voice logic works on any OS with Python 3.8+, but `pyvirtualcam` is primarily designed for Windows. On macOS/Linux, you may need to skip virtual camera features or use platform-specific alternatives.

**Q: Can I integrate this with PowerPoint or Google Slides?**
A: Yes. The gesture/voice system simulates keyboard presses (`left`/`right` arrow keys), which work with most presentation software. Test in your target app first.

**Q: How do I deploy this online?**
A: This is designed for **local use only**. For online deployment, harden security significantly (HTTPS, proper auth, secrets management) and deploy behind a reverse proxy/firewall.

**Q: What if I need to change the SECRET_KEY?**
A: Update `.env` and restart the server. Existing session tokens will become invalid, forcing users to log in again.

**Q: Can I add multiple users?**
A: Currently, only one 'admin' user exists. To add multiple users, extend `auth.py` to support user registration and role-based access control in the database.

---

**Enjoy your gesture-controlled presentation system!** 🎉
