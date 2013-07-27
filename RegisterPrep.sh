sudo apt-get install git
git config --global user.name "David Smits"
git config --global user.email "david.j.smits@gmail.com"
git config --global credential.helper cache
mkdir ~/.ssh
cd ~/.ssh
ssh-keygen -t rsa -C "Farmer8"
read -p "Copy Value in ~/.ssh/id_rsa.pub to Github SSH page before continuing"
mkdir ~/Register
cd ~/Register
git init
git remote add origin git@github.com:ddavedd/Register.git
git pull origin master
sudo apt-get install python-tk
sudo apt-get install python-mysqldb
sudo apt-get install python-pip
sudo pip install django
read -p "Create shortcut on desktop by copying script and changing values of where things are located, then run script from launcher"
read -p "Turn off : hot corner, locked screen saver, show home and trash on desktop"
sudo apt-get install mysql-server
read -p "Comment out bind address to allow networking"
gksudo gedit /etc/mysql/my.cnf
read -p "Create database called thefarm in mysql"
read -p "Grant privelges: GRANT ALL ON *.* TO 'root'@'10.1.10.%' USING PASSWORD; to allow incoming connections, restart database(Reset comp)"
