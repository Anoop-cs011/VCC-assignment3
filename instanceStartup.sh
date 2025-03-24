sudo apt update && sudo apt -y install git gunicorn3 python3-pip virtualenv
git clone https://github.com/Anoop-cs011/VCC-assignment3.git
cd VCC-assignment3
virtualenv myProjectEnv
source myProjectEnv/bin/activate
pip install -r requirements.txt
python3 mainApp.py
