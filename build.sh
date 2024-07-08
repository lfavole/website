python3 -m pip install --target . -r requirements.txt
python3 -m pip install --target . psycopg[binary,pool]~=3.2
dnf install -y gettext
python3 manage.py reload
