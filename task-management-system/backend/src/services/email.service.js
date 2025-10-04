/**
 * Email service for sending verification and password reset emails
 * Using SendGrid API
 */

const logger = require('../utils/logger');

// SendGrid configuration
const SENDGRID_API_KEY = process.env.SENDGRID_API_KEY;
const FROM_EMAIL = process.env.FROM_EMAIL || 'noreply@taskmanagement.com';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3001';

// Mock email sending in development
const isDevelopment = process.env.NODE_ENV !== 'production';

/**
 * Send email using SendGrid
 * @param {Object} options - Email options
 * @returns {Promise<boolean>} Success status
 */
async function sendEmail({ to, subject, html, text }) {
  try {
    if (isDevelopment) {
      // In development, just log the email
      logger.info('📧 Email sent (dev mode)', {
        to,
        subject,
        preview: text?.substring(0, 100),
      });
      console.log('\n=== EMAIL PREVIEW ===');
      console.log(`To: ${to}`);
      console.log(`Subject: ${subject}`);
      console.log(`Content:\n${text}`);
      console.log('===================\n');
      return true;
    }

    if (!SENDGRID_API_KEY) {
      logger.error('SendGrid API key not configured');
      throw new Error('Email service not configured');
    }

    // In production, use actual SendGrid
    const sgMail = require('@sendgrid/mail');
    sgMail.setApiKey(SENDGRID_API_KEY);

    await sgMail.send({
      to,
      from: FROM_EMAIL,
      subject,
      text,
      html,
    });

    logger.info('Email sent successfully', { to, subject });
    return true;
  } catch (error) {
    logger.error('Failed to send email', {
      to,
      subject,
      error: error.message,
    });
    throw error;
  }
}

/**
 * Send verification email
 * @param {string} email - User email
 * @param {string} token - Verification token
 */
async function sendVerificationEmail(email, token) {
  const verificationUrl = `${FRONTEND_URL}/verify-email?token=${token}`;

  const subject = 'Verify Your Email - Task Management System';
  
  const text = `
Welcome to Task Management System!

Please verify your email address by clicking the link below:

${verificationUrl}

This link will expire in 24 hours.

If you didn't create an account, please ignore this email.

Best regards,
Task Management Team
  `.trim();

  const html = `
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
    .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
    .button { display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
    .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Welcome to Task Management! 🎉</h1>
    </div>
    <div class="content">
      <h2>Verify Your Email Address</h2>
      <p>Thanks for signing up! Please verify your email address to get started.</p>
      <p>Click the button below to verify your email:</p>
      <a href="${verificationUrl}" class="button">Verify Email Address</a>
      <p>Or copy and paste this link into your browser:</p>
      <p style="word-break: break-all; color: #667eea;">${verificationUrl}</p>
      <p><strong>This link will expire in 24 hours.</strong></p>
      <p>If you didn't create an account, please ignore this email.</p>
    </div>
    <div class="footer">
      <p>© 2024 Task Management System. All rights reserved.</p>
    </div>
  </div>
</body>
</html>
  `.trim();

  return await sendEmail({ to: email, subject, text, html });
}

/**
 * Send password reset email
 * @param {string} email - User email
 * @param {string} token - Reset token
 */
async function sendPasswordResetEmail(email, token) {
  const resetUrl = `${FRONTEND_URL}/reset-password?token=${token}`;

  const subject = 'Reset Your Password - Task Management System';
  
  const text = `
Password Reset Request

We received a request to reset your password for your Task Management System account.

Click the link below to reset your password:

${resetUrl}

This link will expire in 1 hour.

If you didn't request a password reset, please ignore this email or contact support if you have concerns.

Best regards,
Task Management Team
  `.trim();

  const html = `
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
    .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
    .button { display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
    .warning { background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }
    .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🔐 Password Reset Request</h1>
    </div>
    <div class="content">
      <h2>Reset Your Password</h2>
      <p>We received a request to reset your password. Click the button below to create a new password:</p>
      <a href="${resetUrl}" class="button">Reset Password</a>
      <p>Or copy and paste this link into your browser:</p>
      <p style="word-break: break-all; color: #667eea;">${resetUrl}</p>
      <p><strong>This link will expire in 1 hour.</strong></p>
      <div class="warning">
        <strong>⚠️ Security Notice:</strong> If you didn't request this password reset, please ignore this email. Your password will remain unchanged.
      </div>
    </div>
    <div class="footer">
      <p>© 2024 Task Management System. All rights reserved.</p>
    </div>
  </div>
</body>
</html>
  `.trim();

  return await sendEmail({ to: email, subject, text, html });
}

/**
 * Send welcome email after verification
 * @param {string} email - User email
 * @param {string} username - Username
 */
async function sendWelcomeEmail(email, username) {
  const subject = 'Welcome to Task Management System! 🎉';
  
  const text = `
Hello ${username}!

Your email has been verified successfully. Welcome to Task Management System!

You can now:
- Create and manage projects
- Collaborate with team members in real-time
- Track tasks and progress
- Stay organized and productive

Get started now: ${FRONTEND_URL}

Best regards,
Task Management Team
  `.trim();

  const html = `
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
    .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
    .features { background: white; padding: 20px; border-radius: 5px; margin: 20px 0; }
    .feature { margin: 15px 0; padding-left: 30px; position: relative; }
    .feature:before { content: "✓"; position: absolute; left: 0; color: #667eea; font-weight: bold; font-size: 18px; }
    .button { display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
    .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🎉 Welcome Aboard!</h1>
    </div>
    <div class="content">
      <h2>Hello ${username}!</h2>
      <p>Your email has been verified successfully. You're all set to start managing your tasks!</p>
      
      <div class="features">
        <h3>What you can do:</h3>
        <div class="feature">Create and manage projects</div>
        <div class="feature">Collaborate with team members in real-time</div>
        <div class="feature">Track tasks and progress</div>
        <div class="feature">Stay organized and productive</div>
      </div>
      
      <a href="${FRONTEND_URL}" class="button">Get Started</a>
      
      <p>Need help? Check out our <a href="${FRONTEND_URL}/help">help center</a> or contact support.</p>
    </div>
    <div class="footer">
      <p>© 2024 Task Management System. All rights reserved.</p>
    </div>
  </div>
</body>
</html>
  `.trim();

  return await sendEmail({ to: email, subject, text, html });
}

/**
 * Send password changed notification
 * @param {string} email - User email
 */
async function sendPasswordChangedEmail(email) {
  const subject = 'Password Changed - Task Management System';
  
  const text = `
Password Changed Successfully

Your password has been changed successfully.

If you did not make this change, please contact support immediately at support@taskmanagement.com

Best regards,
Task Management Team
  `.trim();

  const html = `
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
    .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
    .alert { background: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 20px 0; }
    .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🔒 Password Changed</h1>
    </div>
    <div class="content">
      <div class="alert">
        <strong>✓ Success!</strong> Your password has been changed successfully.
      </div>
      <p>If you did not make this change, please contact support immediately:</p>
      <p><strong>Email:</strong> support@taskmanagement.com</p>
    </div>
    <div class="footer">
      <p>© 2024 Task Management System. All rights reserved.</p>
    </div>
  </div>
</body>
</html>
  `.trim();

  return await sendEmail({ to: email, subject, text, html });
}

module.exports = {
  sendEmail,
  sendVerificationEmail,
  sendPasswordResetEmail,
  sendWelcomeEmail,
  sendPasswordChangedEmail,
};
