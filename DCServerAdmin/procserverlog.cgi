#!/usr/bin/perl -w

# Dream Cup ����������ץ����(������)

$SCRIPT = "dcserver.cgi";

require '/home/two/gameServer/procserver.ini.pl';

# ɽ���⡼��
print "Content-type: text/html\n\n";
print "<HTML><HEAD>\n";
print qq(<meta http-equiv="Content-Type" content="text/html; charset=EUC-JP">\n);
print "<TITLE>DC�����楹��� ver2</TITLE>\n";
print "</HEAD><BODY>\n";

print qq(<H1 style="font-size: 120%; font-weight: normal">�ƻ������</H1>\n);
print qq(<P><A HREF="$SCRIPT?">���</A></P>);
print qq(<PRE>\n);
if(open(DATA, $LOG_FILE)){
	flock(DATA, 1);
	while(<DATA>){
		print $_;
	}
	close(DATA);
}else{
	print qq(open err.\n);
}
print qq(</PRE>\n);
print qq(<P><A HREF="$SCRIPT?">���</A></P>);

print qq(<ADDRESS>Apache2 + Perl + (DreamCup)gameServer</ADDRESS>\n);
print "</BODY></HTML>\n";

