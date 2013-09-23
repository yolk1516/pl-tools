#!/usr/bin/perl -w

package main;

# ラジオシステム
$VERSION = '-radiosystem.cgi- 0.01';

####-▼-設定-▼-####
$PASS = '***';
$CHARMARK = 'euc';
$SCRIPT = 'radiosystem.cgi';

$DB_DRIVER = 'mysql';
$DB_NAME = 'ices_db';
$DB_HOSTNAME = 'localhost';
$DB_USER = 'root';
$DB_PASSWORD = '***';

$MP3_DIR = '/usr/local/pub/g/mp3/';
$LOG_FILE = '/home/two/stream/work.log';
$ACTEXEC = '/home/two/stream/actExec.dat';
$NEXT_FILE = '/home/two/stream/next.dat';
$INFOMP3 = '/home/two/stream/information.dat';
$CLEAR_RECORD = '/home/two/stream/clear_record.dat';
$TMP_FILE = '/tmp/ices.log';
####-▲-設定-▲-####

use DBI;
use Jcode;
use HTMLball;
use MP3::Tag;

local $hth = HTMLball->new('Radio System');
my $j = Jcode->new();

$dsn = "DBI:$DB_DRIVER:database=$DB_NAME:host=$DB_HOSTNAME";
my $dbh = DBI->connect($dsn,$DB_USER,$DB_PASSWORD)|| $hth->err($DBI::errstr);
my %in;
local %cke;

Read_Parse(\%in,\%cke);
$hth->setTitle('Kurinet Radio System');
$hth->setCss('radiosystem.css');

if($in{'request'} eq 'admin'){
	if($in{'pass'} eq $PASS){
		if($in{'mode'} eq 'oneorder'){
			DB_one_order($dbh,\%in);
		}elsif($in{'mode'} eq 'playmode'){
			DB_change_playmode($dbh,\%in);
		}elsif($in{'mode'} eq 'nextplay'){
			DB_nextplay($dbh,\%in);
		}elsif($in{'mode'} eq 'diradd'){
			DB_diradd_playlist($dbh,\%in);
		}elsif($in{'mode'} eq 'pledit'){
			my $KANKYO = DB_kankyo_load($dbh);
			DB_make_playlist($dbh,\%in, $KANKYO);
		}elsif($in{'mode'} eq 'pladd'){
			my $KANKYO = DB_kankyo_load($dbh);
			DB_add_playlist($dbh,\%in, $KANKYO);
		}elsif($in{'mode'} eq 'delete'){
			my $KANKYO = DB_kankyo_load($dbh);
			DB_delete_playlist($dbh,\%in, $KANKYO);
		}elsif($in{'mode'} eq 'gendb'){
			DB_musiclist_gen($dbh, \%in);
		}elsif($in{'mode'} eq 'theme'){
			DB_set_theme($dbh, \%in);
		}elsif($in{'mode'} eq 'infomp3'){
			DB_set_infomp3($dbh, \%in);
		}elsif($in{'mode'} eq 'point'){
			DB_set_point($dbh, \%in);
		}elsif($in{'mode'} eq 'clear_record'){
			DB_clear_record($dbh, \%in);
		}elsif($in{'mode'} eq 'setcke'){
			$cke{'pass'} = $in{'pass'};
			if($in{'delete'} == 1){
				undef($cke{'pass'});
				$in{'success'} = "Cookieを削除しました．";
			}else{
				$in{'success'} = "Cookieをセットしました．";
			}
			setCookie(\%cke);
		}
	}else{
		$in{'failed'} = "パスワードが違います．";
	}
}elsif($in{'request'} eq 'request'){
	DB_set_request($dbh,\%in);
}elsif($in{'request'} eq 'setoption'){
	$in{'success'} = "";
	if($in{'undefreload'} == 1){
		$cke{'undefreload'} = 1;
		$in{'success'} .= "オートリロードを無効にしました．<BR>\n";
	}else{
		undef($cke{'undefreload'});
		$in{'success'} .= "オートリロードを有効にしました．<BR>\n";
	}
	setCookie(\%cke);
}

if($in{'mode'} eq 'oneorder'){
	DB_one_order_html($dbh,\%in);
}elsif($in{'mode'} eq 'pledit'){
	DB_edit_playlist($dbh,\%in);
}elsif($in{'mode'} eq 'playlist' || $in{'mode'} eq 'delete'){
	my $KANKYO = DB_kankyo_load($dbh);
	print_playlist($dbh,\%in,$KANKYO);
}elsif($in{'mode'} eq 'playmode' || $in{'mode'} eq 'nextplay' || $in{'mode'} eq 'gendb'|| $in{'mode'} eq 'theme'
	|| $in{'mode'} eq 'point' || $in{'mode'} eq 'clear_record'|| $in{'mode'} eq 'infomp3'){
	my $KANKYO = DB_kankyo_load($dbh);
	print_playmode($dbh,\%in,$KANKYO);
}elsif($in{'mode'} eq 'order'){
	my $KANKYO = DB_kankyo_load($dbh);
	print_order($dbh,\%in,$KANKYO);
}elsif($in{'mode'} eq 'pladd'){
	my $KANKYO = DB_kankyo_load($dbh);
	print_add($dbh,\%in,$KANKYO);
}elsif($in{'mode'} eq 'record'){
	print_record_all($dbh,\%in);
}elsif($in{'mode'} eq 'setcke'){
	cke_form(\%in);
}elsif($in{'mode'} eq 'setoption'){
	cke_option(\%in);
}else{
	my $KANKYO = DB_kankyo_load($dbh);
	
	print $hth->contentType;
	my $sec = now_playing($dbh,\%in,$KANKYO);
	my $encodedir = $in{'dir'};
	$encodedir =~ s/(\W)/'%'.unpack("H2", $1)/ego;
	$encodedir =~ tr/ /+/;
	if($cke{'undefreload'}){
		print $hth->header();
	}else{
		print $hth->header(0, $sec, $SCRIPT."?dir=$encodedir");
	}
	print $hth->getBodyln;
	print_menu();
	
	print qq(<H2>曲目リスト ディレクトリ表示</H2>\n);
	print qq(<DIV class="sidebar">\n);
	my $cd = ML_print_dir($in{'dir'});
	print qq(<H2 class="smallbox">最近かかった曲(<A HREF="$SCRIPT?mode=record">履歴</A>)</H2>\n);
	print_record($dbh,\%in,6,1);
	print qq(<H2>お知らせ</H2>\n);
	print qq(<P class="sbpl">ラジオテーマ: <B>$KANKYO->{'theme'}</B></P>\n) if($KANKYO->{'theme'});
	if(($KANKYO->{'playmode'} == 1 || $KANKYO->{'playmode'} == 3) && pl_check()){
		print qq(<P class="request">現在，リクエストを受け付けています，リクエストした曲はしばらくするとかかります．</P>\n);
	}else{
		print qq(<P class="request">現在，リクエストは受け付けていません．</P>\n);
	}

	print qq(</DIV>);

	print qq(<DIV class="mainbox">\n);
	DB_print_musiclist($dbh, "where filepath like '$cd%' and filepath not like '$cd%/%'",\%in, 3, $KANKYO->{'playmode'});
	print qq(</DIV>);

	print $hth->footer();
}
$dbh->disconnect();


####-▼-アクセス制限なし-▼-########-▼-アクセス制限なし-▼-########-▼-アクセス制限なし-▼-####
# ---------- ---------- ---------- ---------- ---------- ----------
#  	pl_check
#  		
sub pl_check{
	my $COMMAND = `ps -ax | awk '/streamdaemon/ && !/awk/ {print \$2}'`;
	return $COMMAND;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	print_menu
#  		
sub print_menu{
	my $mode = shift;
	
	print qq(<H1>Kurinet Radio!!</H1>\n);
	
	print qq(<DIV class="menu">\n);
	print qq(<A HREF="$SCRIPT">ホーム</A>\n);
	print qq(<A HREF="kurinet.m3u">聴く</A>\n);
	print qq(<A HREF="http://www.teu.ac.jp/ktin/~two/kr/">1鯖 Status</A>\n);
	print qq(<A HREF="http://www.kurinet.org:8000/">2鯖 Status</A>\n);
	print qq(<A HREF="http://www.kurinet.org:8000/admin/">管理用xsl</A>\n) if($cke{'pass'} eq $PASS);
	print qq(<A HREF="$SCRIPT?mode=record&rnum=51">履歴</A>\n);
	print qq(<A HREF="$SCRIPT?mode=playmode">プレイモード</A>\n) if($cke{'pass'} eq $PASS);
	print qq(<A HREF="$SCRIPT?mode=playlist">プレイリスト</A>\n) if($cke{'pass'} eq $PASS);
	print qq(<A HREF="$SCRIPT?mode=pledit">プレイリスト編集</A>\n) if($cke{'pass'} eq $PASS);
	print qq(<A HREF="$SCRIPT?mode=pladd">プレイリストに1曲追加</A>\n) if($cke{'pass'} eq $PASS);
	print qq(<A HREF="$SCRIPT?mode=order">すぐ1曲放送したい(1曲選択モード)</A>\n) if($cke{'pass'} eq $PASS);
	print qq(<A HREF="$SCRIPT?mode=setoption">オプション設定</A>\n);
	print qq(<A HREF="$SCRIPT?mode=setcke">管理ログイン</A>\n);
	print qq(</DIV>\n);
}
# ---------- ---------- ---------- ---------- ---------- ----------
#  	print_record_all
#  		
sub print_record_all{
	my $dbh = $_[0];
	my $in = $_[1];

	print $hth->contentType;
	my $sec = now_playing($dbh,\%in,$KANKYO);
	my $encodedir = $in{'dir'};
	$encodedir =~ s/(\W)/'%'.unpack("H2", $1)/ego;
	$encodedir =~ tr/ /+/;
	if($cke{'undefreload'}){
		print $hth->header();
	}else{
		print $hth->header(0, $sec, $SCRIPT."?mode=$in->{'mode'}&rnum=$in->{'rnum'}");
	}
	print $hth->getBodyln;
	print_menu();

	print qq(<H2>再生履歴</H2>\n);
	print qq(<DIV class="menu">\n);
	print qq(<A HREF="$SCRIPT?mode=record&rnum=51">50件</A>\n);
	print qq(<A HREF="$SCRIPT?mode=record&rnum=101">100件</A>\n);
	print qq(<A HREF="$SCRIPT?mode=record&rnum=201">200件</A>\n);
	print qq(<A HREF="$SCRIPT?mode=record">全て</A>\n);
	print qq(</DIV>\n);
	print_record($dbh,$in,$in->{'rnum'});
	print $hth->footer();
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	now_playing (return SEC)
#  		
sub now_playing{
	my $dbh = $_[0];
	my $in = $_[1];
	my $KANKYO = $_[2];

	my $string;
	if($KANKYO->{'playmode'} == 7){
		$string = "select no,filepath,UNIX_TIMESTAMP(stamp) from rireki order by no desc limit 1";
	}else{
		$string = "select no,filepath,UNIX_TIMESTAMP(stamp) from record left join musiclist on record.id=musiclist.id order by no desc limit 1"
	}

	my $sth = $dbh->prepare($string); 
	my $result=$sth->execute(); 
	unless($result){ 
		$in->{'failed'} = $DBI::errstr;
		return 0; 
	}
	
	my ($no,$filepath,$stamp); 
	$sth->bind_col(1,\$no); 
	$sth->bind_col(2,\$filepath); 
	$sth->bind_col(3,\$stamp);
	
	use MP3::Info;
	while($sth->fetch()){
		my $mp3 = MP3::Info->new($filepath);
		return (int(($stamp + $mp3->{'SECS'})-time())+15);
	}
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	print_record
#  		
sub print_record{
	my $dbh = shift;
	my $in = shift;
	my $limit = shift;
	my $small = shift;
	my $css = ($small)? 'sbpl' : 'pls';
	my $top = ($small)? 'sb1st' : 'plfirst';
	my $KANKYO = DB_kankyo_load($dbh);
	if($limit){
		$limit = " limit $limit";
	}
	
	my $string;
	if($KANKYO->{'playmode'} == 7){
		$string = "select no,filepath,stamp from rireki order by no desc$limit";
	}else{
		$string = "select no,filepath,stamp,artist,musicname,filename from record left join musiclist on record.id=musiclist.id order by no desc$limit"
	}
	
	my $sth = $dbh->prepare($string); 
	my $result=$sth->execute(); 
	unless($result){ 
		$in->{'failed'} = $DBI::errstr;
		return 0; 
	}
	my ($no,$artist,$musicname,$filename,$filepath,$stamp); 
	$sth->bind_col(1,\$no); 
	$sth->bind_col(2,\$filepath); 
	$sth->bind_col(3,\$stamp);
	if($KANKYO->{'playmode'} != 7){
		$sth->bind_col(4,\$artist);
		$sth->bind_col(5,\$musicname); 
		$sth->bind_col(6,\$filename);
	}

	print qq(<TABLE class="$css">\n);
	print qq(<TR class="$css">\n);
	print qq(<TH class="$css">Num</TH>);
	print qq(<TH class="$css">Artist</TH>);
	print qq(<TH class="$css">Music Name</TH>);
	print qq(<TH class="$css">Time Stamp</TH>\n) unless($small);
	print qq(</TR>\n);
	my $c = 0;
	while($sth->fetch()){
		if($KANKYO->{'playmode'} == 7){
			my $DATA = get_tag($filepath);
			$artist = $DATA->{'TPE1'};
			$musicname = $DATA->{'TIT2'};
			$filename = $filepath;
			$filename =~ s/(\/.+)*\/([^\/]+\.mp3)$/$+/;
			$j->set($artist);
			$artist = $j->euc;
			$j->set($musicname);
			$musicname = $j->euc;
			$j->set($filename);
			$filename = $j->euc;
		}
		$artist =~ s/-QQ-/'/g;  #'
		$musicname =~ s/-QQ-/'/g;  #'
		$filename =~ s/-QQ-/'/g;  #'
		$filepath =~ s/-QQ-/'/g;  #'
		if($c==0){
			print qq(<TR class="$top">\n);
			print qq(<TD class="$top" style="text-align: center;">Now!</TD>);
			if($musicname){
				print qq(<TD class="$top" colspan=2>$artist - $musicname</TD>);
#				print qq(<TD class="$top">$artist</TD>);
#				print qq(<TD class="$top">$musicname</TD>);
			}else{
				print qq(<TD class="$top" colspan=2>$filename</TD>);
			}
			print qq(<TD class="$top">$stamp</TD>\n) unless($small);
			print qq(</TR>\n);
		}else{
			print qq(<TR class="$css">\n);
			print qq(<TD class="$css" style="text-align: center;">$c</TD>);
			if($musicname){
				$artist = 'Unknown' unless($artist);
				print qq(<TD class="$css" colspan=2>$artist - $musicname</TD>);
#				print qq(<TD class="$css">$artist</TD>);
#				print qq(<TD class="$css">$musicname</TD>);
			}else{
				print qq(<TD class="$css" colspan=2 style="text-align: center;">$filename</TD>);
			}
			print qq(<TD class="$css" style="text-align: center;">$stamp</TD>\n) unless($small);
			print qq(</TR>\n);
		}
		$c++;
	}
	print qq(</TABLE>\n);
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	ML_print_dir
#  		
sub ML_print_dir{
	my $argdir = $_[0];

	if($argdir =~ /^\//){
		$argdir =~ s/^\///;
	}
	my $CURRENT_DIR = $MP3_DIR.$argdir;
	my $dir;
	
	opendir(DIR, $CURRENT_DIR);
	print qq(<H2 class="smallbox">ディレクトリ</H3>);
	print qq(<H3 class="mldir">CURRENT DIRECTORY:<BR> /$argdir</H3>\n);
	if($cke{'pass'} eq $PASS){
		print qq(<FORM ACTION="$SCRIPT" METHOD="POST">\n);
		print qq(<INPUT type="hidden" name="mode" value="diradd">);
		print qq(<INPUT type="hidden" name="request" value="admin">);
		print qq(<INPUT type="hidden" name="dir" value="$argdir">);
		print qq(<INPUT type="submit" value="追加実行">);
		print qq(PW<INPUT type="password" name="pass" value="$cke{'pass'}" size="8">\n);
		print qq(<INPUT type="checkbox" name="delete" value="1">PL削除\n);
	}
	print qq(<TABLE class="directory">\n);
#	print qq(<TR>);
#	if($cke{'pass'} eq $PASS){
#		print qq(<TH class="mldir">PL追加</TH>);
#	}else{
#		print qq(<TH class="mldir"></TH>);
#	}
#	print qq(<TH class="mldir">ディレクトリ名</TH>);
#	print qq(</TR>\n);
	while (defined($dir = readdir(DIR))) {

		if($dir =~ /^\.$/){
			my $encodedir = $argdir;
			$encodedir =~ s/(\W)/'%'.unpack("H2", $1)/ego;
			$encodedir =~ tr/ /+/;
			print qq(<TR>);
			print qq(<TD class="mldir">);
			print qq(<INPUT TYPE="checkbox" NAME="adddir" value="$argdir">) if($cke{'pass'} eq $PASS);
			print qq(<TD class="mldir"><A HREF="$SCRIPT?dir=$encodedir">$dir</A></TD>\n);
			print qq(</TR>);
		}elsif($dir =~ /^\.\.$/){
			if($CURRENT_DIR ne $MP3_DIR){
				my $tmpstr = '/'.substr($argdir,0,rindex($argdir,"/"));
				my $tmpdir = substr($tmpstr,0,rindex($tmpstr,"/"));
				$tmpdir =~ s/^\///;
				$tmpdir =~ s/(\W)/'%'.unpack("H2", $1)/ego;
				$tmpdir =~ tr/ /+/;
				print qq(<TR>);
				print qq(<TD class="mldir"></TD><TD class="mldir"><A HREF="$SCRIPT?dir=$tmpdir/">$dir</A></TD>\n);
				print qq(</TR>);
			}
		}elsif(-d $CURRENT_DIR.$dir){
			my $encodedir = $argdir.$dir;
			$encodedir =~ s/(\W)/'%'.unpack("H2", $1)/ego;
			$encodedir =~ tr/ /+/;
			print qq(<TR>);
			print qq(<TD class="mldir">);
			print qq(<INPUT TYPE="checkbox" NAME="adddir" value="$argdir$dir/">) if($cke{'pass'} eq $PASS);
			print qq(</TD>);
			print qq(<TD class="mldir"><A HREF="$SCRIPT?dir=$encodedir/">$dir</A></TD>\n);
			print qq(</TR>);
		}
	}
	print qq(</FORM>\n) if($cke{'pass'} eq $PASS);
	print qq(</TABLE>);
 	closedir(DIR);
 	$CURRENT_DIR =~ s/'/-QQ-/g; #'
	return $CURRENT_DIR;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_print_musiclist
#  		
sub DB_print_musiclist{
	my $dbh = $_[0];
	my $state = $_[1];
	my $in = $_[2];
	my $formmode = $_[3];
	my $playmode = $_[4];

	sysMsg($in);

	my $sth = $dbh->prepare("select id,artist,musicname,filename,filepath from musiclist $state"); 
	my $result=$sth->execute(); 
	unless($result){ 
		return $DBI::errstr; 
	}
	my ($id,$artist,$musicname,$filename,$filepath); 
	$sth->bind_col(1,\$id); 
	$sth->bind_col(2,\$artist); 
	$sth->bind_col(3,\$musicname);
	$sth->bind_col(4,\$filename); 
	$sth->bind_col(5,\$filepath); 

	print "<TABLE>\n";
	print "<TR>";
	print qq(<TH class="mltitle">id</TH>);
	print qq(<TH class="mltitle">artist</TH>);
	print qq(<TH class="mltitle">musicname</TH>);
	if($formmode == 1){	# 1曲選択モード
		print qq(<TH class="mltitle">Listen Now</TH>);
	}elsif($formmode == 2){	# 追加モード
		print qq(<TH class="mltitle">Add Playlist</TH>);
	}elsif($formmode == 3){	# リクエストモード
		print qq(<TH class="mltitle">Request</TH>);
	}
#	print qq(<TH class="mltitle">filename</TH>);
#	print qq(<TH class="mltitle">filepath</TH>);
	print qq(</TR>\n);
	while($sth->fetch()){
		$artist =~ s/-QQ-/'/g;  #'
		$musicname =~ s/-QQ-/'/g;  #'
		$filename =~ s/-QQ-/'/g;  #'
		$filepath =~ s/-QQ-/'/g;  #'
		print "<TR>";
		print qq(<TD class="musiclist">$id</TD>);
		if($musicname){
			print qq(<TD class="musiclist">$artist</TD>);
			print qq(<TD class="musiclist">$musicname</TD>);
		}else{
			print qq(<TD class="musiclist" colspan=2>$filename</TD>);
		}
		if($formmode == 1){		# 1曲選択モード
			print qq(<FORM ACTION="$SCRIPT" METHOD="POST">);
			print qq(<TD class="musiclist">);
			print qq(<INPUT type="hidden" name="mode" value="oneorder">);
			print qq(<INPUT type="hidden" name="id" value="$id">);
			print qq(<INPUT type="submit" value="Listen">);
			print qq(</TD>);
			print qq(</FORM>);
		}elsif($formmode == 2 && $cke{'pass'}){	# 追加モード
			print qq(<FORM ACTION="$SCRIPT" METHOD="POST">);
			print qq(<TD class="musiclist">);
			print qq(<INPUT type="hidden" name="request" value="admin">);
			print qq(<INPUT type="hidden" name="mode" value="pladd">);
			print qq(<INPUT type="hidden" name="pass" value="$cke{'pass'}">);
			print qq(<INPUT type="hidden" name="id" value="$id">);
			print qq(<INPUT type="submit" value="ADD">);
			print qq(</TD>);
			print qq(</FORM>);
		}elsif($formmode == 3 && ($playmode == 1 || $playmode == 3)){	# リクエストモード
			print qq(<FORM ACTION="$SCRIPT" METHOD="POST">);
			print qq(<TD class="musiclist">);
			print qq(<INPUT type="hidden" name="request" value="request">);
			print qq(<INPUT type="hidden" name="dir" value="$in->{'dir'}">);
			print qq(<INPUT type="hidden" name="id" value="$id">);
			print qq(<INPUT type="image" height="15" width="100" src="request.png">);
			print qq(</TD>);
			print qq(</FORM>);
		}
#		print qq(<TD class="musiclist">$filepath</TD>);
		print qq(</TR>\n);
	}
	print "</TABLE>\n";
	return "OK";
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_set_request
#  		
sub DB_set_request{
	my $dbh = $_[0];
	my $in = $_[1];
	
	my $DATA = DB_iddata_load($dbh,$in->{'id'});
	
	$DATA->{'filepath'} =~ s/-QQ-/'/g;  #'
	unless(-e $DATA->{'filepath'}){
		$in->{'failed'} = "ファイルが見つかりませんでした．";
		return 0;
	}

	open(ACT,">>$ACTEXEC") || return 0;
	flock(ACT, 2);
	print ACT "request $in->{'id'}\n";
	close(ACT);
	
	$DATA->{'filename'} =~ s/-QQ-/'/g;  #'
	$in->{'success'} = "$DATA->{'filename'}をリクエストしました．";
	return 1;
}
# ---------- ---------- ---------- ---------- ---------- ----------
#  	cke_option
#  		
sub cke_option{
	$in = shift;
	
	print $hth->contentType;
	print $hth->header;
	print $hth->getBodyln;
	print_menu();
	sysMsg($in);
	
	print qq(<H2>ウェブオプションをセットする(Cookie有効が条件)</H2>);
	
	print qq(<FORM ACTION="$SCRIPT" METHOD="POST">);
	print qq(<INPUT type="hidden" name="request" value="setoption">);
	print qq(<INPUT type="hidden" name="mode" value="setoption">);
	print qq(<INPUT type="checkbox" name="undefreload" value="1");
	print qq( checked) if($cke{'undefreload'});
	print qq(>オートリロード機能を停止する<BR>\n);
	print qq(<INPUT type="submit" value="オプションをセットする"><BR>\n);
	print qq(</FORM>);
	
	print $hth->footer();
}

####-▼-管理用-▼-########-▼-管理用-▼-########-▼-管理用-▼-########-▼-管理用-▼-####
# ---------- ---------- ---------- ---------- ---------- ----------
#  	cke_form
#  		
sub cke_form{
	$in = shift;
	
	print $hth->contentType;
	print $hth->header;
	print $hth->getBodyln;
	print_menu();
	sysMsg($in);
	
	print qq(<H2>Cookieにパスワードをセットする</H2>);
	
	print qq(<FORM ACTION="$SCRIPT" METHOD="POST">);
	print qq(<INPUT type="hidden" name="request" value="admin">);
	print qq(<INPUT type="hidden" name="mode" value="setcke">);
	print qq(<INPUT type="password" name="pass" value="$cke{'pass'}">\n);
	print qq(<INPUT type="checkbox" name="delete" value="1">Cookie削除<BR>\n);
	print qq(<INPUT type="submit" value="パスワードをセットする"><BR>\n);
	print qq(</FORM>);
	
	print $hth->footer();
}



####-▼-プレイモード変更-▼-####
# ---------- ---------- ---------- ---------- ---------- ----------
#  	print_playmode
#  		
sub print_playmode{
	my $dbh = $_[0];
	my $in = $_[1];
	my $KANKYO = $_[2];

	print $hth->contentType;
	print $hth->header;
	print $hth->getBodyln;
	print_menu();
	sysMsg($in);

	print qq(<H2>曲送り</H2>\n);
	print qq(<FORM ACTION="$SCRIPT" METHOD="POST">\n);
	print qq(<INPUT type="hidden" name="mode" value="nextplay">\n);
	print qq(<INPUT type="hidden" name="request" value="admin">\n);
	print qq(Admin Password<INPUT type="password" name="pass" value="$cke{'pass'}"><BR>\n);
	print qq(<INPUT type="submit" value="Next Play">\n);
	print qq(</FORM>\n);

	print qq(<H2>内部変数</H2>\n);
	print qq(<TABLE BORDER>\n);
	while (my($name, $value) = each(%$KANKYO)) {
		print qq(<TR><TH>$name</TH><TD>$value</TD></TR>\n);
	}
	print qq(</TABLE>\n);

	print qq(<H2>監視ログ</H2>\n);
	print qq(<H3>$LOG_FILE</H3>\n);
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
	print qq(<H3>$TMP_FILE</H3>\n);
	print qq(<PRE>\n);
	if(open(DATA, "|tail -n 10 $TMP_FILE")){
		while(<DATA>){
			print $_;
		}
		close(DATA);
	}else{
		print qq(open err.\n);
	}
	print qq(</PRE>\n);

	print qq(<H2>ラジオテーマ設定</H2>\n);
	print qq(<FORM ACTION="$SCRIPT" METHOD="POST">\n);
	print qq(<INPUT type="hidden" name="mode" value="theme">\n);
	print qq(<INPUT type="hidden" name="request" value="admin">\n);
	print qq(Admin Password<INPUT type="password" name="pass" value="$cke{'pass'}"><BR>\n);
	print qq(Radio Theme<INPUT type="text" name="theme" value="$KANKYO->{'theme'}"><BR>\n);
	print qq(<INPUT type="submit" value="ラジオテーマ変更">\n);
	print qq(</FORM>\n);

	print qq(<H2>再生ポイント選択(no)</H2>\n);
	print qq(<FORM ACTION="$SCRIPT" METHOD="POST">\n);
	print qq(<INPUT type="hidden" name="mode" value="point">\n);
	print qq(<INPUT type="hidden" name="request" value="admin">\n);
	print qq(Admin Password<INPUT type="password" name="pass" value="$cke{'pass'}"><BR>\n);
	print qq(再生ポイント<INPUT type="text" name="point" value="$KANKYO->{'playnum'}"><BR>\n);
	print qq(<INPUT type="submit" value="再生ポイント変更">\n);
	print qq(</FORM>\n);

	print qq(<H2>プレイモード変更</H2>\n);
	print qq(<FORM ACTION="$SCRIPT" METHOD="POST">\n);
	print qq(<INPUT type="hidden" name="mode" value="playmode">\n);
	print qq(<INPUT type="hidden" name="request" value="admin">\n);
	print qq(Admin Password<INPUT type="password" name="pass" value=""><BR>\n);
	my @chk;
	my $tmp = ($KANKYO->{'playmode'} != 6)? $KANKYO->{'playmode'} : $KANKYO->{'backmode'};
	$chk[$tmp] = ' checked';
	print qq(<INPUT type="radio" name="playmode" value="1"$chk[1]>ラジオモード(全ファイル) - プレイリスト再構築<BR>\n);
	print qq(<INPUT type="radio" name="playmode" value="2"$chk[2]>ランダムモード(全ファイル) - プレイリスト再構築<BR>\n);
	print qq(<INPUT type="radio" name="playmode" value="3"$chk[3]>ラジオモード(プレイリスト)<BR>\n);
	print qq(<INPUT type="radio" name="playmode" value="4"$chk[4]>ランダムモード(プレイリスト)<BR>\n);
	print qq(<INPUT type="radio" name="playmode" value="5"$chk[5]>プレイリストモード<BR>\n);
	print qq(<INPUT type="radio" name="playmode" value="7"$chk[7]>随時追加モード(特殊)\n);
	print qq(<BR>\n);
	print qq(<INPUT type="submit" value="Change!!">\n);
	print qq(</FORM>\n);

	print qq(<H2>infomp3セット(radio_information)</H2>\n);
	print qq(<FORM ACTION="$SCRIPT" METHOD="POST">\n);
	print qq(<INPUT type="hidden" name="mode" value="infomp3">\n);
	print qq(<INPUT type="hidden" name="request" value="admin">\n);
	print qq(Admin Password<INPUT type="password" name="pass" value=""><BR>\n);
	print qq(infomp3<INPUT type="text" name="id" value="$KANKYO->{'infomp3'}"><BR>\n);
	print qq(<INPUT type="submit" value="infomp3変更">\n);
	print qq(</FORM>\n);

	print qq(<H2>履歴削除</H2>\n);
	print qq(<FORM ACTION="$SCRIPT" METHOD="POST">\n);
	print qq(<INPUT type="hidden" name="mode" value="clear_record">\n);
	print qq(<INPUT type="hidden" name="request" value="admin">\n);
	print qq(Admin Password<INPUT type="password" name="pass" value=""><BR>\n);
	print qq(<INPUT type="submit" value="履歴削除">\n);
	print qq(</FORM>\n);

	print qq(<H2>曲目リストデータベース再構築</H2>\n);
	print qq(<FORM ACTION="$SCRIPT" METHOD="POST">\n);
	print qq(<INPUT type="hidden" name="mode" value="gendb">\n);
	print qq(<INPUT type="hidden" name="request" value="admin">\n);
	print qq(Admin Password<INPUT type="password" name="pass" value=""><BR>\n);
	print qq(<INPUT type="submit" value="曲目リスト再構築">\n);
	print qq(</FORM>\n);

	print $hth->footer();
}
# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_change_playmode
#  		
sub DB_change_playmode{
	my $dbh = $_[0];
	my $in = $_[1];
	my $KANKYO = DB_kankyo_load($dbh);
	$in->{'success'} = "";
	
	# モードごとに処理分け
	if($KANKYO->{'playmode'} == 6){
		$in->{'failed'} .= "1曲選択が入っているのでしばらく待ってください．";
	}
	
	if($in->{'playmode'} == 1 || $in->{'playmode'} == 2){
		DB_excute($dbh,"drop table playlist");
		my $result = DB_excute($dbh,"create table playlist (no INT(8) not null auto_increment,request tinyint(1),played tinyint(1), PRIMARY KEY (no)) select id from musiclist");
		DB_excute($dbh,"update kankyo SET num=$result where name='playmax'");
		DB_excute($dbh,"update kankyo SET num=$in->{'playmode'} where name='playmode'");
		$in->{'success'} = "$result個のファイルをプレイリストに登録しました．<BR>\n";
	}elsif(($in->{'playmode'} >= 3 && $in->{'playmode'} <= 5) || $in->{'playmode'} <= 7){
		DB_excute($dbh,"update kankyo SET num=$in->{'playmode'} where name='playmode'");
	}
	$in->{'success'} .= "$in->{'playmode'}のモードに変更しました．";
}

# ---------- ---------- ---------- ---------- ---------- ----------
#   DB_set_theme
#  		
sub DB_set_theme{
	my $dbh = $_[0];
	my $in = $_[1];
	my $KANKYO = DB_kankyo_load($dbh);
	
	DB_excute($dbh,"update kankyo SET value='$in->{'theme'}' where name='theme'");
	$in->{'success'} = "テーマを$in->{'theme'}に変更しました．";
}

# ---------- ---------- ---------- ---------- ---------- ----------
#   DB_set_point
#  		
sub DB_set_point{
	my $dbh = $_[0];
	my $in = $_[1];
	my $KANKYO = DB_kankyo_load($dbh);
	
	DB_excute($dbh,"update kankyo SET num='$in->{'point'}' where name='playnum'");
	$in->{'success'} = "再生ポイントを$in->{'point'}に変更しました．";
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_clear_record
#  		
sub DB_clear_record{
	my $dbh = $_[0];
	my $in = $_[1];

	system("cp -rf $CLEAR_RECORD $ACTEXEC");
	
	$in->{'success'} = '送信しました．';
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_nextplay
#  		
sub DB_nextplay{
	my $dbh = $_[0];
	my $in = $_[1];

	system("cp -rf $NEXT_FILE $ACTEXEC");
	
	$in->{'success'} = '送信しました．';
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_set_infomp3
#  		
sub DB_set_infomp3{
	my $dbh = $_[0];
	my $in = $_[1];
	
	open(ACT,">$INFOMP3") || return 0;
	flock(ACT, 2);
	print ACT "radio_information $in->{'id'}\n";
	close(ACT);
	
	DB_excute($dbh,"update kankyo SET num='$in->{'id'}' where name='infomp3'");
	
	$in->{'success'} = "$in->{'id'}をinfomp3にセットしました．";
	return 1;
}



####-▼-プレイリスト関係-▼-####
# ---------- ---------- ---------- ---------- ---------- ----------
#  	print_playlist
#  		
sub print_playlist{
	my $dbh = $_[0];
	my $in = $_[1];
	my $KANKYO = $_[2];

	print $hth->contentType;
	print $hth->header;
	print $hth->getBodyln;
	print_menu();
	sysMsg($in);

	print qq(<DIV class="linklist">[\n);
	my $limit = $in{'limit'} | 50;
	my $start = $in{'start'} | 0;
	my $calc = $start-($limit*10) - ($start%$limit);
	my $c = ($calc>0)? $calc : 0;
	my $i = ($c == $limit)? 2 : (int(($c)/$limit)+1>0)? int(($c)/$limit)+1 : 1;
	my $j = 0;
	while($j<10){
		if($c>$KANKYO->{'playmax'}){
			last;
		}
		if($c<=$start && $c+$limit>$start){
			print qq($i\n);
		}else{
			print qq(<A HREF="$SCRIPT?mode=playlist&start=$c&limit=$limit">$i</A>\n);
		}
		$c+=$limit; $i++;
		if($c>$start){
			$j++;
		}
	}
	print qq(]</DIV>);

	DB_print_playlist($dbh,"where playlist.no>$start limit $limit");
	
	print $hth->footer();
}
# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_print_playlist
#  		
sub DB_print_playlist{
	my $dbh = $_[0];
	my $state = $_[1];

	my $sth = $dbh->prepare("select no,artist,musicname,filename,filepath,played from playlist left join musiclist on playlist.id=musiclist.id $state"); 
	my $result=$sth->execute(); 
	unless($result){ 
		return $DBI::errstr; 
	}
	my ($no,$artist,$musicname,$filename,$filepath,$played); 
	$sth->bind_col(1,\$no); 
	$sth->bind_col(2,\$artist); 
	$sth->bind_col(3,\$musicname);
	$sth->bind_col(4,\$filename); 
	$sth->bind_col(5,\$filepath); 
	$sth->bind_col(6,\$played); 
	print qq(<H2 class="pl">PLAY LIST</H2>\n);
	print "<TABLE>\n";
	print "<TR>";
	print qq(<TH class="pltitle">no</TH>);
	print qq(<TH class="pltitle">artist</TH>);
	print qq(<TH class="pltitle">musicname</TH>);
	print qq(<TH class="pltitle">played</TH>);
	print qq(<TH class="pltitle">Delete</TH>);
#	print qq(<TH class="pltitle">filename</TH>);
#	print qq(<TH class="pltitle">filepath</TH>);
	print qq(</TR>\n);
	while($sth->fetch()){ 
		$artist =~ s/-QQ-/'/g;  #'
		$musicname =~ s/-QQ-/'/g;  #'
		$filename =~ s/-QQ-/'/g;  #'
		$filepath =~ s/-QQ-/'/g;  #'
		print "<TR>";
		print qq(<TD class="playlist">$no</TD>);
		if($musicname){
			print qq(<TD class="playlist">$artist</TD>);
			print qq(<TD class="playlist">$musicname</TD>);
		}else{
			print qq(<TD class="playlist" colspan=2>$filename</TD>);
		}
		if($played == 1){
			print qq(<TD class="playlist" style="color: #00C">未再生</TD>);
		}elsif($played == 2){
			print qq(<TD class="playlist" style="color: #C00">再生済</TD>);
		}
		print qq(<TD class="playlist">);
		if($cke{'pass'}){
			print qq(<FORM ACTION="$SCRIPT" METHOD="POST">);
			print qq(<INPUT type="hidden" name="mode" value="delete">);
			print qq(<INPUT type="hidden" name="request" value="admin">);
			print qq(<INPUT type="hidden" name="pass" value="$cke{'pass'}">);
			print qq(<INPUT type="hidden" name="no" value="$no">);
			print qq(<INPUT type="submit" value="DELETE">);
			print qq(</FORM>);
		}
		print qq(</TD>);
#		print qq(<TD class="playlist">$filepath</TD>);
		print qq(</TR>\n);
	}
	print "</TABLE>\n";
	return OK;
}
# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_delete_playlist
#  		
sub DB_delete_playlist{
	my $dbh = $_[0];
	my $in = $_[1];
	my $KANKYO = $_[2];
	
	$in->{'success'} = "";
	$in->{'failed'} = "";
	
	# 曲を削除する
	unless(DB_excute($dbh,"delete from playlist where no=$in{'no'}")){
		$in->{'failed'} .= "削除できませんでした．";
		return 0;
	}
	$in->{'success'} = "$in{'no'}にあった曲を削除しました．";
	
	# playlistのデータをまとめて得る
	my @pl_id;
	my @pl_request;
	my @pl_played;
	DB_get_array($dbh,\@pl_id,\@pl_request,\@pl_played); 
	
	# playlistテーブルを破棄
	DB_excute($dbh,"delete from playlist");
	DB_excute($dbh,"alter table playlist auto_increment=1");
	
	# playlistのデータを書き込む
	my $c = 0;
	my $state;
	while(my $id = shift(@pl_id)){
		my $request = shift(@pl_request);
		my $played  = shift(@pl_played);
		unless($request){
			$request = 'NULL';
		}
		unless($played){
			$played = 'NULL';
		}
		$state .= "($id,$request,$played)";
		$c++;
		if($c%50==0){
			$in->{'success'} .= $state;
			DB_excute($dbh,"insert into playlist (id,request,played) values $state");
			$state = '';
			next;
		}
		$state .= ",";
	}
	if($state){
		$state = substr($state,0,length($state)-1);
		$in->{'success'} .= $state;
		DB_excute($dbh,"insert into playlist (id,request,played) values $state");
	}
	DB_excute($dbh,"update kankyo SET num=$c where name='playmax'");
}
# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_get_array
#  		
sub DB_get_array{
	$dbh = shift;
	$pl_id = shift;
	$pl_request = shift;
	$pl_played = shift;
	
	my $sth = $dbh->prepare("select id,request,played from playlist"); 
	my $result=$sth->execute(); 
	unless($result){ 
		return $DBI::errstr; 
	}
	my ($id,$request,$played); 
	$sth->bind_col(1,\$id); 
	$sth->bind_col(2,\$request); 
	$sth->bind_col(3,\$played);

	while($sth->fetch()){
		push(@$pl_id,$id);
		push(@$pl_request,$request);
		push(@$pl_played,$played);
	}
	return;
}



####-▼-プレイリスト編集-▼-####
# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_edit_playlist
#  		
sub DB_edit_playlist{
	my $dbh = $_[0];
	my $in = $_[1];
	my $KANKYO = $_[2];

	print $hth->contentType;
	print $hth->header;
	print $hth->getBodyln;
	print_menu();
	sysMsg($in);
	
	print qq(<UL>\n);
	print qq(<LI>一行が一つの曲．\n);
	print qq(<LI>書式は「(曲ID,Request,Played)コメント〜」\n);
	print qq(<LI>コメント部は処理時に廃棄される．\n);
	print qq(</UL>\n);
	print qq(<FORM ACTION="$SCRIPT" METHOD="POST">);
	print qq(<INPUT type="hidden" name="request" value="admin">);
	print qq(<INPUT type="hidden" name="mode" value="pledit">);
	print qq(Admin Password<INPUT type="password" name="pass" value="$cke{'pass'}"><BR>\n);
	print qq(<textarea name="playlist" cols=80 rows=30>);

	my $sth = $dbh->prepare("select playlist.id,request,played,filename from playlist left join musiclist on playlist.id=musiclist.id"); 
	my $result=$sth->execute(); 
	unless($result){ 
		print $DBI::errstr;
		return 0; 
	}
	my ($id,$request,$played,$filename); 
	$sth->bind_col(1,\$id); 
	$sth->bind_col(2,\$request); 
	$sth->bind_col(3,\$played);
	$sth->bind_col(4,\$filename);

	while($sth->fetch()){
		unless($request){
			$request = 'NULL';
		}
		unless($played){
			$played = 'NULL';
		}
		$j->set($filename);
		$filename = $j->euc;
		print "($id,$request,$played)$filename\n";
	}
	print qq(</textarea>);
	print qq(<INPUT type="submit" value="更新">);
	print qq(</FORM>);
	
	print $hth->footer();
	return;
}
# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_make_playlist
#  		
sub DB_make_playlist{
	my $dbh = $_[0];
	my $in = $_[1];
	my $KANKYO = $_[2];
	
	my @PL = split(/\n/, $in->{'playlist'});
	
	# playlistテーブルを破棄
	DB_excute($dbh,"delete from playlist");
	DB_excute($dbh,"alter table playlist auto_increment=1");
	
	# playlistのデータを書き込む
	my $c = 0;
	my $state;
	while(my $tmpstr = shift(@PL)){
		$tmpstr =~ s/^(\([^\(\)]+\)).*$/$1/;
		$state .= $tmpstr;
		$c++;
		if($c%50==0){
			DB_excute($dbh,"insert into playlist (id,request,played) values $state");
			$state = '';
			next;
		}
		$state .= ",";
	}
	if($state){
		$state = substr($state,0,length($state)-1);
		DB_excute($dbh,"insert into playlist (id,request,played) values $state");
	}
	DB_excute($dbh,"update kankyo SET num=$c where name='playmax'");
	$in->{'success'} = "プレイリストを再構築しました．";
}



####-▼-1曲追加-▼-####
# ---------- ---------- ---------- ---------- ---------- ----------
#  	print_add
#  		
sub print_add{
	my $dbh = $_[0];
	my $in = $_[1];
	my $KANKYO = $_[2];

	print $hth->contentType;
	print $hth->header;
	print $hth->getBodyln;
	print_menu();

	print qq(<DIV class="linklist">[\n);
	my $limit = $in{'limit'} | 50;
	my $start = $in{'start'} | 0;
	my $calc = $start-($limit*10) - ($start%$limit);
	my $c = ($calc>0)? $calc : 0;
	my $i = ($c == $limit)? 2 : (int(($c)/$limit)+1>0)? int(($c)/$limit)+1 : 1;
	my $j = 0;
	while($j<10){
		if($c>$KANKYO->{'maxnum'}){
			last;
		}
		if($c<=$start && $c+$limit>$start){
			print qq($i\n);
		}else{
			print qq(<A HREF="$SCRIPT?mode=pladd&start=$c&limit=$limit">$i</A>\n);
		}
		$c+=$limit; $i++;
		if($c>$start){
			$j++;
		}
	}
	print qq(]</DIV>);

	DB_print_musiclist($dbh, "where id>$start limit $limit", $in , 2);
	
	print $hth->footer();
}
# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_add_playlist
#  		
sub DB_add_playlist{
	my $dbh = $_[0];
	my $in = $_[1];
	my $KANKYO = $_[2];
	
	# 曲が存在するか確認する
	my $DATA = DB_iddata_load($dbh,$in->{'id'});
	$DATA->{'filepath'} =~ s/-QQ-/'/g;  #'
	unless(-e $DATA->{'filepath'}){
		$in->{'failed'} = "$DATA->{'filename'}の曲ファイルは存在しませんでした．";
		return 0;
	}
	
	# プレイリストへ曲を書き込む
	if(!DB_excute($dbh,"insert into playlist (id) values ($in->{'id'})")){
		$in->{'failed'} = "プレイリストへの書き込みを失敗しました．";
		return 0;
	}
	$KANKYO->{'playmax'}++;
	# 環境のプレイリストの総数をインクリメント
	DB_excute($dbh,"update kankyo SET num=$KANKYO->{'playmax'} where name='playmax'");
	$DATA->{'filename'} =~ s/-QQ-/'/g;  #'
	$in->{'success'} = "$DATA->{'filename'}をプレイリストに追加しました．";
	
	return 1;
}



####-▼-1曲選択モード-▼-####
# ---------- ---------- ---------- ---------- ---------- ----------
#  	print_order
#  		
sub print_order{
	my $dbh = $_[0];
	my $in = $_[1];
	my $KANKYO = $_[2];

	print $hth->contentType;
	print $hth->header;
	print $hth->getBodyln;
	print_menu();

	print qq(<DIV class="linklist">[\n);
	my $limit = $in{'limit'} | 50;
	my $start = $in{'start'} | 0;
	my $calc = $start-($limit*10) - ($start%$limit);
	my $c = ($calc>0)? $calc : 0;
	my $i = ($c == $limit)? 2 : (int(($c)/$limit)+1>0)? int(($c)/$limit)+1 : 1;
	my $j = 0;
	while($j<10){
		if($c>$KANKYO->{'maxnum'}){
			last;
		}
		if($c<=$start && $c+$limit>$start){
			print qq($i\n);
		}else{
			print qq(<A HREF="$SCRIPT?mode=order&start=$c&limit=$limit">$i</A>\n);
		}
		$c+=$limit; $i++;
		if($c>$start){
			$j++;
		}
	}
	print qq(]</DIV>);

	DB_print_musiclist($dbh, "where id>$start limit $limit", $in , 1);
	
	print $hth->footer();
}
# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_one_order
#  		
sub DB_one_order{
	my $dbh = $_[0];
	my $in = $_[1];
	
	my $DATA = DB_iddata_load($dbh,$in->{'id'});
	my $KANKYO = DB_kankyo_load($dbh);
	
	if($KANKYO->{'backmode'}){
		$in->{'failed'} = "既に1曲選択されています，演奏されてから登録し直してください．";
		return 0;
	}
	if($KANKYO->{'mname'}){
		$in->{'failed'} = "現在，選択モードの曲が再生されています．終わってから登録しなおしてください．";
		return 0;
	}
	
	DB_excute($dbh,"update kankyo SET num='$DATA->{'id'}' where name='order'");
	DB_excute($dbh,"update kankyo SET num=$KANKYO->{'playmode'} where name='backmode'");
	DB_excute($dbh,"update kankyo SET num=6 where name='playmode'");
	if($DATA->{'musicname'}){
		DB_excute($dbh,"update kankyo SET value='$DATA->{'musicname'}' where name='mname'");
	}else{
		DB_excute($dbh,"update kankyo SET value='$DATA->{'filename'}' where name='mname'");
	}
	
	if($in->{'now'}==1){
		my $ACTEXEC = '/home/two/stream/actExec.dat';
		my $NEXT = '/home/two/stream/next.dat';
	
		system("cp -rf $NEXT $ACTEXEC");
	}
	
	$in->{'success'} = "送信しました．";
	return 1;
}
# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_one_order_html
#  		
sub DB_one_order_html{
	my $dbh = $_[0];
	my $in = $_[1];
	
	my $DATA = DB_iddata_load($dbh,$in->{'id'});
	
	print $hth->contentType;
	print $hth->header;
	print $hth->getBodyln;
	
	print_menu();
	
	print qq(<H2>1曲選択モード</H2>\n);
	
	sysMsg($in);
	
	print qq(<UL>\n);
	print qq(<LI>曲名：$DATA->{'musicname'}\n);
	print qq(<LI>アーティスト：$DATA->{'artist'}\n);
	print qq(<LI>DBID：$DATA->{'id'}\n);
	print qq(<LI>ファイル名：$DATA->{'filename'}\n);
	print qq(<LI>ファイルパス：$DATA->{'filepath'}\n);
	print qq(</UL>\n);

	print qq(<FORM ACTION="$SCRIPT" METHOD="POST">\n);
	print qq(<INPUT type="hidden" name="mode" value="oneorder">\n);
	print qq(<INPUT type="hidden" name="request" value="admin">\n);
	print qq(<INPUT type="hidden" name="id" value="$DATA->{'id'}">\n);
	print qq(Admin Password<INPUT type="password" name="pass" value="$cke{'pass'}"><BR>\n);
	print qq(<INPUT type="radio" name="now" value="1">今すぐ \n);
	print qq(<INPUT type="radio" name="now" value="0" checked>曲終了後\n);
	print qq(<BR>\n);
	print qq(<INPUT type="submit" value="Listen!">\n);
	print qq(</FORM>\n);

	print $hth->footer();
}



####-▼-DB操作-▼-########-▼-DB操作-▼-########-▼-DB操作-▼-########-▼-DB操作-▼-####
# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_diradd_playlist
#  		
sub DB_diradd_playlist{
	my $dbh = $_[0];
	my $in = $_[1];
	my $KANKYO = DB_kankyo_load($dbh);
	
	if($in->{'delete'} == 1){
		# playlistテーブルを破棄
		DB_excute($dbh,"delete from playlist");
		DB_excute($dbh,"alter table playlist auto_increment=1");
		$KANKYO->{'playmax'} = 0;
	}
	
	my @query = split(/,/,$in->{'adddir'});
	my $c = $KANKYO->{'playmax'};
	for(@query){
		my $CD = $MP3_DIR.$_;
		$CD =~ s/'/-QQ-/g; #'
		my $sth = $dbh->prepare("select id from musiclist where filepath like '$CD%'");
		my $result=$sth->execute(); 
		unless($result){ 
			$in->{'failed'} = $DBI::errstr;
			return 0; 
		}
		my ($id); 
		$sth->bind_col(1,\$id); 
		while($sth->fetch()){ 
			DB_excute($dbh,"insert into playlist (id) values ($id)");
			$c++;
		}
	}
	DB_excute($dbh,"update kankyo SET num=$c where name='playmax'");
	$in->{'success'} = "$c個のプレイリストになりました．";

	return 1;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_iddata_load
#  		
sub DB_iddata_load{
	my $dbh = $_[0];
	my $id = $_[1];
	my $DATA = {};

	my $sth = $dbh->prepare("select id,artist,musicname,filename,filepath from musiclist where id=$id limit 1"); 
	my $result=$sth->execute(); 
	unless($result){ 
		return $DBI::errstr; 
	}
	my ($no,$artist,$musicname,$filename,$filepath); 
	$sth->bind_col(1,\$no); 
	$sth->bind_col(2,\$artist); 
	$sth->bind_col(3,\$musicname);
	$sth->bind_col(4,\$filename);
	$sth->bind_col(5,\$filepath); 

	while($sth->fetch()){
		$DATA->{'id'} = $no;
		$DATA->{'artist'} = $artist;
		$DATA->{'musicname'} = $musicname;
		$DATA->{'filename'} = $filename;
		$DATA->{'filepath'} = $filepath;
	}
	return $DATA;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_musiclist_gen
#  		
sub DB_musiclist_gen{
	my $dbh = $_[0];
	my $in = $_[1];
	my $j = Jcode->new();
	
	# データベースのmusiclistを削除する
	my $statement= "delete from musiclist";
	my $result=$dbh->do($statement);
	unless($result){ 
		$in->{'failed'} = $DBI::errstr;
		return 0;
	}
	
	# mp3のリストを作る(タグも抽出)
	my $LIST = `find /usr/local/pub/g/mp3/ -name *.mp3 -print`;
	my @filelist = split(/\n/,$LIST);
	my $c = 0;
	foreach(@filelist){
		my $tmp = $_;
		my $tag = {};
		$tag = get_tag($tmp);
		
		$tmp =~ s/'/-QQ-/g;
		$tag->{'TPE1'} =~ s/'/-QQ-/g;
		$tag->{'TIT2'} =~ s/'/-QQ-/g;
		# '
		$j->set($tmp);
		$tmp = $j->euc;
		$j->set($tag->{'TPE1'});
		$tag->{'TPE1'} = $j->euc;
		$j->set($tag->{'TIT2'});
		$tag->{'TIT2'} = $j->euc;

		$c++;
		my $fname = $tmp;
		$fname =~ s/(\/.+)*\/([^\/]+\.mp3)$/$+/;
		my $statement=sprintf("insert into musiclist values (NULL,'%s','%s','%s','%s')",$tag->{'TPE1'},$tag->{'TIT2'},$fname,$tmp);
		my $result=$dbh->do($statement);
		unless($result){
			$in->{'failed'} = $DBI::errstr;
			return 0;
		}
	}
	DB_excute($dbh,"update kankyo SET num=$c where name='maxnum'");
	$in->{'success'} = 'データベースを再構築しました．';
	return 1;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_kankyo_load
#  		
sub DB_kankyo_load{
	my $dbh = $_[0];
	my $kankyo = {};

	my $sth = $dbh->prepare("select name,num,value,stamp from kankyo"); 
	my $result=$sth->execute(); 
	unless($result){ 
		return $DBI::errstr; 
	}
	my ($name,$num,$value,$stamp); 
	$sth->bind_col(1,\$name); 
	$sth->bind_col(2,\$num); 
	$sth->bind_col(3,\$value);
	$sth->bind_col(4,\$stamp); 

	while($sth->fetch()){ 
		if($value ne ''){
			$kankyo->{$name} = $value;
		}else{
			$kankyo->{$name} = $num;
		}
	}
	return $kankyo;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_excute
#  		
sub DB_excute{
	my $dbh = $_[0];
	my $statement = $_[1];
	
	my $result=$dbh->do($statement);
	unless($result){
		print $DBI::errstr;
		return 0; 
	}
	return $result;
}



####-▼-ライブラリ-▼-####
# ---------- ---------- ---------- ---------- ---------- ----------
#  	get_tag
#  		
sub get_tag{
	my $file = $_[0];
	my $mp3 = MP3::Tag->new($file);

	return undef unless defined $mp3;

	$mp3->get_tags();

	my $tag = {};
	if (exists $mp3->{ID3v2}){
		my $id3v2 = $mp3->{ID3v2};
		my $frames = $id3v2->supported_frames();
		while (my ($fname, $longname) = each %$frames){
			# only grab the frames we know
#			next unless exists $supported_frames{$fname};
#			print "exists ID3v2\n";
			$tag->{$fname} = $id3v2->get_frame($fname);
			delete $tag->{$fname} unless defined $tag->{$fname};
			$tag->{$fname} = $tag->{$fname}->{Text} if $fname eq 'COMM';
			$tag->{$fname} = $tag->{$fname}->{URL} if $fname eq 'WXXX';
			$tag->{$fname} = '' unless defined $tag->{$fname};
			
#			print "$fname=$tag->{$fname}\n";
		}
	}
	elsif (exists $mp3->{ID3v1}){
		warn "No ID3 v2 TAG info in $file, using the v1 tag";
		my $id3v1 = $mp3->{ID3v1};
		$tag->{COMM} = $id3v1->comment();
		$tag->{TIT2} = $id3v1->song();
		$tag->{TPE1} = $id3v1->artist();
		$tag->{TALB} = $id3v1->album();
		$tag->{TYER} = $id3v1->year();
		$tag->{TRCK} = $id3v1->track();
		$tag->{TIT1} = $id3v1->genre();
	}
	else{
		warn "No ID3 TAG info in $file, creating it";
		$tag = {
			TIT2 => '',
			TPE1 => '',
			TALB => '',
			TYER => 9999,
			COMM => '',
		};
	}
	return $tag;
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


#	if($name == 'dir'){
#		$form->{$name}=$value;
#	}else{
	$value =~ tr/+/ /;
	$value =~ s/%([0-9a-fA-F][0-9a-fA-F])/pack("C", hex($1))/eg;

	my $j = Jcode->new();
	$j->set($value);
	$value = $j->euc;
	
	if($tagcheck){
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
#	}
    }

    if ( $ENV{HTTP_COOKIE} && $cookie ){
	foreach ( split(/\s*;\s*/,$ENV{HTTP_COOKIE}) ){
	    foreach ( split(/[\+,]/,$_) ){
		my ($name,$value) = split(/=/,$_);
		$value =~ s/%([0-9a-fA-F][0-9a-fA-F])/pack("C", hex($1))/eg;
		Jcode::convert(\$value, $CHARMARK);
		$cookie->{$name} = $value;
	    }
	}
    }
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	SET COOKIE Routine
#  		&setCookie(%COOKIE);
sub setCookie{
	my $po = $_[0];
	my $cookie_data;
	$cookie_data = "Set-Cookie: ";
	while (my($name, $value) = each(%$po)) {
		$cookie_data = join("+", $cookie_data, $name ."=". $value);
	}
	$cookie_data .= "; expires=Mon, 30 Dec 2020 23:59:59 GMT\n";
	print $cookie_data;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	sysMsg
#  		
sub sysMsg{
	$in = shift;
	if($in->{'failed'}){
		print qq(<DIV class="sysmsgErr">&lt;SYSTEM ERROR MESSAGE&gt;<BR> $in->{'failed'}</DIV>\n);
	}
	if($in->{'success'}){
		print qq(<DIV class="sysmsgSuc">&lt;SYSTEM MESSAGE&gt;<BR> $in->{'success'}</DIV>\n);
	}
}

