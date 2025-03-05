git clone https://www.github.com/odoo/odoo --depth 1 --branch 18.0 /opt/odoo18/odoo
cd /opt/odoo18
python3 -m venv odoo-venv
source odoo-venv/bin/activate
pip3 install wheel
pip3 install -r odoo/requirements.txt
sudo apt update && sudo apt install -y python3-dev python3-pip   python3-venv libxml2-dev libxslt1-dev libldap2-dev   libsasl2-dev libpq-dev libjpeg-dev libffi-dev libssl-dev   build-essential libevent-dev
python --version
python3.12 --version
deactivate
python3.12 -m venv odoo-venv
source odoo-venv/bin/activate
python --version
deactivate
rm -rf odoo-venv
sudo rm -rf odoo-venv
cd /opt/odoo18
rm -r odoo-venv/
cd
exit]
exit
cd /opt/odoo18
ls
cd /opt/odoo18
python3.12 -m venv odoo-venv
source odoo-venv/bin/activate
python --version
pip3 install wheel
pip3 install -r odoo/requirements.txt
deactivate
mkdir /opt/odoo15/odoo-custom-addons
mkdir /opt/odoo18/odoo-custom-addons
exit
