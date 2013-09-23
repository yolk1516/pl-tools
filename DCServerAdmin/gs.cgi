#!/usr/bin/perl -w

# **gameServerをウェブ上からコントロールするよ**
#  これ置くディレクトリにgameServer.iniが必要．
#  これ置くディレクトリにprogram.logができるので注意(書き込み属性)．
#  簡単なのは全部同じディレクトリに放り込む．

# gameServerの場所(gameServer.iniとは違っても大丈夫)
#  $GSDIR = "/home/*/gameServer/"
#  $GSSCRIPT = $GSDIR."gameServer";
$GSDIR = "/home/two/gameServer4/";
$GSSCRIPT = $GSDIR."gameServer";
#$GSINI = $GSDIR."gameServer.ini";

# このスクリプト名
$SCRIPT = "gs.cgi";

# PIDファイルを置くディレクトリ
#$GSPIDDIR = "/home/two/public_html/gs/";

# 起動しているかどうか判定するファイル
#$GSPIDFILE = $GSPIDDIR."gs.pid";

# 時間と操作IPをチェックするファイル
$CHECKFILE = $GSPIDDIR."check.dat";

local %in;
&Read_Parse(\%in);

my $pid, $value, $exec;

print "Content-type: text/html\n\n";
print "<HTML><HEAD>\n";
print qq(<meta http-equiv="Refresh" content="30">\n);
print qq(<meta http-equiv="Content-Type" content="text/html; charset=Shift_JIS">\n);
print "<TITLE>DC鯖制御スルヨ</TITLE>\n";
print "</HEAD><BODY>\n";
print qq(<P>DC鯖を起動したり終了させたりするよ!　むやみに連打しないでね!</P>\n);


if(&checkTime){

	if($in{'exec'}){
		if(!&killGameServer){
			&startGameServer;
			print qq(<P style="color: #F00">起動しますた．</P>);
		}else{
			print qq(<P style="color: #00F">停止しますた．</P>);
		}
	}

	if(&pid){
		print qq(<P style="color: #F00">稼動中．</P>);
		$value = "停止";
		$exec = 2;
	}else{
		print qq(<P style="color: #00F">停止中．</P>);
		$value = "始動";
		$exec = 1;
	}

	&form;

}

print<<"_EOT_";
<UL>
<LI>乱暴\な使い方するとjijiさんに迷惑かかるかも．</LI>
<LI>練習場を利用したいときだけ鯖を立て，使用後は鯖を落とす．</LI>
<LI>このページは30秒で勝手にリロードする．</LI>
<LI>既に鯖が19立ってると立てられない．</LI>
<LI><A HREF="$SCRIPT?">操作する前に必ずリロードよろ．</A></LI>
</UL>

<P>TODO</P>
<UL>
<LI>鯖の設定ファイルもいじくれるように．
</UL>
_EOT_

print qq(</BODY>\n);
print qq(</HTML>\n);

exit;

# 割り込み防止 (10秒間 他のホストからのアクセスブロック)
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
		print qq(<P style="color: #0F0">操作した直後なので舞ってね．</P>);
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
	print qq(<P style="color: #0F0">他の人が操作した直後なので10秒ぐらい舞ってね．</P>);
	return 0;
}

# ボタン部分
sub form {

	print qq(<FORM action="$SCRIPT" method="POST">\n);
	print qq(<INPUT type="hidden" name="exec" value="$exec">\n);
	print qq(<INPUT type="submit" value="$value">\n);
	print qq(</FORM>);
	
}

# プロセスを返す
sub pid{
	return `ps ux | awk '/gameServer/ && !/awk/ {print \$2}'`;
}

# 鯖を落とす
sub killGameServer{
	my $pid = &pid;
	if($pid){
		print OUT `kill $pid`;
		return 1;
	}else{
		return 0;
	}
}

# 鯖を立てる
sub startGameServer{
	system("$GSSCRIPT &");
}

# 使ってないけど pidファイルからpidゲット
sub getGsPid {
	my $tmp;
	open(IN, $GSPIDFILE) || return 0;
	while(<IN>){
		$tmp = $_;
	}
	close(IN);
	return $tmp;
}

# 使ってないけど pidファイルを作成
sub makeGsPid {
	my $pid = $_[0];
	open(OUT, ">".$GSPIDFILE) || return 0;
	print OUT $pid;
	close(OUT);
	return 1;
}

# 使ってないけど pidファイルを削除
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
	    &err("データの量が多すぎます。発言を短くして下さい。");
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

