#!/usr/bin/perl

require 'jcode.pl'; 

# POST 受け取る
read( STDIN, $data, $ENV{ 'CONTENT_LENGTH' } );
$data =~ tr/+/ /;
$data =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack('C', hex($1) )/ge;
&jcode'convert(\$data, 'sjis');


# 送信準備
$host = "192.168.1.83";       #接続先のホスト名
$path = "/~one/pytest/b2forward/b2forward.py";           #CGIなどへのパス
$port = "80";             #接続先のポート番号
$post_data = $data; #POSTで送るデータ
$len = length( $data );

use Socket;

$ipaddr = inet_aton( $host );
socket(SOCK, PF_INET, SOCK_STREAM, getprotobyname( 'tcp')) || die;
connect(SOCK, sockaddr_in($port, $ipaddr)) || die;
select(SOCK);
$|=1;
select(STDOUT);

print "Content-Type: text/plain\n\n";
#print "---- sousin mae ----\r\n";
#print $data . "\r\n";

#リクエストメッセージの生成と送信
print SOCK "POST $path HTTP/1.1\r\n";
print SOCK "Accept: */*\r\n";
print SOCK "Referer: http://$host" . "$path\r\n";
print SOCK "Accept-Language: ja,en;q=0.5\r\n";
print SOCK "Content-Type: application/x-www-form-urlencoded\r\n";
print SOCK "Accept-Encoding: gzip, deflate\r\n";
print SOCK "User-Agent: Mozilla/4.0 (compatible; MSIE 6.0; Windows XP)\r\n";
print SOCK "Host: $host\r\n";
print SOCK "Content-Length: $len\r\n";
print SOCK "Connection: Keep-Alive\r\n";
print SOCK "\r\n";
print SOCK "$data\r\n";

#レスポンスデータの表示
while (chomp($buf=<SOCK>)) {
  print "$buf\n";
}
close(SOCK);


