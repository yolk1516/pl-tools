#!/usr/bin/perl -w

# Dream Cup サーバ制御プログラム(常駐用)
$ver = "1.0.5-041202";

require '/home/two/gameServer/procserver.ini.pl';

@PID = ();

log_write("[[procserver $ver started]]");

while(1){

	my @command = &read_command;

	foreach(@command){
		my $tmp = $_;
		$tmp =~ s/\r//;
		$tmp =~ s/\n//;
		my @c = split(/ /,$tmp);
		
		# 起動
		if($c[0] eq 'start'){
			if($c[1] ne '' && $c[1] >= 0 && $c[1] < @DCS_INI_DIR){
				&dcs_start($c[1]);
			}else{
				log_write("dcs_start arg1 err.");
			}
		}
		
		# 終了
		elsif($c[0] eq 'kill'){
			if($c[1] ne '' && $c[1] >= 0 && $c[1] < @DCS_INI_DIR){
				&dcs_kill($c[1]);
			}else{
				log_write("dcs_kill arg1 err.");
			}
		}
		
		# 再起動
		elsif($c[0] eq 'reboot'){
			if($c[1] ne '' && $c[1] >= 0 && $c[1] < @DCS_INI_DIR){
				&dcs_reboot($c[1]);
			}else{
				log_write("dcs_reboot arg1 err.");
			}
		}
		
		# プロセスチェック
		elsif($c[0] eq 'pid_check'){
			&pid_check();
		}
		
		# Versionログ書き込み
		elsif($c[0] eq 'version'){
			log_write("--procserver version $ver.");
		}
		
		# pidログ書き込み
		elsif($c[0] eq 'pid_logger'){
			for(my $i = 0; $i < @DCS_INI_DIR; $i++){
				if($PID[$i]){
					log_write("pid_logger SERVER[$i] $PID[$i].");
				}
			}
		}
		
		# 手動修正コマンド(つかい方を誤るとメチャクチャになるよ)
		elsif($c[0] eq 'fix'){
			if($c[1] eq 'memory'){
				if($c[2] >= 0 && $c[2] < @DCS_INI_DIR){
					if($c[3] =~ /(\d)/){
						log_write("fix MEMORY[$c[2] $PID[$c[2]] -> $1");
						$PID[$c[2]] = $1;
					}elsif($c[3] =~ /delete/){
						log_write("fix MEMORY[$c[2] $PID[$c[2]] -> delete");
						undef($PID[$c[2]]);
					}else{
						log_write("fix arg3 err.");
					}
				}else{
					log_write("fix arg2 err.");
				}
			}elsif($c[1] eq 'file'){
				if($c[2] >= 0 && $c[2] < @DCS_INI_DIR){
					if($c[3] =~ /(\d)/){
						log_write("fix FILE[$c[2] $PID[$c[2]] -> $1");
						root_write($c[2], $1);
					}elsif($c[3] =~ /delete/){
					log_write("fix FILE[$c[2] $PID[$c[2]] -> delete");
						root_delete($c[2], $1);
					}else{
						log_write("fix arg3 err.");
					}
				}else{
					log_write("fix arg2 err.");
				}
			}else{
				log_write("fix arg1 err.");
			}
		}
		
		# 変数とファイルの同期を取るコマンドを実装するべきか否か．→手動修正でなんとかしてくれ．
		
		# このプログラムの終了
		elsif($c[0] eq 'shutdown'){
			for(my $i = 0; $i < @DCS_INI_DIR; $i++){
				&dcs_kill($i);
				root_delete($i);
			}
			log_write("[[procserver $ver shutdown]]");
			exit;
		}else{
			log_write("unknown command '$c[0]'");
		}
		
		sleep 5;
	}

	sleep 30;
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

# プロセスチェック
# ゾンビプロセスのチェックもできるようにしたい．<defunct>
sub pid_check{
	my $pid = `ps ux | awk '/$DC_SERVER_NAME/ && !/awk/ && !/defunct/ {print \$2}'`;
	my @pidlist = split(/\n/,$pid);
	
	log_write("pid_check start");
	for(my $i = 0; $i < @DCS_INI_DIR; $i++){
		my $flag = 0;
		if(!$PID[$i]){
			next;
		}
		foreach(@pidlist){
			if($PID[$i] == $_){
				$flag = 1;
				last;
			}
		}
		if(!$flag){
			log_write("pid_check SERVER[$i] $PID[$i] -> process not found.");
			&dcs_kill($i);
			sleep 5;
			&dcs_start($i);
		}
	}
	log_write("pid_check done.");
	return 1;
}

# プロセスチェック簡易版
sub pid_test{
	my $str = $_[0];
	my $comp = $_[1];
	my $pid = `ps ux | awk '/$str/ && !/awk/ {print \$2}'`;
	my @pidlist = split(/\n/,$pid);
	
	for(my $i = 0; $i < @pidlist; $i++){
		if($pidlist[$i] == $comp){
			return 1;
		}
	}
	return 0;
}

# 鯖再起動
sub dcs_reboot{
	my $server_no = $_[0];
	&dcs_kill($server_no) || return log_write("dcs_reboot SERVER[$server_no] kill failed.");
	sleep 5;
	&dcs_start($server_no) || return log_write("dcs_reboot SERVER[$server_no] start failed.");
	return 1;
}

# 鯖起動
sub dcs_start{
	my $server_no = $_[0];
	if($PID[$server_no]){
		return log_write("dcs_start SERVER[$server_no] not 0.");
	}

	unless(-e "$DCS_INI_DIR[$server_no]$DCS_INI"){
		return log_write("dcs_start SERVER[$server_no] no gameServer.ini err.");
	}
	chdir $DCS_INI_DIR[$server_no] || return log_write("dcs_start SERVER[$server_no] chdir err.");
	$PID[$server_no] = open($DCS_FH[$server_no],"|$DC_SERVER") || return log_write("dcs_start SERVER[$server_no] open err.");
	
	sleep 5;
	
	if(!&pid_test($DC_SERVER_NAME,$PID[$server_no])){
		return log_write("dcs_start SERVER[$server_no] exit 1 err.");
	}
	
	log_write("dcs_start SERVER[$server_no] started($PID[$server_no]).");
	root_write($server_no,$PID[$server_no]);
	return $PID[$server_no];
}

# 鯖終了
sub dcs_kill{
	my $server_no = $_[0];
	if(!$PID[$server_no]){
		return log_write("dcs_kill SERVER[$server_no] not started.");
	}
	if(!&pid_test($DC_SERVER_NAME,$PID[$server_no])){
		root_delete($server_no,$PID[$server_no]);
		undef($PID[$server_no]);
		return log_write("dcs_kill SERVER[$server_no] already ended.");
	}

	open(KILL,"|kill $PID[$server_no]") || return log_write("dcs_kill SERVER[$server_no] open err.");
	close(KILL);
	close($DCS_FH[$server_no]);
	
	log_write("dcs_kill SERVER[$server_no] done($PID[$server_no]).");
	root_delete($server_no,$PID[$server_no]);
	undef($PID[$server_no]);
	return 1;
}

# ステータス書き出し
sub root_write{
	my $server_no = $_[0];
	my $proid = $_[1];
	my @tmpstr;
	open(DATA, "+< $ACT_ROOT_FILE") || return 0;
	flock(DATA, 2);
	while(<DATA>){
		push(@tmpstr,$_);
	}
	truncate(DATA, 0);
	seek(DATA, 0, 0);
	for(my $i=0; $i<@DCS_INI_DIR;$i++){
#		$tmpstr[$i] =~ s/\r//;
#		$tmpstr[$i] =~ s/\n//;
		if($server_no == $i){
			print DATA "$proid\n";
		}else{
			print DATA $tmpstr[$i];
		}
	}
	close(DATA);
}
# ステータス削除
sub root_delete{
	my $server_no = $_[0];
	my $proid = $_[1];
	my @tmpstr;
	open(DATA, "+< $ACT_ROOT_FILE") || return 0;
	flock(DATA, 2);
	while(<DATA>){
		push(@tmpstr,$_);
	}
	truncate(DATA, 0);
	seek(DATA, 0, 0);
	for(my $i=0; $i<@DCS_INI_DIR;$i++){
#		$tmpstr[$i] =~ s/\r//;
#		$tmpstr[$i] =~ s/\n//;
		if($server_no == $i){
			print DATA "\n";
		}else{
			print DATA $tmpstr[$i];
		}
	}
	close(DATA);
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



