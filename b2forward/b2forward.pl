#!/usr/bin/perl

require 'jcode.pl'; 

# POST �󂯎��
read( STDIN, $data, $ENV{ 'CONTENT_LENGTH' } );
$data =~ tr/+/ /;
$data =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack('C', hex($1) )/ge;
&jcode'convert(\$data, 'sjis');


# ���M����
$host = "192.168.1.83";       #�ڑ���̃z�X�g��
$path = "/~one/pytest/b2forward/b2forward.py";           #CGI�Ȃǂւ̃p�X
$port = "80";             #�ڑ���̃|�[�g�ԍ�
$post_data = $data; #POST�ő���f�[�^
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

#���N�G�X�g���b�Z�[�W�̐����Ƒ��M
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

#���X�|���X�f�[�^�̕\��
while (chomp($buf=<SOCK>)) {
  print "$buf\n";
}
close(SOCK);


