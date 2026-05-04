# Requirements Examples

This reference provides complete worked examples covering common scenarios.

## Example 1: Authentication Module

**Code:**
```python
# src/auth.py
def authenticate_user(email, password):
    if not validate_email(email):
        raise InvalidEmailError()
    user = get_user_by_email(email)
    if not user:
        raise UserNotFoundError()
    if not verify_password(password, user.password_hash):
        raise AuthenticationError()
    if user.is_disabled:
        raise AccountDisabledError()
    session = create_session(user)
    return session

MAX_LOGIN_ATTEMPTS = 5
SESSION_TIMEOUT = 3600
```

**Requirements:**
```markdown
### REQ-001: User Email Validation
**Type:** Functional
**Priority:** Critical
**Status:** Implemented
**Implementation:** src/auth.py:validate_email
**Last Validated:** 2026-04-05

**Description:**
System shall validate user email addresses before authentication attempt.

**Verification:**
1. Verify validate_email() function exists in src/auth.py
2. Test with valid email format (RFC 5322 compliant)
3. Test with invalid email formats (missing @, wrong TLD)
4. Verify InvalidEmailError is raised for invalid emails

**Rationale:**
Email validation prevents database pollution and improves user experience.

---

### REQ-002: Password Verification
**Type:** Functional
**Priority:** Critical
**Status:** Implemented
**Implementation:** src/auth.py:verify_password (line 45)
**Last Validated:** 2026-04-05

**Description:**
System shall verify user passwords against stored bcrypt hash.

**Verification:**
1. Verify verify_password() function uses bcrypt
2. Test with correct password - should return True
3. Test with incorrect password - should return False
4. Verify work factor is minimum 12 rounds

**Rationale:**
Bcrypt provides secure password storage resistant to rainbow table attacks.

---

### REQ-003: Account Status Check
**Type:** Functional
**Priority:** Critical
**Status:** Implemented
**Implementation:** src/auth.py:authenticate_user (line 35)
**Last Validated:** 2026-04-05

**Description:**
System shall verify user account is not disabled before authentication.

**Verification:**
1. Test authentication with active user - should succeed
2. Test authentication with disabled user - should raise AccountDisabledError
3. Verify disabled accounts cannot create sessions

**Rationale:**
Account disabled status is important for security and compliance.

---

### REQ-004: Login Attempt Limiting
**Type:** Non-Functional
**Priority:** High
**Status:** Implemented
**Implementation:** src/auth.py:authenticate_user (inferred)
**Last Validated:** 2026-04-05

**Description:**
System shall limit authentication attempts to prevent brute force attacks.

**Verification:**
1. Verify MAX_LOGIN_ATTEMPTS = 5 constant exists
2. Test 5 failed attempts - should be blocked
3. Verify account lockout is temporary or requires admin action

**Rationale:**
Rate limiting protects against credential stuffing attacks.
```

## Example 2: API Module

**Code:**
```python
# src/api/payments.py
@app.route('/api/payments', methods=['POST'])
def create_payment(request):
    data = request.get_json()
    amount = data.get('amount')
    if amount > MAX_PAYMENT_AMOUNT:
        raise ValidationError('Amount exceeds maximum')
    payment = PaymentService.process(amount)
    return jsonify(payment.to_dict()), 201

MAX_PAYMENT_AMOUNT = 10000
```

**Requirement:**
```markdown
### REQ-015: Payment Amount Validation
**Type:** Functional
**Priority:** High
**Status:** Implemented
**Implementation:** src/api/payments.py:create_payment (line 12)
**Last Validated:** 2026-04-05

**Description:**
System shall validate payment amounts and reject requests exceeding maximum allowed amount.

**Verification:**
1. Verify MAX_PAYMENT_AMOUNT = 10000 constant exists
2. Test payment with amount = 10000 - should succeed
3. Test payment with amount = 10001 - should raise ValidationError
4. Verify error message is clear and user-friendly

**Rationale:**
Amount limits prevent fraud and manage financial exposure.
```

## Example 3: Deviation Detection and Synchronization

**Initial Requirements (before code changes):**
```markdown
### REQ-001: User Authentication
**Type:** Functional
**Priority:** Critical
**Status:** Implemented
**Implementation:** src/auth.py:authenticate_user (line 45)
**Last Validated:** 2026-01-15

**Description:**
System shall authenticate users using email and password credentials.

**Verification:**
1. Verify authenticate_user() function exists in src/auth.py
2. Test with valid email and password - should succeed
3. Test with invalid credentials - should raise AuthenticationError
```

**Current Code (after changes):**
```python
# src/auth.py:45
def authenticate_user(email, password, require_2fa=False):
    if not validate_email_format(email):
        raise InvalidEmailError()
    user = get_user_by_email(email)
    if not user or not verify_password(password, user.password_hash):
        raise AuthenticationError()
    if require_2fa:
        send_2fa_code(user.email)
        return {"status": "pending_2fa", "user_id": user.id}
    session = create_session(user)
    return {"status": "authenticated", "token": session.token}
```

**Detected Deviation (DRIFT):**
- Code now has `require_2fa` parameter and Two-Factor Authentication logic
- Requirement doesn't document 2FA capability
- `Last Validated:` is 91 days old

**Synchronized Requirement:**
```markdown
### REQ-001: User Authentication
**Type:** Functional
**Priority:** Critical
**Status:** Implemented
**Implementation:** src/auth.py:authenticate_user (line 45)
**Last Validated:** 2026-04-06
**Last Changed:** 2026-04-06

**Description:**
System shall authenticate users using email and password credentials, with optional Two-Factor Authentication support.

**Verification:**
1. Verify authenticate_user() function exists in src/auth.py
2. Test with valid email and password - should return authenticated status with token
3. Test with invalid credentials - should raise AuthenticationError
4. Test with require_2fa=True - should return pending_2fa status and send code
5. Verify email validation is performed (test with invalid email)

**Rationale:**
Authentication is the primary security mechanism. Two-Factor Authentication adds an additional layer of security for sensitive operations.

**Change Log:**
- 2026-04-06: [DRIFT FIX] Updated requirement to reflect 2FA capability. Code added require_2fa parameter and conditional 2FA flow. Reason: Feature added to code but requirements not updated. No code changes required - requirements now match implementation.
```

## Example 4: Orphan Code Detection

**Detected Orphan Code:**
```python
# src/payment/webhook_handler.py:23 (newly added, no requirements)
def process_stripe_webhook(event):
    """Handle Stripe webhook events for payment status updates."""
    if event.type == "payment_intent.succeeded":
        order = get_order_by_payment_id(event.data.object.id)
        order.status = "paid"
        order.save()
        send_confirmation_email(order.customer_email)
    elif event.type == "payment_intent.failed":
        order = get_order_by_payment_id(event.data.object.id)
        order.status = "payment_failed"
        order.save()
        notify_support(order.id)
```

**Generated New Requirement:**
```markdown
### REQ-048: Stripe Webhook Processing
**Type:** Functional
**Priority:** High
**Status:** Implemented
**Implementation:** src/payment/webhook_handler.py:process_stripe_webhook (line 23)
**Last Validated:** 2026-04-06
**Last Changed:** 2026-04-06

**Description:**
System shall process Stripe webhook events for payment status updates and update order status accordingly.

**Verification:**
1. Verify process_stripe_webhook() function exists in src/payment/webhook_handler.py
2. Test with payment_intent.succeeded event - order status updated to "paid"
3. Test with payment_intent.failed event - order status updated to "payment_failed"
4. Verify confirmation email sent on successful payment
5. Verify support notification sent on failed payment

**Rationale:**
Webhook processing ensures real-time order status updates from Stripe, improving customer experience and order tracking accuracy.

**Change Log:**
- 2026-04-06: [ORPHAN_CODE] Created requirement for newly discovered webhook processing code. Reason: Code existed without corresponding requirements. No code changes required.
```
