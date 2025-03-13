<?php
# FileName="Connection_php_mysql.htm"
# Type="MYSQL"
# HTTP="true"
$hostname_Wamp = "localhost";
$database_Wamp = "concept5";
$username_Wamp = "root";
$password_Wamp = "";
$Wamp = mysql_pconnect($hostname_Wamp, $username_Wamp, $password_Wamp) or trigger_error(mysql_error(),E_USER_ERROR); 
?>