#!/usr/bin/perl -w

# Dream Cup サーバ制御プログラム(制御用)

$SCRIPT = "dcserver.cgi";

require '/home/two/gameServer/procserver.ini.pl';

@COMMANDS = (
	"start",
	"kill",
	"reboot",
	"pid_check"
);
@DCS_NAME = (
	"ユーザ:ACC専用練習場",
	"00:練習場",
	"ユーザ:臨時練習場3",
	"01:臨時練習場",
	"ユーザ:練習場"
);


$PASSWD = '***';

local %in;

&Read_Parse(\%in);

my $message;

# 処理モード
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
		print "<TITLE>DC鯖設定するヨ ver2</TITLE>\n";
		print "</HEAD><BODY>\n";

		print qq(<H1 style="font-size: 120%; font-weight: normal">DC鯖の設定ファイルをいぢくるヨ!!　気をつけてね!</H1>\n);
		print qq(<P>↓$in{'server'}鯖($DCS_NAME[$in{'server'}])の設定ファイルを開きます．</P>\n);
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
			
			print qq(<INPUT type="submit" value="○送信">\n);
			print qq(<INPUT type="reset" value="×リセット">\n);
			close(INI);
		}else{
			print qq("<P style="color: #F00">open err.</P>\n");
		}

		print qq(</FORM>);
		print qq(<UL>\n);
		print qq(<LI>書式ミスるとうまく鯖が動作しないヨ．</LI>\n);
		print qq(<LI>書き換えるなら元の状態に戻せるように編集すること．</LI>\n);
		print qq(<LI>コメントアウトするためには行の最初に";"</LI>\n);
		print qq(<LI><A HREF="$SCRIPT?">戻る．</A></LI>\n);
		print qq(</UL>\n);
		
		print "</BODY></HTML>\n";
		exit;
	
	}else{
		$message = qq(<span style="color: #F00">Access Failed.</span>);
	}
}

# 表示モード
print "Content-type: text/html\n\n";
print "<HTML><HEAD>\n";
print qq(<meta http-equiv="Content-Type" content="text/html; charset=EUC-JP">\n);
print "<TITLE>DC鯖制御スルヨ ver2</TITLE>\n";
print "</HEAD><BODY>\n";

print qq(<H1 style="font-size: 120%; font-weight: normal">DC鯖を起動したり終了させたりするよ!　むやみに連打しないでね!</H1>\n);

if($message){
	print qq(<P>$message</P>);
}

print qq(<FORM action="$SCRIPT" method="POST">\n);
print qq(<INPUT type="hidden" name="mode" value="exec">\n);
print qq(<SELECT name="server">\n);
for(my $i=0; $i < @DCS_INI_DIR; $i++){
	print qq(<OPTION VALUE="$i">$i鯖($DCS_NAME[$i])</OPTION>\n);
}
print qq(</SELECT>\n);
print qq(<SELECT name="command">\n);
for(my $i=0; $i < @COMMANDS; $i++){
	print qq(<OPTION VALUE="$i">$COMMANDS[$i]</OPTION>\n);
}
print qq(</SELECT>\n);
print qq(PASS<INPUT type="password" name="pass" value="" size="8">\n);
print qq(<INPUT type="submit" value="○送信">\n);
print qq(</FORM>\n);

print qq(<UL>\n);
print qq(<LI style="color: #F00">送信してもすぐには反映されない．処理されるまで最大30秒ほどかかる．</LI>\n);
print qq(<LI>30秒たっても処理されない場合，エラーが起こっている可能性がある．</LI>\n);
print qq(<LI><span style="color: #B00">[コマンド]start</span> - 鯖を起動させる．</LI>\n);
print qq(<LI><span style="color: #B00">[コマンド]kill</span> - 鯖を終了させる．</LI>\n);
print qq(<LI><span style="color: #B00">[コマンド]reboot</span> - 鯖を再起動させる．</LI>\n);
print qq(<LI><span style="color: #B00">[コマンド]pid_check</span> - 不正終了した鯖があるかチェックし，あれば起動させる．操作にパスワードが必要．</LI>\n);
print qq(<LI><span style="color: #F00">鯖1</span>と<span style="color: #F00">鯖3</span>は一般開放鯖につき，操作にパスワードが必要．</LI>\n);
print qq(<LI>予備用の鯖設定もセットしたので別々に同時利用も可能．</LI>\n);
print qq(</UL>\n);

print qq(<FORM action="$SCRIPT" method="POST">\n);
print qq(<INPUT type="hidden" name="mode" value="edit">\n);
print qq(<P>\n);
print qq(<SELECT name="server">\n);
for(my $i=0; $i < @DCS_INI_DIR; $i++){
	print qq(<OPTION VALUE="$i">$i鯖($DCS_NAME[$i])</OPTION>\n);
}
print qq(</SELECT>\n);
print qq(の設定ファイルを\n);
print qq(<INPUT type="submit" value="○編集">\n);
print qq(PASS<INPUT type="password" name="pass" value="" size="8">\n);
print qq(</P>\n);
print qq(</FORM>\n);

print qq(<UL>\n);
print qq(<LI>動作確認はしたが，かなり安全性は低いと思われる．</LI>\n);
print qq(<LI>設定ファイルを更新したら，鯖を再起動させなければならない(自動ではやらないので手動で)．</LI>\n);
print qq(<LI><A HREF="$SCRIPT?">このページをリロードする．</A></LI>\n);
print qq(</UL>\n);

print qq(<H2 style="font-size: 100%; font-weight: normal">鯖すてーたす</H2>\n);
print qq(<UL>\n);

if(open(DATA, $ACT_ROOT_FILE)){
	flock(DATA, 1);
	my $i=0;
	while(<DATA>){
		if($_ =~ /(\d+)/){
			print qq(<LI>鯖$i: <span style="color: #f00">起動中($1)</span></LI>\n);
		}else{
			print qq(<LI>鯖$i: 停止中</LI>\n);
		}
		$i++;
	}
	close(DATA);
}else{
	print qq(<LI>open err.</LI>\n);
}

print qq(</UL>\n);

print qq(<H2 style="font-size: 100%; font-weight: normal">監視ログ</H2>\n);

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
print qq(<LI><A HREF="procserverlog.cgi?">全てのログを見る</A></LI>\n);
print qq(</UL>\n);

print qq(<H2 style="font-size: 100%; font-weight: normal">コマンドを直に打ち込む</H2>\n);

print qq(<FORM action="$SCRIPT" method="POST">\n);
print qq(<INPUT type="hidden" name="mode" value="manual">\n);
print qq(COMMAND<INPUT type="text" name="command" value="" size="16">\n);
print qq(PASS<INPUT type="password" name="pass" value="" size="8">\n);
print qq(<INPUT type="submit" value="○送信">\n);
print qq(</FORM>\n);

print qq(<UL>\n);
print qq(<LI>めんどくさい作業用．</LI>\n);
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
