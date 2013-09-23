#!/usr/bin/perl -w

# icesdaemon
$ver = "1.0.2-050112";

# 常駐プログラム全般の配置場所
$ROOT_DIR = "/home/two/stream/";

# リクエストしてからセットするまでの時間
$REQUEST_TIME = 60*10;

# 常駐→制御の処理のやりとりを扱うファイル
$ACT_ROOT_FILE = $ROOT_DIR."actRoot.dat";
# 常駐←制御の処理のやりとりを扱うファイル
$ACT_EXEC_FILE = $ROOT_DIR."actExec.dat";
# 作業記録を書き出すファイル
$LOG_FILE = $ROOT_DIR."work.log";

log_write("[[icesdaemon $ver started]]");

my @REQUEST;
my @REQUEST_TIME;

while(1){

	my @command = &read_command;

	foreach(@command){
		my $tmp = $_;
		$tmp =~ s/\r//;
		$tmp =~ s/\n//;
		my @c = split(/ /,$tmp);
		
		if($c[0] eq 'next'){
			my $proc = `ps ux | awk '/ices/ && !/awk/ {print \$2}'`;
			system("kill -USR1 $proc");
		}
		
		elsif($c[0] eq 'gen_musiclist'){
			DB_musiclist_gen_daemon();
		}
		
		elsif($c[0] eq 'radio_information'){
			DB_information($c[1],\@REQUEST,\@REQUEST_TIME);
		}
		
		elsif($c[0] eq 'clear_record'){
			DB_clear_record();
		}
		
		elsif($c[0] eq 'request'){
			push(@REQUEST, $c[1]);
			push(@REQUEST_TIME, time+$REQUEST_TIME);
		}

		elsif($c[0] eq 'set_rtime'){
			$REQUEST_TIME = $c[1];
			log_write("set request_time $c[1].");
		}
		
		elsif($c[0] eq 'log_request'){
			for(@REQUEST){
				log_write("request $_.");
			}
		}
		
		elsif($c[0] eq 'shutdown'){
			log_write("[[icesdaemon $ver shutdown]]");
			exit;
		}else{
			log_write("unknown command '$c[0]'");
		}
		sleep 5;
	}
	if($REQUEST_TIME[0] && $REQUEST_TIME[0] < time){
		DB_request(\@REQUEST,\@REQUEST_TIME);
	}
	
	sleep 5;
}
# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_request
#  		
sub DB_request{
	my $DB_DRIVER = 'mysql';
	my $DB_NAME = 'ices_db';
	my $DB_HOSTNAME = 'localhost';
	my $DB_USER = 'root';
	my $DB_PASSWORD = 'kurimura';
	my $R = $_[0];
	my $RT = $_[1];

	use DBI;
	use Jcode;
	use MP3::Tag;
	
	$dsn = "DBI:$DB_DRIVER:database=$DB_NAME:host=$DB_HOSTNAME";
	my $dbh = DBI->connect($dsn,$DB_USER,$DB_PASSWORD)|| return 0;

	my $KANKYO = DB_kankyo_load($dbh);
	
	if($KANKYO->{'playmode'} != 1 && $KANKYO->{'playmode'} != 3 && $KANKYO->{'playmode'} != 6){
		log_write("request clear.");
		undef(@$RT);
		undef(@$R);
		return 0;
	}
	
	if($KANKYO->{'order'} || $KANKYO->{'mname'}){
		$RT->[0] = time+60;
		return;
	}

	my $id = shift(@$R);
	shift(@$RT);
	
	my $j = Jcode->new();
	
	my $DATA = DB_iddata_load($dbh,$id);
	
	DB_excute($dbh,"update kankyo SET num='$id' where name='order'");
	DB_excute($dbh,"update kankyo SET num=$KANKYO->{'playmode'} where name='backmode'");
	DB_excute($dbh,"update kankyo SET num=6 where name='playmode'");
	if($DATA->{'musicname'}){
		DB_excute($dbh,"update kankyo SET value='$DATA->{'musicname'}' where name='mname'");
	}else{
		DB_excute($dbh,"update kankyo SET value='$DATA->{'filename'}' where name='mname'");
	}
	
	log_write("request $id set.");
	return 1;
}


# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_clear_record
#  		
sub DB_clear_record{
	my $DB_DRIVER = 'mysql';
	my $DB_NAME = 'ices_db';
	my $DB_HOSTNAME = 'localhost';
	my $DB_USER = 'root';
	my $DB_PASSWORD = 'kurimura';
	my $id = $_[0];
	
	use DBI;

	$dsn = "DBI:$DB_DRIVER:database=$DB_NAME:host=$DB_HOSTNAME";
	my $dbh = DBI->connect($dsn,$DB_USER,$DB_PASSWORD)|| return 0;
	
	DB_excute($dbh,"delete from record");
	DB_excute($dbh,"alter table record auto_increment=1");

	DB_excute($dbh,"delete from rireki");
	DB_excute($dbh,"alter table rireki auto_increment=1");

	log_write("recird cleared.");
	return 1;
}


# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_information
#  		
sub DB_information{
	my $DB_DRIVER = 'mysql';
	my $DB_NAME = 'ices_db';
	my $DB_HOSTNAME = 'localhost';
	my $DB_USER = 'root';
	my $DB_PASSWORD = 'kurimura';
	my $id = $_[0];
	my $r = $_[1];
	my $rt = $_[2];
	
	use DBI;
	use Jcode;
	use MP3::Tag;

	$dsn = "DBI:$DB_DRIVER:database=$DB_NAME:host=$DB_HOSTNAME";
	my $dbh = DBI->connect($dsn,$DB_USER,$DB_PASSWORD)|| return 0;
	my $j = Jcode->new();
	
	my $DATA = DB_iddata_load($dbh,$id);
	my $KANKYO = DB_kankyo_load($dbh);
	
	if($KANKYO->{'playmode'} != 1 && $KANKYO->{'playmode'} != 3){
		return 0;
	}
	
	if($KANKYO->{'order'}){
		push(@$r, $KANKYO->{'order'});
		push(@$rt, time);
	}
	
	DB_excute($dbh,"update kankyo SET num='$id' where name='order'");
	DB_excute($dbh,"update kankyo SET num=$KANKYO->{'playmode'} where name='backmode'");
	DB_excute($dbh,"update kankyo SET num=6 where name='playmode'");
	if($DATA->{'musicname'}){
		DB_excute($dbh,"update kankyo SET value='$DATA->{'musicname'}' where name='mname'");
	}else{
		DB_excute($dbh,"update kankyo SET value='$DATA->{'filename'}' where name='mname'");
	}

	return 1;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	DB_musiclist_gen_daemon
#  		
sub DB_musiclist_gen_daemon{
	my $DB_DRIVER = 'mysql';
	my $DB_NAME = 'ices_db';
	my $DB_HOSTNAME = 'localhost';
	my $DB_USER = 'root';
	my $DB_PASSWORD = 'kurimura';
	
	use DBI;
	use Jcode;
	use MP3::Tag;
	
	$dsn = "DBI:$DB_DRIVER:database=$DB_NAME:host=$DB_HOSTNAME";
	my $dbh = DBI->connect($dsn,$DB_USER,$DB_PASSWORD)|| return 0;
	my $j = Jcode->new();
	
	my $KANKYO = DB_kankyo_load($dbh);
	if($KANKYO->{'playmode'} != 1 && $KANKYO->{'playmode'} != 2){
		log_write("skip db generate.");
		return 0;
	}
	
	# データベースのmusiclistを削除する
	my $statement= "delete from musiclist";
	my $result=$dbh->do($statement);
	unless($result){ 
		log_write($DBI::errstr);
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
			log_write($DBI::errstr);
			return 0; 
		}
	}
	DB_excute($dbh,"update kankyo SET num=$c where name='maxnum'");
	
	# Playlist generate
	DB_excute($dbh,"drop table playlist");
	$result = DB_excute($dbh,"create table playlist (no INT(8) not null auto_increment,request tinyint(1),played tinyint(1), PRIMARY KEY (no)) select id from musiclist order by rand()");
	DB_excute($dbh,"update kankyo SET num=$result where name='playmax'");
	log_write("musiclist generated.");
	return 1;
}

# コマンドチェック
sub read_command{
	my @tmp;
	open(DATA,"+< $ACT_EXEC_FILE") || die "$ACT_EXEC_FILE open err.";
	flock(DATA, 2);
	while(<DATA>){
		push(@tmp,$_);
	}
	truncate(DATA, 0);
	seek(DATA, 0, 0);
	close(DATA);
	return @tmp;
}

# ログ書き出し
sub log_write{
	my $line = $_[0];
	my @tmp_time = &getDate(time);
	my $now_time = "$tmp_time[5]/$tmp_time[4]/$tmp_time[3]($tmp_time[6]) $tmp_time[2]:$tmp_time[1]:$tmp_time[0] - ";
	
	open(LOG,">>$LOG_FILE") || return 0;
	flock(LOG, 2);
	print LOG $now_time.$line."\n";
	close(LOG);
	return 0;
}

# ---------- ---------- ---------- ---------- ---------- ----------
#  	Get Date Routine
#  		&getDate(TIME);
#		@dateFormat = (SEC, MIN, HOUR, DATE, MONTH, YEAR, DAY);
sub getDate {
	my @dateFormat = localtime($_[0]);
	my @week = ("Sun", "Mon", "Tue", "Wed", "Thu", "fri", "Sat");
	$dateFormat[6] = $week[$dateFormat[6]];
	$dateFormat[5] = sprintf("%02d", $dateFormat[5] + 1900);
	$dateFormat[4] = sprintf("%02d", $dateFormat[4] + 1);
	$dateFormat[3] = sprintf("%02d", $dateFormat[3]);
	$dateFormat[2] = sprintf("%02d", $dateFormat[2]);
	$dateFormat[1] = sprintf("%02d", $dateFormat[1]);
	$dateFormat[0] = sprintf("%02d", $dateFormat[0]);
	return @dateFormat;
}

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


