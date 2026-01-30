# SpendSense Authentication

## Overview

SpendSense now includes a simple but effective authentication system that requires users to create an account and log in before accessing the application.

## Features

### User Registration
- Users can create a new account with a username and password
- Username validation: 3-20 characters, letters and numbers only
- Password validation: Minimum 6 characters
- Passwords must match during registration
- Automatic login after successful registration

### User Login
- Existing users can log in with their credentials
- Session-based authentication
- Passwords are securely hashed using werkzeug security
- Invalid username/password combination shows clear error message

### User Logout
- Users can log out from any page via the logout button
- Session is cleared upon logout
- Redirects to login page after logout

### Protected Routes
- Main evaluation page (`/`) requires authentication
- Evaluation endpoint (`/evaluate`) requires authentication
- Unauthenticated users are redirected to login page

## User Interface

### Header
- Shows "Welcome, [username]" and logout button when authenticated
- Shows Login and Register links when not authenticated

### Login Page
- Clean form with username and password fields
- Link to registration page for new users
- Error messages for invalid credentials

### Register Page
- Form with username, password, and confirm password fields
- Helper text with password requirements
- Link to login page for existing users
- Validation error messages

## Implementation Details

### Routes

| Route | Method | Description | Requires Auth |
|-------|--------|-------------|---------------|
| `/login` | GET | Display login form | No |
| `/login` | POST | Process login submission | No |
| `/register` | GET | Display registration form | No |
| `/register` | POST | Process registration submission | No |
| `/logout` | GET | Clear session and logout | Yes |
| `/` | GET | Main evaluation form | Yes |
| `/evaluate` | POST | Process evaluation | Yes |

### Security Considerations

- **Password Hashing**: Passwords are hashed using `werkzeug.security.generate_password_hash()`
- **Session Management**: Flask sessions are used with a secret key
- **Login Required**: The `@login_required` decorator protects sensitive routes
- **HTTPS Recommended**: In production, always use HTTPS to protect credentials

### Current Limitations

- **In-Memory Storage**: User accounts are stored in memory and lost when the application restarts
- **No Password Reset**: Users cannot reset forgotten passwords
- **No Account Deletion**: Users cannot delete their accounts
- **Single Server**: Session data is not shared across multiple server instances

## Future Improvements

1. **Database Integration**: Replace in-memory storage with a database (PostgreSQL, SQLite, etc.)
2. **Email Verification**: Verify email addresses during registration
3. **Password Reset**: Add "forgot password" functionality
4. **Account Management**: Allow users to change password, delete account
5. **Session Persistence**: Use Redis or database for session storage
6. **Two-Factor Authentication**: Add optional 2FA for enhanced security
7. **Social Login**: Support Google, GitHub, etc. for authentication

## Testing

The authentication system has 22 comprehensive tests covering:

- Username validation (length, special characters)
- Password validation (minimum length)
- Registration (success, existing username, mismatched passwords)
- Login (success, invalid credentials)
- Authentication requirements (protected routes)
- Logout functionality

Run tests with:
```bash
python -m pytest tests/test_authentication.py -v
```

## Usage Example

1. **Register**: Visit `/register` and create an account
   - Username: `john_doe`
   - Password: `secure_password_123`

2. **Login**: Visit `/login` and enter your credentials

3. **Use**: Access the main evaluation form at `/`

4. **Logout**: Click "Logout" button in the header

## Configuration

### Change Secret Key (Production)

Set the `SECRET_KEY` environment variable:

```bash
export SECRET_KEY="your-super-secret-key-here"
```

### Change Session Configuration

Edit `src/web_app.py` to customize session settings:

```python
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
```

## Migration from No-Auth Version

If you had a previous version without authentication, no data migration is needed. Simply update the code and users will be prompted to register on first login attempt.
