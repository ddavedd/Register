cd /home/farmer3/Register
CURRENT_DATE="$(date +%Y-%m-%d)"
echo $CURRENT_DATE
python register.py >> /home/farmer3/Register/logs/$CURRENT_DATE
