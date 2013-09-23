#!/usr/bin/perl -w

# Dream Cup ����������ץ����(������)

$SCRIPT = "dcserver.cgi";

require '/home/two/gameServer/procserver.ini.pl';

@COMMANDS = (
	"start",
	"kill",
	"reboot",
	"pid_check"
);
@DCS_NAME = (
	"�桼��:ACC����������",
	"00:������",
	"�桼��:�׻�������3",
	"01:�׻�������",
	"�桼��:������"
);


$PASSWD = '***';

local %in;

&Read_Parse(\%in);

my $message;

# �����⡼��
if($in{'mode'} eq 'manual'){
	if($in{'pass'} eq $PASSWD){
		if(open(DATA, ">> $ACT_EXEC_FILE")){
			flock(DATA, 2);
			seek(DATA, 0, 2);
			print DATA $in{'command'}."\n";
			close(DATA);
			$message = qq(<span style="color: #00F">done.</span>);
		}else{
			$message = qq(<span style="color: #F00">open err.</span>);
		}
	}else{
		$message = qq(<span style="color: #F00">Access Failed.</span>);
	}
}elsif($in{'mode'} eq 'exec'){
	if((($in{'server'} == 1 || $in{'server'} == 3 || $in{'command'} == 3)&&($in{'pass'} eq $PASSWD)) || 
	    ($in{'server'} != 1 && $in{'server'} != 3 && $in{'command'} != 3)){
	
	if(open(DATA, ">> $ACT_EXEC_FILE")){
		flock(DATA, 2);
		seek(DATA, 0, 2);
		print DATA $COMMANDS[$in{'command'}]." ".$in{'server'}."\n";
		close(DATA);
		$message = qq(<span style="color: #00F">done.</span>);
	}else{
		$message = qq(<span style="color: #F00">open err.</span>);
	}
	
	}else{
		$message = qq(<span style="color: #F00">Access Failed.</span>);
	}
}elsif($in{'mode'} eq 'renew'){
	$in{'data'} =~ s/\r//g;

	if(open(INI, "+< $DCS_INI_DIR[$in{'server'}]$DCS_INI")){
		flock(INI, 2);
		truncate(INI, 0);
		seek(INI, 0, 0);
		print INI $in{'data'}."\n";
		close(INI);
		$message = qq(<span style="color: #00F">done.</span>);
	}else{
		$message = qq(<span style="color: #F00">open err.</span>);
	}

}elsif($in{'mode'} eq 'edit'){
	if((($in{'server'} == 1 || $in{'server'} == 3)&&($in{'pass'} eq $PASSWD)) || 
	     $in{'server'} != 1 && $in{'server'} != 3){

		print "Content-type: text/html\n\n";
		print "<HTML><HEAD>\n";
		print qq(<meta http-equiv="Content-Type" content="text/html; charset=EUC-JP">\n);
		print "<TITLE>DC�����ꤹ��� ver2</TITLE>\n";
		print "</HEAD><BODY>\n";

		print qq(<H1 style="font-size: 120%; font-weight: normal">DC��������ե�����򤤤¤����!!������Ĥ��Ƥ�!</H1>\n);
		print qq(<P>��$in{'server'}��($DCS_NAME[$in{'server'}])������ե�����򳫤��ޤ���</P>\n);
		print qq(<FORM action="$SCRIPT" method="POST">\n);
		if(open(INI, $DCS_INI_DIR[$in{'server'}].$DCS_INI)){
			flock(INI, 1);
			print qq(<INPUT type="hidden" name="server" value="$in{'server'}">\n);
			print qq(<INPUT type="hidden" name="mode" value="renew">\n);
			print qq(<TEXTAREA NAME="data" ROWS=30 COLS=80>\n);
			while(<INI>){
				print $_;
			}
			print qq(</TEXTAREA>\n);
			
			print qq(<INPUT type="submit" value="������">\n);
			print qq(<INPUT type="reset" value="�ߥꥻ�å�">\n);
			close(INI);
		}else{
			print qq("<P style="color: #F00">open err.</P>\n");
		}

		print qq(</FORM>);
		print qq(<UL>\n);
		print qq(<LI>�񼰥ߥ���Ȥ��ޤ�����ư��ʤ��补</LI>\n);
		print qq(<LI>�񤭴�����ʤ鸵�ξ��֤��᤻��褦���Խ����뤳�ȡ�</LI>\n);
		print qq(<LI>�����ȥ����Ȥ��뤿��ˤϹԤκǽ��";"</LI>\n);
		print qq(<LI><A HREF="$SCRIPT?">��롥</A></LI>\n);
		print qq(</UL>\n);
		
		print "</BODY></HTML>\n";
		exit;
	
	}else{
		$message = qq(<span style="color: #F00">Access Failed.</span>);
	}
}

# ɽ���⡼��
print "Content-type: text/html\n\n";
print "<HTML><HEAD>\n";
print qq(<meta http-equiv="Content-Type" content="text/html; charset=EUC-JP">\n);
print "<TITLE>DC�����楹��� ver2</TITLE>\n";
print "</HEAD><BODY>\n";

print qq(<H1 style="font-size: 120%; font-weight: normal">DC����ư�����꽪λ�������ꤹ���!�����ߤ�Ϣ�Ǥ��ʤ��Ǥ�!</H1>\n);

if($message){
	print qq(<P>$message</P>);
}

print qq(<FORM action="$SCRIPT" method="POST">\n);
print qq(<INPUT type="hidden" name="mode" value="exec">\n);
print qq(<SELECT name="server">\n);
for(my $i=0; $i < @DCS_INI_DIR; $i++){
	print qq(<OPTION VALUE="$i">$i��($DCS_NAME[$i])</OPTION>\n);
}
print qq(</SELECT>\n);
print qq(<SELECT name="command">\n);
for(my $i=0; $i < @COMMANDS; $i++){
	print qq(<OPTION VALUE="$i">$COMMANDS[$i]</OPTION>\n);
}
print qq(</SELECT>\n);
print qq(PASS<INPUT type="password" name="pass" value="" size="8">\n);
print qq(<INPUT type="submit" value="������">\n);
print qq(</FORM>\n);

print qq(<UL>\n);
print qq(<LI style="color: #F00">�������Ƥ⤹���ˤ�ȿ�Ǥ���ʤ������������ޤǺ���30�äۤɤ����롥</LI>\n);
print qq(<LI>30�ä��äƤ��������ʤ���硤���顼�������äƤ����ǽ�������롥</LI>\n);
print qq(<LI><span style="color: #B00">[���ޥ��]start</span> - ����ư�����롥</LI>\n);
print qq(<LI><span style="color: #B00">[���ޥ��]kill</span> - ����λ�����롥</LI>\n);
print qq(<LI><span style="color: #B00">[���ޥ��]reboot</span> - ����Ƶ�ư�����롥</LI>\n);
print qq(<LI><span style="color: #B00">[���ޥ��]pid_check</span> - ������λ�����������뤫�����å���������е�ư�����롥���˥ѥ���ɤ�ɬ�ס�</LI>\n);
print qq(<LI><span style="color: #F00">��1</span>��<span style="color: #F00">��3</span>�ϰ��̳������ˤĤ������˥ѥ���ɤ�ɬ�ס�</LI>\n);
print qq(<LI>ͽ���Ѥλ�����⥻�åȤ����Τ��̡���Ʊ�����Ѥ��ǽ��</LI>\n);
print qq(</UL>\n);

print qq(<FORM action="$SCRIPT" method="POST">\n);
print qq(<INPUT type="hidden" name="mode" value="edit">\n);
print qq(<P>\n);
print qq(<SELECT name="server">\n);
for(my $i=0; $i < @DCS_INI_DIR; $i++){
	print qq(<OPTION VALUE="$i">$i��($DCS_NAME[$i])</OPTION>\n);
}
print qq(</SELECT>\n);
print qq(������ե������\n);
print qq(<INPUT type="submit" value="���Խ�">\n);
print qq(PASS<INPUT type="password" name="pass" value="" size="8">\n);
print qq(</P>\n);
print qq(</FORM>\n);

print qq(<UL>\n);
print qq(<LI>ư���ǧ�Ϥ����������ʤ���������㤤�Ȼפ��롥</LI>\n);
print qq(<LI>����ե�����򹹿������顤����Ƶ�ư�����ʤ���Фʤ�ʤ�(��ư�ǤϤ��ʤ��ΤǼ�ư��)��</LI>\n);
print qq(<LI><A HREF="$SCRIPT?">���Υڡ��������ɤ��롥</A></LI>\n);
print qq(</UL>\n);

print qq(<H2 style="font-size: 100%; font-weight: normal">�����ơ�����</H2>\n);
print qq(<UL>\n);

if(open(DATA, $ACT_ROOT_FILE)){
	flock(DATA, 1);
	my $i=0;
	while(<DATA>){
		if($_ =~ /(\d+)/){
			print qq(<LI>��$i: <span style="color: #f00">��ư��($1)</span></LI>\n);
		}else{
			print qq(<LI>��$i: �����</LI>\n);
		}
		$i++;
	}
	close(DATA);
}else{
	print qq(<LI>open err.</LI>\n);
}

print qq(</UL>\n);

print qq(<H2 style="font-size: 100%; font-weight: normal">�ƻ��</H2>\n);

print qq(<PRE>\n);
if(open(DATA, "|tail -n 10 $LOG_FILE")){
	while(<DATA>){
		print $_;
	}
	close(DATA);
}else{
	print qq(open err.\n);
}
print qq(</PRE>\n);
print qq(<UL>\n);
print qq(<LI><A HREF="procserverlog.cgi?">���ƤΥ��򸫤�</A></LI>\n);
print qq(</UL>\n);

print qq(<H2 style="font-size: 100%; font-weight: normal">���ޥ�ɤ�ľ���Ǥ�����</H2>\n);

print qq(<FORM action="$SCRIPT" method="POST">\n);
print qq(<INPUT type="hidden" name="mode" value="manual">\n);
print qq(COMMAND<INPUT type="text" name="command" value="" size="16">\n);
print qq(PASS<INPUT type="password" name="pass" value="" size="8">\n);
print qq(<INPUT type="submit" value="������">\n);
print qq(</FORM>\n);

print qq(<UL>\n);
print qq(<LI>���ɤ���������ѡ�</LI>\n);
print qq(</UL>\n);

print qq(<ADDRESS>Apache2 + Perl + (DreamCup)gameServer</ADDRESS>\n);
print "</BODY></HTML>\n";



# ---------- ---------- ---------- ---------- ---------- ----------
#  	Argument analysis ROUTINE
#  		&Read_Parse(%FORM, %COOKIE, $NON_TAG_CHECK);
sub Read_Parse {
    my ($form, $cookie, $tagcheck) = @_;
    my $query_string;

    if ( $ENV{'REQUEST_METHOD'} eq 'POST') {
	if ( $ENV{CONTENT_LENGTH} > 100000){
	    &err("�ǡ������̤�¿�����ޤ���ȯ����û�����Ʋ�������");
	}
	read(STDIN, $query_string, $ENV{CONTENT_LENGTH});
    } else {
	$query_string = $ENV{QUERY_STRING};
    }

    foreach ( split(/&/, $query_string) ) {
	my ($name, $value) = split(/=/, $_);
	if ( ! defined $value ){ $value=""; }
	$value =~ tr/+/ /;
	$value =~ s/%([0-9a-fA-F][0-9a-fA-F])/pack("C", hex($1))/eg;

	if ( defined &jcode::convert ){
	    &jcode::convert(\$value, $charmark);
	}
	
	unless($tagcheck){
		$value =~ s/&/&amp;/g;
		$value =~ s/\"/&quot;/g;
		$value =~ s/</&lt;/g;
		$value =~ s/>/&gt;/g;
	}

	$value =~ s/^[\r\n]+//;
	$value =~ s/[\r\n]+$//;

	if ( exists $form->{$name} ){
	    $form->{$name} .= ",$value";
	} else {
	    $form->{$name} = $value;
	}
    }

    if ( $ENV{HTTP_COOKIE} && $cookie ){
	foreach ( split(/\s*;\s*/,$ENV{HTTP_COOKIE}) ){
	    foreach ( split(/[\+,]/,$_) ){
		my ($name,$value) = split(/=/,$_);
		$value =~ s/%([0-9a-fA-F][0-9a-fA-F])/pack("C", hex($1))/eg;
		&jcode::convert(\$value, $charmark);
		$cookie->{$name} = $value;
	    }
	}
    }
}
