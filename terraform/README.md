# DigitalOcean Terraform Deployment

Deploy the Meal Planner application to a single DigitalOcean Droplet using Terraform.

## 💰 Cost

**~$6/month** for a single Droplet (s-1vcpu-1gb: 1GB RAM, 1 vCPU, 25GB SSD)

## 📋 Prerequisites

1. **DigitalOcean Account**: [Sign up here](https://www.digitalocean.com/)
2. **DigitalOcean API Token**:
   - Go to API → Tokens/Keys → Generate New Token
   - Give it read/write permissions
   - Save the token securely
3. **SSH Key**:
   ```bash
   # Generate if you don't have one
   ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
   ```
4. **Terraform**: [Install Terraform](https://www.terraform.io/downloads)
5. **API Keys**:
   - OpenAI API key (for recipe parsing)
   - Gemini API key (optional)

## 🚀 Deployment Steps

### 1. Configure Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your values:

```hcl
do_token            = "dop_v1_xxxxxxxxxxxxx"  # Your DO API token
ssh_public_key_path = "~/.ssh/id_rsa.pub"    # Path to your SSH public key
region              = "nyc3"                   # DO region (nyc3, sfo3, etc.)
environment         = "prod"
openai_api_key      = "sk-xxxxxxxxxxxxx"      # Your OpenAI API key
gemini_api_key      = ""                       # Optional
domain_name         = ""                       # Optional custom domain
```

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Preview Changes

```bash
terraform plan
```

### 4. Deploy Infrastructure

```bash
terraform apply
```

Type `yes` when prompted. This will create:
- A Droplet with Ubuntu 22.04
- Firewall rules (ports 22, 80, 443)
- SSH key configuration
- Automated server setup via cloud-init

**Note**: Cloud-init takes 5-10 minutes to complete after the droplet is created.

### 5. Deploy Application Code

After `terraform apply` completes, note the droplet IP address and run:

```bash
chmod +x deploy-initial.sh
./deploy-initial.sh <DROPLET_IP>
```

This script will:
- Wait for cloud-init to finish
- Upload your application code
- Install Python dependencies
- Build the React frontend
- Initialize the database
- Start the backend service

### 6. Access Your Application

Open your browser to: `http://<DROPLET_IP>`

### 7. Migrate Local Data (Optional)

If you have an existing local database with recipes and images, migrate them:

```bash
./migrate-data.sh <DROPLET_IP>
```

This will:
- Backup the remote database (if it exists)
- Upload your local SQLite database
- Upload cached recipe images
- Restart the backend service
- Verify the migration

## 🐛 Troubleshooting Deployment

### Backend Service Failed to Start

If the deployment script shows the backend service failed, it's likely missing gunicorn:

```bash
./fix-backend.sh <DROPLET_IP>
```

Or manually:
```bash
ssh root@<DROPLET_IP>
cd /home/mealplanner/mymealplanner/backend
source venv/bin/activate
pip install gunicorn
systemctl restart mealplanner-backend
```

### Check Backend Logs
```bash
ssh root@<DROPLET_IP> 'journalctl -u mealplanner-backend -n 50'
```

## 🔄 Updating the Application

### Option 1: Use the deploy script on the server

```bash
ssh root@<DROPLET_IP>
cd /home/mealplanner
./deploy.sh
```

### Option 2: Re-run the initial deployment script

```bash
cd terraform
./deploy-initial.sh <DROPLET_IP>
```

### Option 3: Manual deployment

```bash
# SSH into the server
ssh root@<DROPLET_IP>

# Pull code changes (if using git)
cd /home/mealplanner/mymealplanner
# git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Rebuild frontend
cd ../frontend
npm install
VITE_API_URL=https://meal.servais-devos.com npm run build
rm -rf /var/www/mealplanner/*
cp -r dist/* /var/www/mealplanner/

# Restart services
systemctl restart mealplanner-backend
systemctl restart nginx
```

## 🔧 Useful Commands

### View Backend Logs
```bash
ssh root@<DROPLET_IP> 'journalctl -u mealplanner-backend -f'
```

### Check Service Status
```bash
ssh root@<DROPLET_IP> 'systemctl status mealplanner-backend'
```

### Restart Backend
```bash
ssh root@<DROPLET_IP> 'systemctl restart mealplanner-backend'
```

### Check Nginx Configuration
```bash
ssh root@<DROPLET_IP> 'nginx -t'
```

### View Nginx Logs
```bash
ssh root@<DROPLET_IP> 'tail -f /var/log/nginx/access.log'
ssh root@<DROPLET_IP> 'tail -f /var/log/nginx/error.log'
```

## 🌐 Custom Domain Setup (Optional)

If you want to use a custom domain:

1. **Update DNS**: Point your domain's A record to the droplet IP
   ```
   A record: @ → <DROPLET_IP>
   A record: www → <DROPLET_IP>
   ```

2. **Update terraform.tfvars**:
   ```hcl
   domain_name = "yourdomain.com"
   ```

3. **Re-apply Terraform**:
   ```bash
   terraform apply
   ./deploy-initial.sh <DROPLET_IP>
   ```

4. **Install SSL certificate** (optional but recommended):
   ```bash
   ssh root@<DROPLET_IP>
   apt-get install certbot python3-certbot-nginx
   certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

## 🗑️ Destroy Infrastructure

To delete all resources and stop billing:

```bash
terraform destroy
```

Type `yes` when prompted.

## 📊 Project Structure

```
terraform/
├── main.tf                    # Main infrastructure configuration
├── variables.tf               # Input variables
├── outputs.tf                 # Output values (IP, etc.)
├── cloud-init.yaml            # Server initialization script
├── deploy-initial.sh          # Initial deployment script
├── migrate-data.sh            # Migrate local database and images
├── fix-backend.sh             # Fix backend service issues
├── terraform.tfvars.example   # Example configuration
├── terraform.tfvars           # Your actual config (gitignored)
└── README.md                  # This file
```

## 🐛 Troubleshooting

### Cloud-init still running
Wait for cloud-init to complete:
```bash
ssh root@<DROPLET_IP> 'cloud-init status --wait'
```

### Backend service not starting
Check the logs:
```bash
ssh root@<DROPLET_IP> 'journalctl -u mealplanner-backend -n 50'
```

### Frontend showing 404
Make sure the frontend is built and copied:
```bash
ssh root@<DROPLET_IP> 'ls -la /var/www/mealplanner'
```

### API requests failing
Check backend logs and verify Nginx proxy configuration:
```bash
ssh root@<DROPLET_IP> 'cat /etc/nginx/sites-available/mealplanner'
```

### Database errors
Initialize the database manually:
```bash
ssh root@<DROPLET_IP>
cd /home/mealplanner/mymealplanner/backend
source venv/bin/activate
python3 -c "from database import engine, Base; from models import Recipe, MealPlan; Base.metadata.create_all(bind=engine)"
```

## 📝 Notes

- The application runs on port 8000 (backend) and is proxied through Nginx on port 80
- SQLite database is stored at `/home/mealplanner/mymealplanner/backend/sql_app.db`
- Environment variables are stored in `/etc/mealplanner/.env`
- Application logs are in `/var/log/mealplanner/`
- The backend runs as the `mealplanner` user for security

## 🔒 Security Recommendations

1. **Change SSH port**: Edit `/etc/ssh/sshd_config` and change port from 22
2. **Disable root login**: Set `PermitRootLogin no` in `/etc/ssh/sshd_config`
3. **Enable automatic updates**: `dpkg-reconfigure -plow unattended-upgrades`
4. **Set up monitoring**: Consider DigitalOcean monitoring or external services
5. **Regular backups**: Enable DigitalOcean backups or set up custom backup scripts

## 📚 Additional Resources

- [DigitalOcean Documentation](https://docs.digitalocean.com/)
- [Terraform DigitalOcean Provider](https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs)
- [Cloud-init Documentation](https://cloudinit.readthedocs.io/)
