# SSL Certificate Setup Guide for ovovex.com

## Prerequisites

Before setting up SSL, ensure the following:

1. **Domain Configuration**
   - Your domain `ovovex.com` and `www.ovovex.com` DNS A records point to your server's IP address
   - DNS propagation is complete (can take up to 48 hours)

2. **Server Requirements**
   - Ubuntu/Debian Linux server
   - Root or sudo access
   - Nginx installed
   - Ports 80 and 443 open on firewall

3. **Application Ready**
   - Django application running on port 8000 (using Gunicorn)
   - Static files collected to `/home/husain/Desktop/ovovex/staticfiles/`

## Quick Setup (Automated)

### Step 1: Check DNS Configuration

```bash
# Check if domain points to your server
dig +short ovovex.com
dig +short www.ovovex.com

# Compare with your server IP
curl ifconfig.me
```

### Step 2: Run SSL Setup Script

```bash
# Navigate to project directory
cd /home/husain/Desktop/ovovex

# Run the setup script with sudo
sudo bash setup-ssl.sh
```

The script will:
- Install Certbot and dependencies
- Configure Nginx
- Obtain SSL certificates from Let's Encrypt
- Set up automatic renewal
- Configure HTTPS redirects

### Step 3: Follow Prompts

You'll be asked to:
1. Enter your email address (for certificate expiration notifications)
2. Agree to Let's Encrypt Terms of Service

## Manual Setup (Step by Step)

If you prefer manual setup or the automated script fails:

### 1. Install Certbot

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Configure Nginx

```bash
# Copy the Nginx configuration
sudo cp /home/husain/Desktop/ovovex/nginx/ovovex.conf /etc/nginx/sites-available/ovovex.com

# Enable the site
sudo ln -s /etc/nginx/sites-available/ovovex.com /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 3. Obtain SSL Certificate

```bash
# Run Certbot with Nginx plugin
sudo certbot --nginx -d ovovex.com -d www.ovovex.com
```

Follow the prompts:
- Enter your email address
- Agree to Terms of Service (Y)
- Choose whether to share email with EFF (optional)
- Select option 2 to redirect HTTP to HTTPS

### 4. Verify Certificate

```bash
# Check certificate details
sudo certbot certificates

# Test renewal process
sudo certbot renew --dry-run
```

## Verification

### 1. Test HTTPS Access

```bash
# Test main domain
curl -I https://ovovex.com

# Test www subdomain
curl -I https://www.ovovex.com

# Verify HTTP redirects to HTTPS
curl -I http://ovovex.com
```

### 2. Check SSL Grade

Visit: https://www.ssllabs.com/ssltest/analyze.html?d=ovovex.com

Expected grade: A or A+

### 3. Browser Test

Open in browser:
- https://ovovex.com
- https://www.ovovex.com

Check for:
- ✅ Padlock icon in address bar
- ✅ Certificate valid
- ✅ No mixed content warnings

## Configure Django for Production SSL

Update your Django settings for HTTPS:

```python
# In /home/husain/Desktop/ovovex/ovovex/settings.py

# Security Settings for Production
if not DEBUG:
    # HTTPS Settings
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Additional Security
    X_FRAME_OPTIONS = 'DENY'
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

## Firewall Configuration

Configure UFW firewall:

```bash
# Allow HTTPS
sudo ufw allow 'Nginx Full'

# Remove HTTP only rule if exists
sudo ufw delete allow 'Nginx HTTP'

# Check status
sudo ufw status
```

## Certificate Renewal

Let's Encrypt certificates are valid for 90 days. Certbot automatically sets up renewal.

### Check Renewal Status

```bash
# List all certificates
sudo certbot certificates

# Check renewal timer
sudo systemctl list-timers certbot.timer

# Test renewal (dry run)
sudo certbot renew --dry-run
```

### Manual Renewal

If needed, manually renew:

```bash
sudo certbot renew
sudo systemctl reload nginx
```

## Troubleshooting

### Issue: DNS not resolving

**Solution:**
```bash
# Check DNS records
nslookup ovovex.com
nslookup www.ovovex.com

# Wait for DNS propagation or update DNS at your registrar
```

### Issue: Port 80 blocked

**Solution:**
```bash
# Check if Nginx is listening
sudo netstat -tlnp | grep :80

# Check firewall
sudo ufw status

# Allow port 80
sudo ufw allow 80/tcp
```

### Issue: Certificate validation failed

**Solution:**
```bash
# Ensure webroot directory exists
sudo mkdir -p /var/www/certbot
sudo chown -R www-data:www-data /var/www/certbot

# Verify Nginx config allows .well-known
sudo nginx -t

# Try again
sudo certbot --nginx -d ovovex.com -d www.ovovex.com
```

### Issue: Mixed content warnings

**Solution:**
- Update all `http://` links to `https://` in templates
- Use protocol-relative URLs: `//example.com/resource`
- Or relative URLs: `/static/css/style.css`

### Issue: Renewal fails

**Solution:**
```bash
# Check Nginx is running
sudo systemctl status nginx

# Check certificate expiry
sudo certbot certificates

# Force renewal
sudo certbot renew --force-renewal
```

## SSL Best Practices

1. **Keep Certificates Valid**
   - Monitor expiry dates
   - Ensure auto-renewal works
   - Set up email notifications

2. **Strong Security Headers**
   - Already configured in nginx/ovovex.conf
   - HSTS enabled
   - XSS protection
   - Frame options

3. **Regular Updates**
   ```bash
   sudo apt update
   sudo apt upgrade certbot python3-certbot-nginx
   ```

4. **Monitor SSL Health**
   - Use SSL Labs monthly
   - Check certificate transparency logs
   - Monitor for vulnerabilities

5. **Backup Certificates**
   ```bash
   sudo cp -r /etc/letsencrypt /backup/letsencrypt-$(date +%Y%m%d)
   ```

## Additional Commands

### View Certificate Details

```bash
# Show all certificates
sudo certbot certificates

# Show certificate info
sudo openssl x509 -in /etc/letsencrypt/live/ovovex.com/cert.pem -text -noout
```

### Revoke Certificate

```bash
# If compromised, revoke and get new
sudo certbot revoke --cert-path /etc/letsencrypt/live/ovovex.com/cert.pem
sudo certbot delete --cert-name ovovex.com
```

### Add More Domains

```bash
# Add subdomain to existing certificate
sudo certbot --nginx -d ovovex.com -d www.ovovex.com -d api.ovovex.com
```

## Support Resources

- **Let's Encrypt Documentation**: https://letsencrypt.org/docs/
- **Certbot Documentation**: https://certbot.eff.org/docs/
- **SSL Labs Test**: https://www.ssllabs.com/ssltest/
- **Mozilla SSL Config Generator**: https://ssl-config.mozilla.org/

## Security Checklist

- [ ] SSL certificate installed and valid
- [ ] HTTP redirects to HTTPS
- [ ] HSTS header enabled
- [ ] Security headers configured
- [ ] SSL grade A or higher
- [ ] Auto-renewal configured
- [ ] Django HTTPS settings enabled
- [ ] Firewall configured
- [ ] Regular monitoring set up
- [ ] Backup procedures in place

---

**Last Updated**: October 6, 2025  
**Version**: 1.0
