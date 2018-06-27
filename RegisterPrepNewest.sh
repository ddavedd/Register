sudo apt-get install git
sudo apt-get install libcupsys2-dev libcupsimage2-dev libcups2-dev
sudo apt-get install python-tk
sudo apt-get install python-mysqldb
sudo apt-get install python-pip
sudo pip install django
sudo apt-get install mysql-server
git config --global user.name "David Smits"
git config --global user.email "david.j.smits@gmail.com"
git config --global credential.helper cache
mkdir ~/.ssh
cd ~/.ssh
# BEFORE RUNNING CHANGE TO current name
ssh-keygen -t rsa -C "farmername"
read -p "Copy Value in ~/.ssh/id_rsa.pub to Github SSH page before continuing"
mkdir ~/Register
cd ~/Register
git init
git remote add origin git@github.com:ddavedd/Register.git
git pull origin master
read -p "Create shortcut on desktop by creating launcher and use RegisterLaunch.sh script, must change values in script"
read -p "Turn off : hot corner, disable locked screen saver, disable show home and trash on desktop"
read -p "Comment out bind address to allow networking in the file that will be brought up"
gksudo gedit /etc/mysql/my.cnf
read -p "Create database called thefarm in mysql"
read -p "IP address in next instruction may change depending on router type"
read -p "Grant privelges: GRANT ALL ON *.* TO 'root'@'10.1.10.%' IDENTIFIED BY '<password>'; (pw is dave) to allow incoming connections, restart database(Reset comp)"
read -p "Scale setup: make sure scale is plugged in"
read -p "Add to group dialout -> adduser USERNAME dialout"
read -p "Scale is plugged in -> chmod a+rw /dev/ttyUSB0"
read -p "Star printer instructions: More than one step! Download from site (press enter) and sudo make and sudo make install, then bring up CUPS and install ppd file"
firefox www.starmicronics.com/support/Default.aspx?printerCode=TSP100
mkdir ~/Register/receipts
read -p "Bringing up CUPS page next"
firefox localhost:631
read -p "Change default options to include opening cash drawers as well as setting as server default printer"
read -p "Change settings.txt in Register folder to point at the current home of the database"
read -p "Setup cron to save a copy of database every night/week or whatever you like"

