#!/usr/bin/perl -w

# **gameServer���E�F�u�ォ��R���g���[�������**
#  ����u���f�B���N�g����gameServer.ini���K�v�D
#  ����u���f�B���N�g����program.log���ł���̂Œ���(�������ݑ���)�D
#  �ȒP�Ȃ̂͑S�������f�B���N�g���ɕ��荞�ށD

# gameServer�̏ꏊ(gameServer.ini�Ƃ͈���Ă����v)
#  $GSDIR = "/home/*/gameServer/"
#  $GSSCRIPT = $GSDIR."gameServer";
$GSDIR = "/home/two/gameServer4/";
$GSSCRIPT = $GSDIR."gameServer";
#$GSINI = $GSDIR."gameServer.ini";

# ���̃X�N���v�g��
$SCRIPT = "gs.cgi";

# PID�t�@�C����u���f�B���N�g��
#$GSPIDDIR = "/home/two/public_html/gs/";

# �N�����Ă��邩�ǂ������肷��t�@�C��
#$GSPIDFILE = $GSPIDDIR."gs.pid";

# ���ԂƑ���IP���`�F�b�N����t�@�C��
$CHECKFILE = $GSPIDDIR."check.dat";

local %in;
&Read_Parse(\%in);

my $pid, $value, $exec;

print "Content-type: text/html\n\n";
print "<HTML><HEAD>\n";
print qq(<meta http-equiv="Refresh" content="30">\n);
print qq(<meta http-equiv="Content-Type" content="text/html; charset=Shift_JIS">\n);
print "<TITLE>DC�I����X����</TITLE>\n";
print "</HEAD><BODY>\n";
print qq(<P>DC�I���N��������I���������肷���!�@�ނ�݂ɘA�ł��Ȃ��ł�!</P>\n);


if(&checkTime){

	if($in{'exec'}){
		if(!&killGameServer){
			&startGameServer;
			print qq(<P style="color: #F00">�N�����܂����D</P>);
		}else{
			print qq(<P style="color: #00F">��~���܂����D</P>);
		}
	}

	if(&pid){
		print qq(<P style="color: #F00">�ғ����D</P>);
		$value = "��~";
		$exec = 2;
	}else{
		print qq(<P style="color: #00F">��~���D</P>);
		$value = "�n��";
		$exec = 1;
	}

	&form;

}

print<<"_EOT_";
<UL>
<LI>���\\�Ȏg���������jiji����ɖ��f�����邩���D</LI>
<LI>���K��𗘗p�������Ƃ������I�𗧂āC�g�p��͎I�𗎂Ƃ��D</LI>
<LI>���̃y�[�W��30�b�ŏ���Ƀ����[�h����D</LI>
<LI>���ɎI��19�����Ă�Ɨ��Ă��Ȃ��D</LI>
<LI><A HREF="$SCRIPT?">���삷��O�ɕK�������[�h���D</A></LI>
</UL>

<P>TODO</P>
<UL>
<LI>�I�̐ݒ�t�@�C�������������悤�ɁD
</UL>
_EOT_

print qq(</BODY>\n);
print qq(</HTML>\n);

exit;

# ���荞�ݖh�~ (10�b�� ���̃z�X�g����̃A�N�Z�X�u���b�N)
sub checkTime {
	my $lasttime,$nowtime;
	($lasttime) = (stat($CHECKFILE))[9];
	$nowtime = time();
	
#	print qq("$nowtime $lasttime\n");
	if($nowtime - $lasttime > 10){
		open(OUT,">$CHECKFILE") || return 0;
		print OUT $ENV{'REMOTE_ADDR'};
		close(OUT);
		
		return 1;
	}elsif($nowtime - $lasttime < 2){
		print qq(<P style="color: #0F0">���삵������Ȃ̂ŕ����ĂˁD</P>);
		return 0;
	}elsif(open(IN,$CHECKFILE)){
		my $flag = 0;
		while(<IN>){
			if($ENV{'REMOTE_ADDR'} =~ /$_/){
				$flag = 1;
			}
		}
		close(IN);
		if($flag){
			utime($nowtime,$nowtime,$CHECKFILE);
			return 1;
		}
	}
	print qq(<P style="color: #0F0">���̐l�����삵������Ȃ̂�10�b���炢�����ĂˁD</P>);
	return 0;
}

# �{�^������
sub form {

	print qq(<FORM action="$SCRIPT" method="POST">\n);
	print qq(<INPUT type="hidden" name="exec" value="$exec">\n);
	print qq(<INPUT type="submit" value="$value">\n);
	print qq(</FORM>);
	
}

# �v���Z�X��Ԃ�
sub pid{
	return `ps ux | awk '/gameServer/ && !/awk/ {print \$2}'`;
}

# �I�𗎂Ƃ�
sub killGameServer{
	my $pid = &pid;
	if($pid){
		print OUT `kill $pid`;
		return 1;
	}else{
		return 0;
	}
}

# �I�𗧂Ă�
sub startGameServer{
	system("$GSSCRIPT &");
}

# �g���ĂȂ����� pid�t�@�C������pid�Q�b�g
sub getGsPid {
	my $tmp;
	open(IN, $GSPIDFILE) || return 0;
	while(<IN>){
		$tmp = $_;
	}
	close(IN);
	return $tmp;
}

# �g���ĂȂ����� pid�t�@�C�����쐬
sub makeGsPid {
	my $pid = $_[0];
	open(OUT, ">".$GSPIDFILE) || return 0;
	print OUT $pid;
	close(OUT);
	return 1;
}

# �g���ĂȂ����� pid�t�@�C�����폜
sub rmGsPid {
	unlink($GSPIDFILE);
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	Argument analysis ROUTINE
#  		&Read_Parse(%FORM, %COOKIE, $NON_TAG_CHECK);
sub Read_Parse {
    my ($form, $cookie, $tagcheck) = @_;
    my $query_string;

    if ( $ENV{'REQUEST_METHOD'} eq 'POST') {
	if ( $ENV{CONTENT_LENGTH} > 100000){
	    &err("�f�[�^�̗ʂ��������܂��B������Z�����ĉ������B");
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

