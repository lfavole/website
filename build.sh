python3 -m pip install --target . -r requirements.txt
python3 -m pip install --target . psycopg[binary,pool]~=3.2
python3 manage.py reload
