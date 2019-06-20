#!/bin/bash
#Moving receipts to daily bins
NAME=farmer4
mkdir /home/$NAME/Register/receipt_backup
CURRENT_DATE="$(date +%Y-%m-%d)"
echo $CURRENT_DATE
mkdir /home/$NAME/Register/receipt_backup/$CURRENT_DATE
mv /home/$NAME/Register/receipts/* /home/$NAME/Register/receipt_backup/$CURRENT_DATE/

