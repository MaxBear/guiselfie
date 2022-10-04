dpkg --purge remove python3-selfie-portal
apt update
apt install python3-selfie-portal 
dpkg -L python3-selfie-portal 
systemctl stop apache2
systemctl start apache2
